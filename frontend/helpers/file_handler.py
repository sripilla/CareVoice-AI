"""
File handling utilities for the Streamlit frontend.
"""

from pathlib import Path
import tempfile

from streamlit.runtime.uploaded_file_manager import UploadedFile


def save_uploaded_file(uploaded_file: UploadedFile) -> str:
    """
    Save an uploaded Streamlit file to a temporary location.

    Parameters
    ----------
    uploaded_file : UploadedFile
        Audio file uploaded through the Streamlit UI.

    Returns
    -------
    str
        Absolute path to the temporary audio file.

    Raises
    ------
    ValueError
        If the uploaded file is empty.
    """

    if uploaded_file.size == 0:
        raise ValueError("Uploaded file is empty.")

    suffix = Path(uploaded_file.name).suffix

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temp_file:

        temp_file.write(uploaded_file.getbuffer())

        return temp_file.name