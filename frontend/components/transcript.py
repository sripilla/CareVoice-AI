import streamlit as st


def render_transcript():

    st.subheader("📝 Original Transcript")

    st.text_area(
        "Transcript",
        "Waiting for analysis...",
        height=150
    )