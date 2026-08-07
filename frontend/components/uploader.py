import streamlit as st


def render_uploader():
    """
    Upload audio component.
    """

    st.subheader("🎙 Upload Patient Audio")

    uploaded_file = st.file_uploader(
        "Choose a WAV, MP3 or M4A file",
        type=["wav", "mp3", "m4a"]
    )

    analyze = st.button("Analyze")

    return uploaded_file, analyze