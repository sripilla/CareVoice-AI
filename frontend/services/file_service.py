"""
File handling utilities for the Streamlit frontend.
"""

from pathlib import Path


RAW_AUDIO_DIR = Path("data/raw_audio")


def save_uploaded_file(uploaded_file) -> str:
    """
    Save uploaded or recorded audio to the raw audio directory.

    Parameters
    ----------
    uploaded_file : UploadedFile
        Audio file from Streamlit upload or microphone recording.

    Returns
    -------
    str
        Path to the saved audio file.

    Raises
    ------
    ValueError
        If no audio file is provided or the file is empty.
    """

    if uploaded_file is None:
        raise ValueError("No audio file provided.")

    if uploaded_file.size == 0:
        raise ValueError("Audio file is empty.")

    # Create the raw audio directory if it does not exist.
    RAW_AUDIO_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ------------------------------------------------------------
    # Generate the next audio ID
    # ------------------------------------------------------------

    existing_files = RAW_AUDIO_DIR.glob("AU*.wav")

    numbers = []

    for file in existing_files:
        try:
            number = int(file.stem[2:])
            numbers.append(number)
        except ValueError:
            continue

    next_number = max(numbers, default=0) + 1

    # ------------------------------------------------------------
    # Create output path
    # ------------------------------------------------------------

    output_path = RAW_AUDIO_DIR / f"AU{next_number:03d}.wav"

    # ------------------------------------------------------------
    # Save audio
    # ------------------------------------------------------------

    with open(output_path, "wb") as audio_file:
        audio_file.write(uploaded_file.getbuffer())

    return str(output_path)