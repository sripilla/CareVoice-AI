import streamlit as st


def render_transcript():
    """
    Render original transcript.
    """

    st.subheader("📝 Original Transcript")

    report = st.session_state.get("report", {})

    transcript = report.get("original_transcript", "")

    st.text_area(
        "Transcript",
        value=transcript if transcript else "Waiting for analysis...",
        height=150,
        disabled=True,
    )