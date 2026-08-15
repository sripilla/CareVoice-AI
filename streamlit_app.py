"""
Main Streamlit application for CareVoice AI.
"""

import streamlit as st

from frontend.constants import (
    APP_TITLE,
    APP_SUBTITLE,
    PAGE_NEW_CONSULTATION,
    PAGE_REPORT_HISTORY,
    PAGE_ABOUT,
)

from frontend.components.sidebar import render_sidebar
from frontend.components.patient_form import render_patient_form
from frontend.components.uploader import render_uploader
from frontend.components.progress import render_progress
from frontend.components.transcript import render_transcript
from frontend.components.translation import render_translation
from frontend.components.summary import render_summary
from frontend.components.entities import render_entities
from frontend.components.risk import render_risk
from frontend.components.report import render_report
from frontend.components.prescription import render_prescription
from frontend.components.history import render_history

from frontend.services.file_service import save_uploaded_file
from frontend.services.analysis_service import run_analysis


# ------------------------------------------------------------------
# Initialize Session State
# ------------------------------------------------------------------

if "report" not in st.session_state:
    st.session_state.report = {
        "consultation_id": None,
        "original_transcript": "",
        "detected_language": "",
        "english_transcript": "",
        "summary": "",
        "patient": {
            "patient_id": "",
            "patient_name": "",
            "age": None,
            "blood_pressure": None,
            "weight": None,
            "blood_sugar": None,
            "symptoms": [],
            "conditions": [],
            "medications": [],
            "duration": "",
        },
        "risk": {
            "risk_score": None,
            "risk_level": "",
        },
        "clinical_report": "",
    }


if "patient_details" not in st.session_state:
    st.session_state.patient_details = None


if "consultation_started" not in st.session_state:
    st.session_state.consultation_started = False


def main():
    """
    Main Streamlit application.
    """

    st.set_page_config(
        page_title="CareVoice AI",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ------------------------------------------------------------
    # Sidebar
    # ------------------------------------------------------------

    page, show_processing_details = render_sidebar()

    # ------------------------------------------------------------
    # New Consultation
    # ------------------------------------------------------------

    if page == PAGE_NEW_CONSULTATION:

        st.title(APP_TITLE)
        st.subheader(APP_SUBTITLE)

        st.divider()

        # ============================================================
        # Patient Details
        # ============================================================

        if not st.session_state.consultation_started:

            with st.container(border=True):

                patient_details, start_consultation = (
                    render_patient_form()
                )

            if patient_details is not None:

                st.session_state.patient_details = (
                    patient_details
                )

                st.session_state.consultation_started = True

                st.success(
                    "Consultation started successfully."
                )

                st.rerun()

        # ============================================================
        # Upload / Record Audio
        # ============================================================

        if st.session_state.consultation_started:

            patient = st.session_state.patient_details

            st.info(
                f"Consultation in progress for "
                f"**{patient['patient_name']}** "
                f"(Patient ID: **{patient['patient_id']}**)"
            )

            with st.container(border=True):

                uploaded_file, analyze = render_uploader()

            # ========================================================
            # Run Analysis
            # ========================================================

            if analyze:

                if uploaded_file is None:

                    st.warning(
                        "Please upload or record patient audio."
                    )

                else:

                    # Reset previous report before analysis.
                    st.session_state.report = {
                        "consultation_id": None,
                        "original_transcript": "",
                        "detected_language": "",
                        "english_transcript": "",
                        "summary": "",
                        "patient": {
                            "patient_id": "",
                            "patient_name": "",
                            "age": None,
                            "blood_pressure": None,
                            "weight": None,
                            "blood_sugar": None,
                            "symptoms": [],
                            "conditions": [],
                            "medications": [],
                            "duration": "",
                        },
                        "risk": {
                            "risk_score": None,
                            "risk_level": "",
                        },
                        "clinical_report": "",
                    }

                    try:

                        with st.spinner(
                            "Analyzing patient audio..."
                        ):

                            audio_path = save_uploaded_file(
                                uploaded_file
                            )

                            backend_report = run_analysis(
                                audio_path,
                                st.session_state.patient_details,
                            )

                            st.session_state.report = (
                                backend_report
                            )

                        st.success(
                            "Analysis completed successfully."
                        )

                        st.rerun()

                    except Exception as e:

                        st.exception(e)

        # ============================================================
        # Processing Details
        # ============================================================

        if (
            st.session_state.consultation_started
            and show_processing_details
        ):

            with st.expander(
                "⚙️ Processing Details",
                expanded=False,
            ):

                render_progress()

        # ============================================================
        # Analysis Results
        # ============================================================

        if st.session_state.report["clinical_report"]:

            # --------------------------------------------------------
            # Transcript Card
            # --------------------------------------------------------

            with st.container(border=True):

                render_transcript()

            # --------------------------------------------------------
            # Translation Card
            # --------------------------------------------------------

            with st.container(border=True):

                render_translation()

            # --------------------------------------------------------
            # Summary Card
            # --------------------------------------------------------

            with st.container(border=True):

                render_summary()

            # --------------------------------------------------------
            # Patient and Clinical Information Card
            # --------------------------------------------------------

            with st.container(border=True):

                render_entities()

            # --------------------------------------------------------
            # Risk Assessment Card
            # --------------------------------------------------------

            with st.container(border=True):

                render_risk()

            # --------------------------------------------------------
            # Clinical Report Card
            # --------------------------------------------------------

            with st.container(border=True):

                render_report()

            # --------------------------------------------------------
            # Doctor Prescription and Guidelines Card
            # --------------------------------------------------------

            consultation_id = st.session_state.report.get(
                "consultation_id"
            )

            if consultation_id is not None:

                with st.container(border=True):

                    render_prescription(
                        consultation_id=consultation_id
                    )

            else:

                st.error(
                    "Consultation ID is not available. "
                    "Unable to save the prescription."
                )

    # ------------------------------------------------------------
    # Report History
    # ------------------------------------------------------------

    elif page == PAGE_REPORT_HISTORY:

        st.title("📋 Report History")

        st.caption(
            "Search consultations using the Patient ID."
        )

        with st.container(border=True):

            render_history()

    # ------------------------------------------------------------
    # About
    # ------------------------------------------------------------

    elif page == PAGE_ABOUT:

        st.title("ℹ️ About CareVoice AI")

        st.markdown(
            """
### 🏥 CareVoice AI

CareVoice AI is an AI-powered multilingual clinical speech analysis system
that converts patient speech into structured clinical reports.

### Features

- 🎙 Speech Recognition
- 🌍 Language Detection
- 🌐 Machine Translation
- 📄 AI Clinical Summary
- 🩺 Medical Entity Extraction
- ⚠️ Risk Assessment
- 📋 Clinical Report Generation
- 💊 Doctor Prescription Translation
- 📝 Multilingual Patient Guidelines

---

Developed as part of the **NLP Minor Specialisation**.
"""
        )


if __name__ == "__main__":
    main()