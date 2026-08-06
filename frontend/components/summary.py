import streamlit as st


def render_summary():

    st.subheader("📄 Clinical Summary")

    st.text_area(
        "Summary",
        "Waiting for analysis...",
        height=120
    )