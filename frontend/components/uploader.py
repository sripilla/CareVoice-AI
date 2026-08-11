import streamlit as st


def render_uploader():
    """
    Render audio upload and microphone recording components.

    Returns
    -------
    tuple
        selected_audio : UploadedFile or None
        analyze : bool
    """

    st.subheader("🎙 Patient Audio")

    # ------------------------------------------------------------
    # Input method
    # ------------------------------------------------------------

    input_method = st.radio(
        "Choose audio input method",
        ["Upload Audio", "Record Audio"],
        horizontal=True,
    )

    selected_audio = None

    # ------------------------------------------------------------
    # Upload existing audio
    # ------------------------------------------------------------

    if input_method == "Upload Audio":

        selected_audio = st.file_uploader(
            "Choose a WAV, MP3 or M4A file",
            type=["wav", "mp3", "m4a"],
        )

    # ------------------------------------------------------------
    # Record audio from microphone
    # ------------------------------------------------------------

    else:

        selected_audio = st.audio_input(
            "Record patient audio",
            sample_rate=16000,
            help="Record the patient's consultation audio using your microphone.",
        )

    # ------------------------------------------------------------
    # Preview selected/recorded audio
    # ------------------------------------------------------------

    if selected_audio is not None:
        st.audio(selected_audio)

    # ------------------------------------------------------------
    # Analyze button
    # ------------------------------------------------------------

    analyze = st.button(
        "Analyze",
        type="primary",
    )

    return selected_audio, analyze