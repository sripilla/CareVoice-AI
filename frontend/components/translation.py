import streamlit as st

from constants import (
    TRANSLATION_TITLE,
    WAITING_MESSAGE,
)


def render_translation():
    """
    Display the translated English text.
    """

    st.subheader(TRANSLATION_TITLE)

    st.text_area(
        "English Translation",
        WAITING_MESSAGE,
        height=150,
    )