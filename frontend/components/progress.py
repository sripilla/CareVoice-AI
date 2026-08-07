import streamlit as st


PIPELINE_STEPS = [
    "Speech Recognition",
    "Translation",
    "Summarization",
    "Medical Entity Extraction",
    "Risk Assessment",
    "Clinical Report Generation",
]


def render_progress():
    """
    Display pipeline processing status.
    """

    report = st.session_state.get("report", {})

    analysis_complete = bool(report.get("clinical_report"))

    st.subheader("⚙️ Pipeline Status")

    if analysis_complete:

        for step in PIPELINE_STEPS:
            st.success(f"✔ {step}")

        st.success("🎉 Analysis completed successfully!")

    else:

        st.info("Upload an audio file and click **Analyze** to begin.")