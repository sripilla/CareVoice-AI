from careinsight.engine import CareVoiceEngine
from config import DEFAULT_AUDIO_FILE
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """
    Run the CareVoice AI pipeline using
    the default sample audio file.
    """

    logger.info("Starting CareVoice AI...")

    engine = CareVoiceEngine()

    patient_details = {
        "patient_id": "P001",
        "patient_name": "Sample Patient",
        "age": 45,
    }


    report = engine.process_audio(
        str(DEFAULT_AUDIO_FILE),
        patient_details,
    )

    logger.info("Clinical report generated successfully.")

    print(report["clinical_report"])


if __name__ == "__main__":
    main()