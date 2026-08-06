import streamlit as st


def render_progress():

    st.subheader("⚙ Pipeline Status")

    st.info("⏳ Speech Recognition")

    st.info("⏳ Translation")

    st.info("⏳ Summarization")

    st.info("⏳ Medical Entity Extraction")

    st.info("⏳ Risk Assessment")