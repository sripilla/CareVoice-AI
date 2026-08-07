"""
File handling utilities for the Streamlit frontend.
"""

import tempfile
from pathlib import Path


def save_uploaded_file(uploaded_file) -> str:
    """
    Save an uploaded Streamlit file to a temporary location.

    Parameters
    ----------
    uploaded_file : UploadedFile

    Returns
    -------
    str
        Path to the temporary file.
    """

    suffix = Path(uploaded_file.name).suffix

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temp_file:

        temp_file.write(uploaded_file.getbuffer())

        return temp_file.name