from config import (
    AGE_RISK_SCORE,
    AGE_RISK_THRESHOLD,
    CONDITION_RISK_SCORES,
    LOW_RISK_MAX,
    MEDIUM_RISK_MAX,
    SYMPTOM_RISK_SCORES,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class RiskAssessor:
    """
    Calculate a patient's clinical risk score
    based on extracted medical information.
    """

    def assess(
        self,
        patient: dict,
    ) -> dict:
        """
        Assess patient risk.

        Parameters
        ----------
        patient : dict
            Extracted patient information.

        Returns
        -------
        dict
            {
                "risk_score": int,
                "risk_level": str
            }
        """

        logger.info(
            "Assessing patient risk..."
        )

        score = 0

        score += self._age_score(patient)

        score += self._symptom_score(patient)

        score += self._condition_score(patient)

        level = self._risk_level(score)

        logger.info(
            "Risk assessment completed."
        )

        logger.debug(
            "Risk Score: %d | Level: %s",
            score,
            level,
        )

        return {
            "risk_score": score,
            "risk_level": level,
        }

    # ======================================================
    # Helper Methods
    # ======================================================

    def _age_score(
        self,
        patient: dict,
    ) -> int:
        """
        Calculate age-based risk.
        """

        age = patient.get("age")

        if age and age >= AGE_RISK_THRESHOLD:
            return AGE_RISK_SCORE

        return 0

    def _symptom_score(
        self,
        patient: dict,
    ) -> int:
        """
        Calculate symptom-based risk.
        """

        score = 0

        for symptom in patient.get("symptoms", []):

            score += SYMPTOM_RISK_SCORES.get(
                symptom,
                0,
            )

        return score

    def _condition_score(
        self,
        patient: dict,
    ) -> int:
        """
        Calculate condition-based risk.
        """

        score = 0

        for condition in patient.get("conditions", []):

            score += CONDITION_RISK_SCORES.get(
                condition,
                0,
            )

        return score

    def _risk_level(
        self,
        score: int,
    ) -> str:
        """
        Convert risk score into a
        clinical risk category.
        """

        if score <= LOW_RISK_MAX:
            return "Low"

        if score <= MEDIUM_RISK_MAX:
            return "Medium"

        return "High"