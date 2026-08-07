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
from frontend.components.uploader import render_uploader
from frontend.components.progress import render_progress
from frontend.components.transcript import render_transcript
from frontend.components.translation import render_translation
from frontend.components.summary import render_summary
from frontend.components.entities import render_entities
from frontend.components.risk import render_risk
from frontend.components.report import render_report

from frontend.services.file_service import save_uploaded_file
from frontend.services.analysis_service import run_analysis


# ------------------------------------------------------------------
# Initialize Session State
# ------------------------------------------------------------------

if "report" not in st.session_state:
    st.session_state.report = {
        "original_transcript": "",
        "detected_language": "",
        "english_transcript": "",
        "summary": "",
        "patient": {
            "patient_name": "",
            "age": None,
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

        uploaded_file, analyze = render_uploader()

        # --------------------------------------------------------
        # Run Analysis
        # --------------------------------------------------------
        if analyze:

            if uploaded_file is None:

                st.warning("Please upload an audio file.")

            else:

                # Reset report
                st.session_state.report = {
                    "original_transcript": "",
                    "detected_language": "",
                    "english_transcript": "",
                    "summary": "",
                    "patient": {
                        "patient_name": "",
                        "age": None,
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

                    with st.spinner("Analyzing patient audio..."):

                        audio_path = save_uploaded_file(uploaded_file)

                        backend_report = run_analysis(audio_path)

                        # Save backend response
                        st.session_state.report = backend_report

                    st.success("Analysis completed successfully.")

                    # Force Streamlit to rerun using the updated session state
                    st.rerun()

                except Exception as e:
                    st.exception(e)

        # --------------------------------------------------------
        # Processing Details
        # --------------------------------------------------------
        if show_processing_details:
            with st.expander("⚙️ Processing Details", expanded=False):
                render_progress()

        st.divider()

        render_transcript()

        st.divider()

        render_translation()

        st.divider()

        render_summary()

        st.divider()

        left_col, right_col = st.columns([2, 1])

        with left_col:
            render_entities()

        with right_col:
            render_risk()

        st.divider()

        render_report()

    # ------------------------------------------------------------
    # Report History
    # ------------------------------------------------------------
    elif page == PAGE_REPORT_HISTORY:

        st.title("📋 Report History")

        st.info(
            "Previously generated clinical reports will appear here."
        )

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

---

Developed as part of the NLP Minor Specialisation.
"""
        )


if __name__ == "__main__":
    main()