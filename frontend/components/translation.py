import streamlit as st

from frontend.constants import (
    TRANSLATION_TITLE,
    WAITING_MESSAGE,
)


def render_translation():
    """
    Display the translated English text.
    """

    st.subheader(TRANSLATION_TITLE)

    report = st.session_state.get("report", {})

    translation = report.get("english_transcript", "")

    st.text_area(
        "English Translation",
        value=translation if translation else WAITING_MESSAGE,
        height=150,
        disabled=True,
    )