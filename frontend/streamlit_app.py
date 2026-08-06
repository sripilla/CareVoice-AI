import streamlit as st

st.set_page_config(
    page_title="CareVoice AI",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 CareVoice AI")
st.subheader("Multilingual Clinical Speech Analysis")

st.divider()

uploaded_file = st.file_uploader(
    "Upload Patient Audio",
    type=["wav", "mp3", "m4a"]
)

if st.button("Analyze"):
    if uploaded_file:
        st.success("Audio uploaded successfully!")
    else:
        st.warning("Please upload an audio file.")

st.divider()

st.header("Results")

st.info("No report generated yet.")