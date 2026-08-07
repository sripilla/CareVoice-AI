import streamlit as st


def render_report():
    """
    Display the generated clinical report.
    """

    st.subheader("📋 Clinical Report")

    report = st.session_state.get("report", {})

    clinical_report = report.get("clinical_report", "")

    if clinical_report:
        st.text_area(
            "Clinical Report",
            value=clinical_report,
            height=450,
            disabled=True,
        )
    else:
        st.info("No report generated.")