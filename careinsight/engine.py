from careinsight.extractor import MedicalExtractor
from careinsight.report_generator import ReportGenerator
from careinsight.risk_assessor import RiskAssessor
from careinsight.summarizer import MedicalSummarizer
from config import WHISPER_MODEL
from database.database import DatabaseManager
from speech.transcriber import SpeechTranscriber
from translation.translator import Translator
from utils.logger import get_logger

logger = get_logger(__name__)


class CareVoiceEngine:
    """
    Main orchestration engine for the CareVoice AI pipeline.
    """

    def __init__(self):
        """
        Initialize all AI pipeline components.
        """

        logger.info("Initializing CareVoice AI...")

        self.transcriber = SpeechTranscriber(
            model_name=WHISPER_MODEL,
        )

        self.translator = Translator()

        self.summarizer = MedicalSummarizer()

        self.extractor = MedicalExtractor()

        self.risk_assessor = RiskAssessor()

        self.report_generator = ReportGenerator()

        self.database = DatabaseManager()

        logger.info("CareVoice AI initialized successfully.")

    # ======================================================
    # Public API
    # ======================================================

    def process_audio(
        self,
        audio_path: str,
    ) -> dict:
        """
        Execute the complete CareVoice AI pipeline.
        """

        logger.info("Processing audio: %s", audio_path)

        transcript, language = self._transcribe_audio(
            audio_path
        )

        english_text = self._translate_text(
            transcript,
            language,
        )

        summary = self._summarize_text(
            english_text
        )

        patient = self._extract_patient(
            english_text
        )

        risk = self._assess_risk(
            patient
        )

        clinical_report = self._generate_report(
            summary,
            patient,
            risk,
        )

        report = self._build_report(
            transcript=transcript,
            language=language,
            english_text=english_text,
            summary=summary,
            patient=patient,
            risk=risk,
            clinical_report=clinical_report,
        )

        self._save_report(report)

        logger.info("Audio processing completed successfully.")

        return report

    # ======================================================
    # Pipeline Steps
    # ======================================================

    def _transcribe_audio(
        self,
        audio_path: str,
    ) -> tuple[str, str]:
        """
        Perform speech recognition.
        """

        logger.info("Step 1: Speech Recognition")

        speech = self.transcriber.transcribe(
            audio_path
        )

        return (
            speech["transcript"],
            speech["language"],
        )

    def _translate_text(
        self,
        transcript: str,
        language: str,
    ) -> str:
        """
        Translate transcript into English.
        """

        logger.info("Step 2: Translation")

        return self.translator.translate(
            transcript,
            language,
        )

    def _summarize_text(
        self,
        english_text: str,
    ) -> str:
        """
        Generate a clinical summary.
        """

        logger.info("Step 3: Summarization")

        return self.summarizer.summarize_text(
            english_text
        )

    def _extract_patient(
        self,
        english_text: str,
    ) -> dict:
        """
        Extract structured medical information.
        """

        logger.info("Step 4: Medical Entity Extraction")

        return self.extractor.extract(
            english_text
        )

    def _assess_risk(
        self,
        patient: dict,
    ) -> dict:
        """
        Assess patient risk.
        """

        logger.info("Step 5: Risk Assessment")

        return self.risk_assessor.assess(
            patient
        )

    def _generate_report(
        self,
        summary: str,
        patient: dict,
        risk: dict,
    ) -> str:
        """
        Generate the clinical report.
        """

        logger.info("Step 6: Clinical Report Generation")

        return self.report_generator.generate(
            summary=summary,
            patient=patient,
            risk=risk,
        )

    # ======================================================
    # Report Management
    # ======================================================

    def _build_report(
        self,
        transcript: str,
        language: str,
        english_text: str,
        summary: str,
        patient: dict,
        risk: dict,
        clinical_report: str,
    ) -> dict:
        """
        Build the final response object.
        """

        return {
            "original_transcript": transcript,
            "detected_language": language,
            "english_transcript": english_text,
            "summary": summary,
            "patient": patient,
            "risk": risk,
            "clinical_report": clinical_report,
        }

    def _save_report(
        self,
        report: dict,
    ):
        """
        Persist the report to the database.
        """

        logger.info("Saving report to database.")

        self.database.save_report(report)