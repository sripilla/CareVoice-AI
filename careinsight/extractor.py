import re

import spacy

from careinsight.medical_patterns import patterns
from config import (
    BP_MEDICATIONS,
    DISEASE_MAP,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class MedicalExtractor:
    """
    Extract structured clinical information
    from translated English text.
    """

    def __init__(self):
        """
        Initialize spaCy and Entity Ruler.
        """

        logger.info("Loading spaCy model...")

        try:

            self.nlp = spacy.load("en_core_web_sm")

            if "entity_ruler" not in self.nlp.pipe_names:

                ruler = self.nlp.add_pipe(
                    "entity_ruler",
                    before="ner",
                )

                ruler.add_patterns(patterns)

            logger.info(
                "Medical entity extractor initialized."
            )

        except Exception:

            logger.exception(
                "Failed to initialize MedicalExtractor."
            )

            raise

    # ======================================================
    # Public API
    # ======================================================

    def extract(
        self,
        text: str,
    ) -> dict:
        """
        Extract structured clinical information.
        """

        if not text.strip():

            logger.warning(
                "Received empty text for extraction."
            )

            return self._initialize_clinical_data()

        logger.info(
            "Extracting medical entities..."
        )

        doc = self.nlp(text)

        data = self._initialize_clinical_data()

        self._extract_entities(
            doc,
            data,
        )

        self._extract_duration(
            text,
            data,
        )

        self._infer_conditions(
            data,
        )

        logger.info(
            "Medical entity extraction completed."
        )

        logger.debug(
            "Extracted clinical data: %s",
            data,
        )

        return data

    # ======================================================
    # Helper Methods
    # ======================================================

    def _initialize_clinical_data(self) -> dict:
        """
        Initialize an empty clinical data record.
        """

        return {
            "symptoms": [],
            "conditions": [],
            "medications": [],
            "duration": None,
        }

    def _extract_entities(
        self,
        doc,
        data: dict,
    ):
        """
        Extract symptoms, diseases,
        and existing medications.
        """

        for ent in doc.ents:

            text_entity = ent.text.lower().strip()
            lemma_entity = ent.lemma_.lower().strip()

            # Symptoms

            if ent.label_ == "SYMPTOM":

                if lemma_entity not in {
                    symptom.lower()
                    for symptom in data["symptoms"]
                }:

                    data["symptoms"].append(
                        lemma_entity
                    )

            # Diseases

            elif ent.label_ == "DISEASE":

                disease = DISEASE_MAP.get(
                    text_entity,
                    ent.text.title(),
                )

                if disease not in data["conditions"]:

                    data["conditions"].append(
                        disease
                    )

            # Existing Medications

            elif ent.label_ == "MEDICATION":

                if text_entity not in {
                    medicine.lower()
                    for medicine in data["medications"]
                }:

                    data["medications"].append(
                        text_entity
                    )

    def _extract_duration(
        self,
        text: str,
        data: dict,
    ):
        """
        Extract symptom duration.
        """

        duration = re.search(
            r"(\d+\s*(day|days|week|weeks|month|months))",
            text,
            re.IGNORECASE,
        )

        if duration:

            data["duration"] = duration.group(1)

            return

        duration = re.search(
            r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\s+"
            r"(day|days|week|weeks|month|months)\b",
            text,
            re.IGNORECASE,
        )

        if duration:

            data["duration"] = duration.group(0)

    def _infer_conditions(
        self,
        data: dict,
    ):
        """
        Infer conditions from existing medications.
        """

        if any(
            medicine.lower() in BP_MEDICATIONS
            for medicine in data["medications"]
        ):

            if "Hypertension" not in data["conditions"]:

                data["conditions"].append(
                    "Hypertension"
                )