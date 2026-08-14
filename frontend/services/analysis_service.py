"""
Service layer between the Streamlit UI and CareVoiceEngine.
"""

from careinsight.engine import CareVoiceEngine


# Initialize the engine once when Streamlit starts.
engine = CareVoiceEngine()


def run_analysis(
    audio_path: str,
    patient_details: dict,
) -> dict:
    """
    Run the CareVoice AI pipeline on consultation audio.

    Parameters
    ----------
    audio_path : str
        Path to the consultation audio.

    patient_details : dict
        Doctor-provided patient identity information.

    Returns
    -------
    dict
        Clinical consultation report.
    """

    return engine.process_audio(
        audio_path,
        patient_details,
    )