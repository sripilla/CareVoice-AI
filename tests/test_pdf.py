"""
PDF rendering.

The assertions are structural -- valid document, plausible size,
no crash on sparse data -- since layout itself is not meaningfully
testable here.
"""

import utils.pdf as pdf_module
from utils.pdf import build_report_pdf


def test_produces_a_valid_pdf(report):

    result = build_report_pdf(report)

    assert result.startswith(b"%PDF-")
    assert result.rstrip().endswith(b"%%EOF")
    assert len(result) > 2000


def test_accepts_a_flat_database_row():
    """
    Stored reports come back flat, not with nested patient/risk
    keys, and the same builder has to handle both.
    """

    row = {
        "id": 7,
        "timestamp": "01-01-2026 10:00",
        "patient_name": "Ravi",
        "age": 45,
        "symptoms": "fever, cough",
        "conditions": "Diabetes",
        "medications": "",
        "duration": "2 days",
        "summary": "Patient reports fever.",
        "risk_score": 2,
        "risk_level": "Medium",
        "clinical_report": "report text",
        "detected_language": "hi",
        "original_transcript": "मुझे बुखार है।",
        "english_transcript": "I have a fever.",
    }

    result = build_report_pdf(row)

    assert result.startswith(b"%PDF-")


def test_handles_an_empty_report(empty_patient):

    report = {
        "patient": empty_patient,
        "risk": {"risk_score": 0, "risk_level": "Low"},
        "summary": "",
        "english_transcript": "",
        "original_transcript": "",
        "clinical_report": "",
        "warnings": [],
    }

    result = build_report_pdf(report)

    assert result.startswith(b"%PDF-")


def test_renders_warnings(report):

    report["warnings"] = ["Unsupported source language."]

    assert build_report_pdf(report).startswith(b"%PDF-")


def test_escapes_markup_in_transcripts(report):
    """
    ReportLab paragraphs parse a small HTML subset, so an unescaped
    angle bracket in a transcript would abort the build.
    """

    report["english_transcript"] = (
        "Patient said <b>unclosed and & ampersand"
    )

    assert build_report_pdf(report).startswith(b"%PDF-")


def test_unknown_risk_level_does_not_crash(report):

    report["risk"] = {"risk_score": 3, "risk_level": "Unknown"}

    assert build_report_pdf(report).startswith(b"%PDF-")


def test_falls_back_when_no_indic_font_is_available(
    report,
    monkeypatch,
):
    """
    On a host without a suitable font the PDF must still build,
    with a note in place of the original-script transcript.
    """

    monkeypatch.setattr(pdf_module, "_INDIC_FONT", None)
    monkeypatch.setattr(
        pdf_module,
        "INDIC_FONT_CANDIDATES",
        [],
    )

    result = build_report_pdf(report)

    assert result.startswith(b"%PDF-")


def test_as_list_normalizes_both_shapes():

    assert pdf_module._as_list(["fever", "cough"]) == [
        "fever",
        "cough",
    ]
    assert pdf_module._as_list("fever, cough") == [
        "fever",
        "cough",
    ]
    assert pdf_module._as_list("") == []
    assert pdf_module._as_list(None) == []


def test_escape_renders_missing_values():

    assert pdf_module._escape(None) == "Not recorded"
    assert pdf_module._escape("  ") == "Not recorded"
    assert pdf_module._escape("<x>") == "&lt;x&gt;"
