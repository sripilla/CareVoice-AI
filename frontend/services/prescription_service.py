from database.database import DatabaseManager
from translation.translator import Translator
from utils.logger import get_logger

logger = get_logger(__name__)


class PrescriptionService:
    """
    Service for managing doctor prescriptions
    and patient-language guidelines.
    """

    def __init__(
        self,
        database: DatabaseManager | None = None,
        translator: Translator | None = None,
    ):
        """
        Initialize prescription service dependencies.
        """

        self.database = (
            database
            if database is not None
            else DatabaseManager()
        )

        self.translator = (
            translator
            if translator is not None
            else Translator()
        )

    def get_consultation(
        self,
        consultation_id: int,
    ):
        """
        Retrieve a consultation by ID.
        """

        consultation = (
            self.database.get_consultation_by_id(
                consultation_id
            )
        )

        if consultation is None:

            logger.error(
                "Consultation %d was not found.",
                consultation_id,
            )

            raise ValueError(
                f"Consultation {consultation_id} not found."
            )

        return consultation

    def translate_prescription(
        self,
        consultation_id: int,
        english_prescription: str,
        english_guidelines: str,
    ) -> dict:
        """
        Translate prescription and guidelines into
        the patient's detected consultation language.

        The patient language is always retrieved from
        the saved consultation and is never selected
        manually.
        """

        consultation = self.get_consultation(
            consultation_id
        )

        patient_language = consultation[
            "detected_language"
        ]

        if not patient_language:

            logger.error(
                "No detected language found for "
                "consultation %d.",
                consultation_id,
            )

            raise ValueError(
                "Patient language is not available "
                "for this consultation."
            )

        translated_prescription = (
            self.translator.translate_from_english(
                text=english_prescription,
                target_language=patient_language,
            )
        )

        translated_guidelines = (
            self.translator.translate_from_english(
                text=english_guidelines,
                target_language=patient_language,
            )
        )

        logger.info(
            "Prescription translated for "
            "consultation %d using language %s.",
            consultation_id,
            patient_language,
        )

        return {
            "consultation_id": consultation_id,
            "patient_language": patient_language,
            "english_prescription": english_prescription,
            "translated_prescription": (
                translated_prescription
            ),
            "english_guidelines": english_guidelines,
            "translated_guidelines": (
                translated_guidelines
            ),
        }

    def save_prescription(
        self,
        prescription: dict,
    ) -> int:
        """
        Save a translated prescription and guidelines.
        """

        prescription_id = (
            self.database.save_prescription(
                prescription
            )
        )

        logger.info(
            "Prescription %d saved successfully.",
            prescription_id,
        )

        return prescription_id

    def get_prescription(
        self,
        consultation_id: int,
    ):
        """
        Retrieve the prescription for a consultation.
        """

        return (
            self.database
            .get_prescription_by_consultation_id(
                consultation_id
            )
        )