"""
PDF generation for CareVoice AI clinical reports.

Built on ReportLab, which is pure Python and therefore installs
without system dependencies on Windows, macOS and Linux alike.
"""

from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from config import (
    INDIC_FONT_CANDIDATES,
    INDIC_FONT_NAME,
    MEDICAL_DISCLAIMER,
    REPORT_DATE_FORMAT,
    REPORT_TITLE,
    RISK_COLORS,
)
from utils.logger import get_logger

logger = get_logger(__name__)

# Resolved once per process: None until _indic_font() runs, then
# either the registered font name or False if none was available.
_INDIC_FONT: "str | bool | None" = None


def _indic_font():
    """
    Register and return an Indic-capable font name, or None if
    the host has no suitable font installed.

    ReportLab's built-in fonts are Latin-1 only, so Telugu,
    Devanagari and Tamil need a TrueType font registered first.

    Caveat: ReportLab does not perform OpenType complex-script
    shaping, so conjuncts in these scripts render imperfectly.
    The English report -- the part a clinician acts on -- is
    unaffected, and the dashboard renders the original script
    correctly because the browser shapes it.
    """

    global _INDIC_FONT

    if _INDIC_FONT is not None:
        return _INDIC_FONT or None

    for candidate in INDIC_FONT_CANDIDATES:

        if not candidate.exists():
            continue

        try:

            # .ttc files are font collections; index 0 is the
            # regular face.
            if candidate.suffix.lower() == ".ttc":
                font = TTFont(
                    INDIC_FONT_NAME,
                    str(candidate),
                    subfontIndex=0,
                )
            else:
                font = TTFont(
                    INDIC_FONT_NAME,
                    str(candidate),
                )

            pdfmetrics.registerFont(font)

            logger.info(
                "Registered Indic PDF font: %s",
                candidate,
            )

            _INDIC_FONT = INDIC_FONT_NAME

            return INDIC_FONT_NAME

        except Exception:

            logger.warning(
                "Could not register font %s; trying the next "
                "candidate.",
                candidate,
                exc_info=True,
            )

    logger.warning(
        "No Indic-capable font found. The original-script "
        "transcript will be omitted from the PDF."
    )

    _INDIC_FONT = False

    return None


# ==========================================================
# Styles
# ==========================================================

def _styles() -> dict:
    """
    Build the paragraph styles used throughout the report.
    """

    base = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "CareVoiceTitle",
            parent=base["Title"],
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0d3b66"),
            spaceAfter=2,
        ),
        "subtitle": ParagraphStyle(
            "CareVoiceSubtitle",
            parent=base["Normal"],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#57606a"),
        ),
        "heading": ParagraphStyle(
            "CareVoiceHeading",
            parent=base["Heading2"],
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#0d3b66"),
            spaceBefore=10,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "CareVoiceBody",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
        ),
        "mono": ParagraphStyle(
            "CareVoiceQuote",
            parent=base["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#24292f"),
        ),
        "disclaimer": ParagraphStyle(
            "CareVoiceDisclaimer",
            parent=base["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#57606a"),
        ),
        "warning": ParagraphStyle(
            "CareVoiceWarning",
            parent=base["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#bf8700"),
        ),
    }


def _escape(value) -> str:
    """
    Render a value as PDF-safe paragraph markup.

    ReportLab paragraphs accept a small HTML subset, so raw
    transcript text must have its markup characters escaped.
    """

    if value is None:
        return "Not recorded"

    text = str(value).strip()

    if not text:
        return "Not recorded"

    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _as_list(value) -> list:
    """
    Normalize a field that may arrive as a list (from the live
    pipeline) or a comma-joined string (from the database).
    """

    if not value:
        return []

    if isinstance(value, str):
        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

    return [
        str(item).strip()
        for item in value
        if str(item).strip()
    ]


# ==========================================================
# Sections
# ==========================================================

def _header(styles: dict, report: dict) -> list:
    """
    Title block.
    """

    generated_on = datetime.now().strftime(
        REPORT_DATE_FORMAT
    )

    report_id = report.get("report_id") or report.get("id")

    reference = (
        f"Report #{report_id}"
        if report_id is not None
        else "Unsaved report"
    )

    return [
        Paragraph(REPORT_TITLE, styles["title"]),
        Paragraph(
            f"{reference} &nbsp;|&nbsp; Generated on "
            f"{generated_on}",
            styles["subtitle"],
        ),
        Spacer(1, 6),
        HRFlowable(
            width="100%",
            color=colors.HexColor("#0d3b66"),
            thickness=1.2,
        ),
        Spacer(1, 8),
    ]


def _patient_table(report: dict) -> Table:
    """
    Patient particulars and the detected language.
    """

    patient = report.get("patient") or report

    language = _escape(report.get("detected_language"))

    probability = report.get("language_probability")

    if isinstance(probability, (int, float)):
        language = f"{language} ({probability:.0%} confidence)"

    rows = [
        ["Patient Name", _escape(patient.get("patient_name"))],
        ["Age", _escape(patient.get("age"))],
        ["Symptom Duration", _escape(patient.get("duration"))],
        ["Spoken Language", language],
    ]

    table = Table(rows, colWidths=[45 * mm, 120 * mm])

    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, -2),
                    0.4,
                    colors.HexColor("#d0d7de"),
                ),
            ]
        )
    )

    return table


def _risk_badge(report: dict) -> Table:
    """
    Colour-coded risk banner.
    """

    risk = report.get("risk") or report

    level = risk.get("risk_level") or "Unknown"
    score = risk.get("risk_score")

    background = colors.HexColor(
        RISK_COLORS.get(level, "#57606a")
    )

    label = f"{level.upper()} RISK"

    if score is not None:
        label = f"{label} - Risk Score {score}"

    cell = Paragraph(
        f'<font color="white"><b>{_escape(label)}</b></font>',
        ParagraphStyle(
            "CareVoiceRiskBadge",
            fontSize=12,
            leading=16,
            alignment=TA_CENTER,
        ),
    )

    table = Table([[cell]], colWidths=[165 * mm])

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    return table


def _findings_table(styles: dict, report: dict) -> Table:
    """
    Symptoms, conditions and medications side by side.
    """

    patient = report.get("patient") or report

    def column(title: str, items: list):

        body = (
            "<br/>".join(
                f"&bull; {_escape(item)}" for item in items
            )
            if items
            else "&bull; None recorded"
        )

        return (
            Paragraph(f"<b>{title}</b>", styles["body"]),
            Paragraph(body, styles["body"]),
        )

    symptoms = column(
        "Symptoms",
        _as_list(patient.get("symptoms")),
    )

    conditions = column(
        "Conditions",
        _as_list(patient.get("conditions")),
    )

    medications = column(
        "Medications",
        _as_list(patient.get("medications")),
    )

    rows = [
        [symptoms[0], conditions[0], medications[0]],
        [symptoms[1], conditions[1], medications[1]],
    ]

    table = Table(rows, colWidths=[55 * mm] * 3)

    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#f0f4f8"),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#d0d7de"),
                ),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    return table


def _transcript_section(styles: dict, report: dict) -> list:
    """
    English transcript, then the original-script transcript on a
    fresh page when a suitable font is available.
    """

    flowables = []

    english = report.get("english_transcript")

    if english:
        flowables.extend(
            [
                Paragraph(
                    "English Transcript",
                    styles["heading"],
                ),
                Paragraph(_escape(english), styles["mono"]),
            ]
        )

    original = report.get("original_transcript")

    if not original:
        return flowables

    font = _indic_font()

    flowables.append(PageBreak())

    flowables.append(
        Paragraph(
            "Original-Language Transcript",
            styles["heading"],
        )
    )

    if font is None:

        flowables.append(
            Paragraph(
                "The original-language transcript is stored with "
                "this report but cannot be rendered here: no font "
                "covering the source script is installed on the "
                "machine that produced this PDF. View it in the "
                "CareVoice dashboard.",
                styles["disclaimer"],
            )
        )

        return flowables

    flowables.append(
        Paragraph(
            "Rendered without complex-script shaping; consult the "
            "dashboard for a faithful rendering.",
            styles["disclaimer"],
        )
    )

    flowables.append(Spacer(1, 4))

    flowables.append(
        Paragraph(
            _escape(original),
            ParagraphStyle(
                "CareVoiceIndicBody",
                parent=styles["mono"],
                fontName=font,
                fontSize=11,
                leading=18,
            ),
        )
    )

    return flowables


# ==========================================================
# Public API
# ==========================================================

def build_report_pdf(report: dict) -> bytes:
    """
    Render a clinical report as a PDF.

    Accepts either the live pipeline's report dict (with nested
    ``patient`` and ``risk`` keys) or a flat database row, so the
    same builder serves ``/analyze`` results and stored reports.

    Parameters
    ----------
    report : dict
        Report data.

    Returns
    -------
    bytes
        The PDF document.
    """

    report = dict(report)

    logger.info("Building PDF report.")

    styles = _styles()

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=22 * mm,
        rightMargin=22 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=REPORT_TITLE,
        author="CareVoice AI",
    )

    story = []

    story.extend(_header(styles, report))

    story.append(_patient_table(report))
    story.append(Spacer(1, 10))

    story.append(_risk_badge(report))
    story.append(Spacer(1, 12))

    warnings = report.get("warnings") or []

    if warnings:

        story.append(
            Paragraph(
                "Processing Warnings",
                styles["heading"],
            )
        )

        for warning in warnings:
            story.append(
                Paragraph(
                    f"&bull; {_escape(warning)}",
                    styles["warning"],
                )
            )

        story.append(Spacer(1, 6))

    story.append(
        Paragraph("Clinical Findings", styles["heading"])
    )

    story.append(_findings_table(styles, report))

    summary = report.get("summary")

    if summary:
        story.append(
            KeepTogether(
                [
                    Paragraph(
                        "Consultation Summary",
                        styles["heading"],
                    ),
                    Paragraph(_escape(summary), styles["body"]),
                ]
            )
        )

    story.extend(_transcript_section(styles, report))

    story.append(Spacer(1, 14))

    story.append(
        HRFlowable(
            width="100%",
            color=colors.HexColor("#d0d7de"),
            thickness=0.6,
        )
    )

    story.append(Spacer(1, 5))

    story.append(
        Paragraph(MEDICAL_DISCLAIMER, styles["disclaimer"])
    )

    document.build(story)

    pdf_bytes = buffer.getvalue()

    buffer.close()

    logger.info(
        "PDF report built (%d bytes).",
        len(pdf_bytes),
    )

    return pdf_bytes
