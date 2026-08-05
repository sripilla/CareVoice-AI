"""
CareVoice AI clinician dashboard.

This app is a thin client over the FastAPI backend. It deliberately
never imports CareVoiceEngine: doing so would load Whisper, NLLB and
BART a second time, roughly doubling memory on a CPU-only machine.
Everything goes over HTTP to CAREVOICE_API_URL instead.
"""

import sys
from pathlib import Path

import httpx
import streamlit as st

# Allow `streamlit run frontend/streamlit_app.py` from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import (  # noqa: E402
    API_TIMEOUT_SECONDS,
    API_URL,
    MEDICAL_DISCLAIMER,
    RISK_COLORS,
    SUPPORTED_AUDIO_EXTENSIONS,
)

RISK_LEVELS = ["Low", "Medium", "High"]

UPLOAD_TYPES = sorted(
    extension.lstrip(".")
    for extension in SUPPORTED_AUDIO_EXTENSIONS
)


# ==========================================================
# API Client
# ==========================================================

def api_get(path: str, **params):
    """
    GET from the backend, returning (data, error_message).
    """

    try:

        response = httpx.get(
            f"{API_URL}{path}",
            params={
                key: value
                for key, value in params.items()
                if value
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.json(), None

    except httpx.HTTPStatusError as error:

        return None, _detail(error.response)

    except httpx.RequestError:

        return None, (
            "Cannot reach the CareVoice API at "
            f"{API_URL}. Start it with "
            "`uvicorn api.app:app`."
        )


def api_get_bytes(path: str):
    """
    GET binary content (the PDF), returning (bytes, error).
    """

    try:

        response = httpx.get(
            f"{API_URL}{path}",
            timeout=60,
        )

        response.raise_for_status()

        return response.content, None

    except httpx.HTTPStatusError as error:

        return None, _detail(error.response)

    except httpx.RequestError:

        return None, f"Cannot reach the CareVoice API at {API_URL}."


def api_delete(path: str):
    """
    DELETE a resource, returning (data, error).
    """

    try:

        response = httpx.delete(
            f"{API_URL}{path}",
            timeout=30,
        )

        response.raise_for_status()

        return response.json(), None

    except httpx.HTTPStatusError as error:

        return None, _detail(error.response)

    except httpx.RequestError:

        return None, f"Cannot reach the CareVoice API at {API_URL}."


def analyze(filename: str, data: bytes):
    """
    POST audio to /analyze, returning (report, error).

    The timeout is generous because a full CPU pipeline run takes
    tens of seconds.
    """

    try:

        response = httpx.post(
            f"{API_URL}/analyze",
            files={"audio": (filename, data, "application/octet-stream")},
            timeout=API_TIMEOUT_SECONDS,
        )

        response.raise_for_status()

        return response.json(), None

    except httpx.HTTPStatusError as error:

        return None, _detail(error.response)

    except httpx.ReadTimeout:

        return None, (
            "The backend did not respond within "
            f"{int(API_TIMEOUT_SECONDS)} seconds. Long recordings "
            "on CPU can exceed this -- raise CAREVOICE_API_TIMEOUT "
            "or use a shorter clip."
        )

    except httpx.RequestError:

        return None, (
            f"Cannot reach the CareVoice API at {API_URL}. "
            "Start it with `uvicorn api.app:app`."
        )


def _detail(response) -> str:
    """
    Pull FastAPI's error detail out of a failed response.
    """

    try:
        return str(response.json().get("detail", response.text))

    except Exception:
        return response.text or f"HTTP {response.status_code}"


# ==========================================================
# Shared UI pieces
# ==========================================================

def risk_badge(level: str, score=None):
    """
    Render the colour-coded risk banner.
    """

    color = RISK_COLORS.get(level, "#57606a")

    detail = (
        f"&nbsp;&middot;&nbsp; Risk Score {score}"
        if score is not None
        else ""
    )

    st.markdown(
        f"""
        <div style="
            background:{color};
            color:white;
            padding:0.75rem 1rem;
            border-radius:8px;
            font-size:1.05rem;
            font-weight:600;
            text-align:center;
            margin:0.5rem 0 1rem 0;">
            {level.upper()} RISK{detail}
        </div>
        """,
        unsafe_allow_html=True,
    )


def chips(items, empty="None recorded"):
    """
    Render a list of extracted entities as chips.
    """

    if isinstance(items, str):
        items = [
            item.strip()
            for item in items.split(",")
            if item.strip()
        ]

    if not items:
        st.caption(empty)
        return

    markup = "".join(
        f"""<span style="
            display:inline-block;
            background:#eef2f7;
            color:#24292f;
            border:1px solid #d0d7de;
            border-radius:999px;
            padding:0.15rem 0.7rem;
            margin:0 0.3rem 0.35rem 0;
            font-size:0.85rem;">{item}</span>"""
        for item in items
    )

    st.markdown(markup, unsafe_allow_html=True)


def pdf_download_button(report_id: int, key: str):
    """
    Fetch the PDF and offer it for download.
    """

    pdf_bytes, error = api_get_bytes(f"/reports/{report_id}/pdf")

    if error:
        st.warning(f"PDF unavailable: {error}")
        return

    st.download_button(
        "Download PDF report",
        data=pdf_bytes,
        file_name=f"carevoice_report_{report_id}.pdf",
        mime="application/pdf",
        key=key,
    )


def disclaimer():
    """
    Footer disclaimer shown on every page.
    """

    st.divider()

    st.caption(MEDICAL_DISCLAIMER)


# ==========================================================
# Page: New Consultation
# ==========================================================

def render_result(report: dict):
    """
    Render a completed /analyze response.
    """

    patient = report.get("patient", {})
    risk = report.get("risk", {})

    st.success("Consultation processed.")

    for warning in report.get("warnings", []):
        st.warning(warning)

    language = report.get("detected_language", "unknown")
    probability = report.get("language_probability")

    confidence = (
        f" ({probability:.0%} confidence)"
        if isinstance(probability, (int, float))
        else ""
    )

    st.caption(f"Detected language: **{language}**{confidence}")

    risk_badge(
        risk.get("risk_level", "Unknown"),
        risk.get("risk_score"),
    )

    left, middle, right = st.columns(3)

    left.metric("Patient", patient.get("patient_name") or "Unknown")
    middle.metric("Age", patient.get("age") or "Unknown")
    right.metric("Duration", patient.get("duration") or "Unknown")

    st.subheader("Clinical Findings")

    symptoms, conditions, medications = st.columns(3)

    with symptoms:
        st.markdown("**Symptoms**")
        chips(patient.get("symptoms"))

    with conditions:
        st.markdown("**Conditions**")
        chips(patient.get("conditions"))

    with medications:
        st.markdown("**Medications**")
        chips(patient.get("medications"))

    st.subheader("Consultation Summary")
    st.write(report.get("summary") or "No summary generated.")

    with st.expander("English transcript"):
        st.write(report.get("english_transcript") or "-")

    with st.expander("Original-language transcript"):
        st.write(report.get("original_transcript") or "-")

    with st.expander("Full clinical report (text)"):
        st.code(
            report.get("clinical_report") or "-",
            language=None,
        )

    st.subheader("Export")

    download_left, download_right = st.columns(2)

    with download_left:

        report_id = report.get("report_id")

        if report_id is not None:
            pdf_download_button(report_id, key="pdf_new")

    with download_right:

        st.download_button(
            "Download text report",
            data=report.get("clinical_report") or "",
            file_name=(
                f"carevoice_report_{report.get('report_id', 0)}.txt"
            ),
            mime="text/plain",
            key="txt_new",
        )


def page_new_consultation():
    """
    Record or upload a consultation and run the pipeline.
    """

    st.title("New Consultation")

    st.write(
        "Record the consultation live or upload an existing "
        "recording. Speech in any of the supported Indian "
        "languages is transcribed, translated, and turned into a "
        "structured clinical report."
    )

    record_tab, upload_tab = st.tabs(["Record", "Upload"])

    audio_name = None
    audio_bytes = None

    with record_tab:

        recording = st.audio_input(
            "Record consultation",
            key="recorder",
        )

        if recording is not None:
            audio_name = "consultation.wav"
            audio_bytes = recording.getvalue()

    with upload_tab:

        uploaded = st.file_uploader(
            "Upload an audio file",
            type=UPLOAD_TYPES,
            key="uploader",
        )

        if uploaded is not None:
            audio_name = uploaded.name
            audio_bytes = uploaded.getvalue()

    if audio_bytes:

        st.audio(audio_bytes)

        if st.button("Analyze consultation", type="primary"):

            with st.spinner(
                "Transcribing, translating and analyzing. "
                "This takes 30-90 seconds on CPU."
            ):
                report, error = analyze(audio_name, audio_bytes)

            if error:
                st.error(error)
                st.session_state.pop("report", None)
            else:
                st.session_state["report"] = report

    if st.session_state.get("report"):
        st.divider()
        render_result(st.session_state["report"])

    disclaimer()


# ==========================================================
# Page: Report History
# ==========================================================

def render_report_detail(report: dict):
    """
    Render a stored report fetched from /reports/{id}.
    """

    risk_badge(
        report.get("risk_level", "Unknown"),
        report.get("risk_score"),
    )

    left, middle, right = st.columns(3)

    left.metric("Patient", report.get("patient_name") or "Unknown")
    middle.metric("Age", report.get("age") or "Unknown")
    right.metric("Recorded", report.get("timestamp") or "-")

    language = report.get("detected_language")

    if language:
        st.caption(f"Detected language: **{language}**")

    symptoms, conditions, medications = st.columns(3)

    with symptoms:
        st.markdown("**Symptoms**")
        chips(report.get("symptoms"))

    with conditions:
        st.markdown("**Conditions**")
        chips(report.get("conditions"))

    with medications:
        st.markdown("**Medications**")
        chips(report.get("medications"))

    st.subheader("Consultation Summary")
    st.write(report.get("summary") or "-")

    if report.get("english_transcript"):
        with st.expander("English transcript"):
            st.write(report["english_transcript"])

    if report.get("original_transcript"):
        with st.expander("Original-language transcript"):
            st.write(report["original_transcript"])

    with st.expander("Full clinical report (text)"):
        st.code(report.get("clinical_report") or "-", language=None)


def page_history():
    """
    Browse, filter and manage stored reports.
    """

    st.title("Report History")

    filter_name, filter_risk = st.columns([2, 1])

    name = filter_name.text_input(
        "Search by patient name",
        placeholder="e.g. Lakshmi",
    )

    risk_level = filter_risk.selectbox(
        "Risk level",
        ["All"] + RISK_LEVELS,
    )

    reports, error = api_get(
        "/reports",
        name=name or None,
        risk_level=(
            None if risk_level == "All" else risk_level
        ),
    )

    if error:
        st.error(error)
        disclaimer()
        return

    if not reports:
        st.info(
            "No reports match. Process a consultation on the "
            "New Consultation page."
        )
        disclaimer()
        return

    st.caption(f"{len(reports)} report(s)")

    st.dataframe(
        reports,
        width="stretch",
        hide_index=True,
        column_config={
            "id": "ID",
            "timestamp": "Recorded",
            "patient_name": "Patient",
            "age": "Age",
            "risk_level": "Risk",
        },
    )

    st.divider()

    options = {
        (
            f"#{report['id']} - "
            f"{report.get('patient_name') or 'Unknown'} - "
            f"{report.get('risk_level')}"
        ): report["id"]
        for report in reports
    }

    selection = st.selectbox(
        "Open a report",
        list(options),
    )

    report_id = options[selection]

    detail, detail_error = api_get(f"/reports/{report_id}")

    if detail_error:
        st.error(detail_error)
        disclaimer()
        return

    render_report_detail(detail)

    st.subheader("Actions")

    download_column, delete_column = st.columns(2)

    with download_column:
        pdf_download_button(report_id, key=f"pdf_{report_id}")

    with delete_column:

        if st.button(
            "Delete this report",
            key=f"delete_{report_id}",
        ):

            _, delete_error = api_delete(f"/reports/{report_id}")

            if delete_error:
                st.error(delete_error)
            else:
                st.success(f"Report {report_id} deleted.")
                st.rerun()

    disclaimer()


# ==========================================================
# Page: About
# ==========================================================

def page_about():
    """
    Pipeline description, models and limitations.
    """

    st.title("About CareVoice AI")

    st.warning(MEDICAL_DISCLAIMER)

    st.subheader("Pipeline")

    st.code(
        """Patient audio (recorded or uploaded)
   |
   v  Faster-Whisper          speech recognition + language detection
   v  NLLB-200                translation into English
   v  BART-large-cnn          consultation summary
   v  spaCy + EntityRuler     clinical entity extraction
   v  Rule-based engine       risk scoring
   v  Report generator        structured clinical report
   |
   v  SQLite  ->  FastAPI  ->  this dashboard  ->  PDF""",
        language=None,
    )

    st.subheader("Models")

    st.table(
        [
            {
                "Stage": "Speech recognition",
                "Model": "Faster-Whisper (CTranslate2)",
            },
            {
                "Stage": "Language detection",
                "Model": "Whisper built-in",
            },
            {
                "Stage": "Translation",
                "Model": "facebook/nllb-200-distilled-600M",
            },
            {
                "Stage": "Summarization",
                "Model": "facebook/bart-large-cnn",
            },
            {
                "Stage": "Entity extraction",
                "Model": "spaCy en_core_web_sm + EntityRuler",
            },
            {
                "Stage": "Risk assessment",
                "Model": "Rule-based scoring",
            },
        ]
    )

    st.caption(
        "All models run locally. No audio, transcript or patient "
        "data leaves this machine."
    )

    st.subheader("Known limitations")

    st.markdown(
        """
- **Summarization** uses a news-domain model, not a clinical one.
  Summaries read fluently but are not clinically validated.
- **Entity extraction** relies on a hand-written pattern
  vocabulary and will miss terms outside it.
- **Risk scoring** is a simple additive rule set, not a
  validated clinical risk model.
- **Transcription accuracy** depends on the Whisper model size.
  Set `CAREVOICE_WHISPER_MODEL=large-v3` for the best results on
  Indian languages.
        """
    )


# ==========================================================
# Entry point
# ==========================================================

def main():
    """
    Configure the page and route to the selected view.
    """

    st.set_page_config(
        page_title="CareVoice AI",
        page_icon="+",
        layout="wide",
    )

    st.sidebar.title("CareVoice AI")

    st.sidebar.caption(
        "Multilingual clinical documentation assistant"
    )

    page = st.sidebar.radio(
        "Go to",
        [
            "New Consultation",
            "Report History",
            "About",
        ],
    )

    health, health_error = api_get("/")

    if health_error:
        st.sidebar.error("Backend offline")
    else:
        st.sidebar.success(
            f"Backend {health.get('status', 'Running').lower()}"
        )

    st.sidebar.caption(API_URL)

    if page == "New Consultation":
        page_new_consultation()

    elif page == "Report History":
        page_history()

    else:
        page_about()


main()
