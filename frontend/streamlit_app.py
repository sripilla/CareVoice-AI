"""
Main Streamlit application for CareVoice AI.
"""

import streamlit as st

from constants import (
    APP_TITLE,
    APP_SUBTITLE,
    PAGE_NEW_CONSULTATION,
    PAGE_REPORT_HISTORY,
    PAGE_ABOUT,
)

from components.sidebar import render_sidebar
from components.uploader import render_uploader
from components.progress import render_progress
from components.transcript import render_transcript
from components.translation import render_translation
from components.summary import render_summary
from components.entities import render_entities
from components.risk import render_risk
from components.report import render_report


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

    # -------------------------------------------------------------
    # Sidebar
    # -------------------------------------------------------------
    page, show_processing_details = render_sidebar()

    # -------------------------------------------------------------
    # New Consultation
    # -------------------------------------------------------------
    if page == PAGE_NEW_CONSULTATION:

        st.title(APP_TITLE)
        st.subheader(APP_SUBTITLE)

        st.divider()

        # ---------------------------------------------------------
        # Upload Audio
        # ---------------------------------------------------------
        uploaded_file, analyze = render_uploader()

        if analyze and uploaded_file:

         report = analyze_audio(audio_path)

        # ---------------------------------------------------------
        # Optional Processing Details
        # ---------------------------------------------------------
        if show_processing_details:
            with st.expander("⚙️ Processing Details", expanded=False):
                render_progress()

        st.divider()

        # ---------------------------------------------------------
        # Original Transcript
        # ---------------------------------------------------------
        render_transcript()

        st.divider()

        # ---------------------------------------------------------
        # English Translation
        # ---------------------------------------------------------
        render_translation()

        st.divider()

        # ---------------------------------------------------------
        # AI Clinical Summary
        # ---------------------------------------------------------
        render_summary()

        st.divider()

        # ---------------------------------------------------------
        # Medical Information + Risk Assessment
        # ---------------------------------------------------------
        left_col, right_col = st.columns([2, 1])

        with left_col:
            render_entities()

        with right_col:
            render_risk()

        st.divider()

        # ---------------------------------------------------------
        # Clinical Report
        # ---------------------------------------------------------
        render_report()

    # -------------------------------------------------------------
    # Report History
    # -------------------------------------------------------------
    elif page == PAGE_REPORT_HISTORY:

        st.title("📋 Report History")

        st.info(
            "Previously generated clinical reports will appear here."
        )

    # -------------------------------------------------------------
    # About
    # -------------------------------------------------------------
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

Developed as part of the **NLP Minor Specialisation**.
"""
        )


if __name__ == "__main__":
    main()