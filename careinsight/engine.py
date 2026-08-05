from careinsight.extractor import MedicalExtractor
from careinsight.pipelines import build_pipeline
from careinsight.report_generator import ReportGenerator
from careinsight.risk_assessor import RiskAssessor
from careinsight.summarizer import MedicalSummarizer
from database.database import DatabaseManager
from utils.logger import get_logger

logger = get_logger(__name__)


class CareVoiceEngine:
    """
    Main orchestration engine for the CareVoice AI pipeline.
    """

    def __init__(self, pipeline: str = None):
        """
        Initialize all AI pipeline components.

        Parameters
        ----------
        pipeline : str
            Speech-to-English backend ("cascade", "seamless" or
            "indic"). Defaults to CAREVOICE_PIPELINE.
        """

        logger.info("Initializing CareVoice AI...")

        # Everything from here down operates on English text, so the
        # speech front end is swappable without touching it.
        self.pipeline = build_pipeline(pipeline)

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

        speech = self.pipeline.to_english(audio_path).as_dict()

        transcript = speech["original_transcript"]
        language = speech["detected_language"]
        english_text = speech["english_transcript"]

        warnings = list(speech["warnings"])

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
            language_probability=speech["language_probability"],
            english_text=english_text,
            summary=summary,
            patient=patient,
            risk=risk,
            clinical_report=clinical_report,
            warnings=warnings,
        )

        report["report_id"] = self._save_report(report)

        logger.info("Audio processing completed successfully.")

        return report

    # ======================================================
    # Pipeline Steps
    # ======================================================

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
        language_probability: float,
        english_text: str,
        summary: str,
        patient: dict,
        risk: dict,
        clinical_report: str,
        warnings: list[str],
    ) -> dict:
        """
        Build the final response object.
        """

        return {
            "original_transcript": transcript,
            "detected_language": language,
            "language_probability": language_probability,
            "english_transcript": english_text,
            "summary": summary,
            "patient": patient,
            "risk": risk,
            "clinical_report": clinical_report,
            "warnings": warnings,
        }

    def _save_report(
        self,
        report: dict,
    ) -> int:
        """
        Persist the report to the database and return its ID.
        """

        logger.info("Saving report to database.")

        return self.database.save_report(report)