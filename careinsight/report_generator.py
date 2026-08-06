from datetime import datetime

from config import (
    REPORT_DATE_FORMAT,
    REPORT_SEPARATOR,
    REPORT_SUB_SEPARATOR,
    REPORT_TITLE,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """
    Generate a formatted clinical report.
    """

    def generate(
        self,
        summary: str,
        patient: dict,
        risk: dict,
        language: str = None,
        language_probability: float = None,
        warnings: list = None,
    ) -> str:
        """
        Generate the complete clinical report.

        The language line and the warnings section make the report
        self-diagnosing: when speech recognition or translation
        degrades, the report itself says so instead of presenting
        unreliable data with full confidence.
        """

        logger.info("Generating clinical report...")

        timestamp = datetime.now().strftime(
            REPORT_DATE_FORMAT
        )

        report = f"""
{REPORT_SEPARATOR}
                {REPORT_TITLE}
{REPORT_SEPARATOR}

Generated On : {timestamp}{self._language_line(language, language_probability)}
{self._warnings_section(warnings)}
{REPORT_SUB_SEPARATOR}
Clinical Summary
{REPORT_SUB_SEPARATOR}

{self._clinical_summary(patient, risk)}

{REPORT_SUB_SEPARATOR}
Conversation Summary (BART)
{REPORT_SUB_SEPARATOR}

{summary}

{REPORT_SUB_SEPARATOR}
Extracted Medical Information
{REPORT_SUB_SEPARATOR}

Patient Name : {patient.get("patient_name") or "Unknown"}
Age          : {patient.get("age") or "Unknown"}

Symptoms
{self._format_list(patient.get("symptoms", []))}

Conditions
{self._format_list(patient.get("conditions", []))}

Medications
{self._format_list(patient.get("medications", []))}

Duration
- {patient.get("duration") or "Not specified"}

{REPORT_SUB_SEPARATOR}
Risk Assessment
{REPORT_SUB_SEPARATOR}

Risk Score : {risk["risk_score"]}
Risk Level : {risk["risk_level"]}

{REPORT_SEPARATOR}
"""

        logger.info(
            "Clinical report generated successfully."
        )

        return report

    # ======================================================
    # Helper Methods
    # ======================================================

    def _language_line(
        self,
        language: str,
        probability: float,
    ) -> str:
        """
        Format the detected-language line, when known.
        """

        if not language:
            return ""

        line = f"\nLanguage     : {language}"

        if probability:
            line += f" (confidence {probability:.0%})"

        return line

    def _warnings_section(
        self,
        warnings: list,
    ) -> str:
        """
        Format the processing-warnings section, when present.
        """

        if not warnings:
            return ""

        items = "\n".join(
            f"! {warning}"
            for warning in warnings
        )

        return (
            f"\n{REPORT_SUB_SEPARATOR}\n"
            "Processing Warnings\n"
            f"{REPORT_SUB_SEPARATOR}\n\n"
            f"{items}\n"
        )

    def _clinical_summary(
        self,
        patient: dict,
        risk: dict,
    ) -> str:
        """
        Generate the clinical summary paragraph.
        """

        name = patient.get("patient_name") or "Unknown"

        age = patient.get("age") or "Unknown"

        duration = (
            patient.get("duration")
            or "Not specified"
        )

        symptoms = (
            ", ".join(patient.get("symptoms", []))
            or "Not reported"
        )

        conditions = (
            ", ".join(patient.get("conditions", [])).lower()
            or "none"
        )

        medications = (
            ", ".join(patient.get("medications", []))
            or "none"
        )

        return (
            f"A {age}-year-old patient ({name}) reports\n"
            f"{symptoms} for {duration}.\n\n"
            f"The patient has {conditions}\n"
            f"and is currently taking {medications}.\n\n"
            f"Based on the extracted clinical information,\n"
            f"the patient is classified as\n\n"
            f"{risk['risk_level']} Risk\n"
            f"(Risk Score: {risk['risk_score']})."
        )

    def _format_list(
        self,
        items: list,
    ) -> str:
        """
        Format a list as bullet points.
        """

        if not items:
            return "- None"

        return "\n".join(
            f"- {item}"
            for item in items
        )