import streamlit as st


def render_summary():
    """
    Display the AI-generated clinical summary.
    """

    st.subheader("📄 Clinical Summary")

    report = st.session_state.get("report", {})

    summary = report.get("summary", "")

    st.text_area(
        "Summary",
        value=summary if summary else "Waiting for analysis...",
        height=120,
        disabled=True,
    )