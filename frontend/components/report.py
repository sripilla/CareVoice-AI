import streamlit as st
from datetime import datetime


def render_report():
    """
    Display and download the generated clinical report.
    """

    report = st.session_state.get("report", {})
    clinical_report = report.get("clinical_report", "")

    # ----------------------------------------------------------
    # Header
    # ----------------------------------------------------------

    header_col, button_col = st.columns([8, 1])

    with header_col:
        st.subheader("📋 Clinical Report")

    with button_col:
        if clinical_report:
            st.write("")  # Vertical alignment
            st.download_button(
                label="📥 Download",
                data=clinical_report,
                file_name=f"carevoice_report_{datetime.now():%Y%m%d_%H%M%S}.txt",
                mime="text/plain",
                use_container_width=True,
            )

    # ----------------------------------------------------------
    # No Report Yet
    # ----------------------------------------------------------

    if not clinical_report:
        st.info("No report generated.")
        return

    # ----------------------------------------------------------
    # Display Report
    # ----------------------------------------------------------

    st.text_area(
        "Clinical Report",
        value=clinical_report,
        height=450,
        disabled=True,
    )