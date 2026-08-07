import streamlit as st


def render_progress():
    """
    Display pipeline processing status.
    """

    report = st.session_state.get("report", {})

    # Analysis is considered complete once a clinical report exists
    analysis_complete = bool(report.get("clinical_report"))

    st.subheader("⚙️ Pipeline Status")

    if analysis_complete:
        st.success("✅ Speech Recognition")
        st.success("✅ Translation")
        st.success("✅ Summarization")
        st.success("✅ Medical Entity Extraction")
        st.success("✅ Risk Assessment")
        st.success("✅ Clinical Report Generation")
    else:
        st.info("⏳ Waiting for analysis...")