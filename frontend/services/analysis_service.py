"""
Service layer between the Streamlit UI and CareVoiceEngine.
"""

from careinsight.engine import CareVoiceEngine

# Initialize the engine once when Streamlit starts.
engine = CareVoiceEngine()


def run_analysis(audio_path: str) -> dict:
    """
    Run the CareVoice AI pipeline on an uploaded audio file.

    Parameters
    ----------
    audio_path : str

    Returns
    -------
    dict
        Clinical analysis report.
    """

    return engine.process_audio(audio_path)