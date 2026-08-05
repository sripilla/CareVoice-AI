"""
The text clinical report -- what the API returns as
`clinical_report` and what the text download contains.
"""

import pytest

from careinsight.report_generator import ReportGenerator
from config import REPORT_TITLE


@pytest.fixture
def generator():
    return ReportGenerator()


def test_includes_every_section(generator, patient):

    report = generator.generate(
        summary="Patient reports fever and cough.",
        patient=patient,
        risk={"risk_score": 5, "risk_level": "High"},
    )

    assert REPORT_TITLE in report
    assert "Clinical Summary" in report
    assert "Extracted Medical Information" in report
    assert "Risk Assessment" in report


def test_renders_patient_details(generator, patient):

    report = generator.generate(
        summary="A summary.",
        patient=patient,
        risk={"risk_score": 5, "risk_level": "High"},
    )

    assert "Lakshmi" in report
    assert "70" in report
    assert "fever" in report
    assert "cough" in report
    assert "Hypertension" in report
    assert "bp medicine" in report
    assert "three days" in report
    assert "Risk Score : 5" in report
    assert "Risk Level : High" in report


def test_empty_patient_reads_sensibly(generator, empty_patient):

    report = generator.generate(
        summary="",
        patient=empty_patient,
        risk={"risk_score": 0, "risk_level": "Low"},
    )

    assert "Unknown" in report
    assert "Not specified" in report
    assert "- None" in report
    assert "Risk Level : Low" in report


def test_format_list_bullets_items(generator):

    assert generator._format_list([]) == "- None"
    assert (
        generator._format_list(["fever", "cough"])
        == "- fever\n- cough"
    )


def test_clinical_summary_paragraph(generator, patient):

    paragraph = generator._clinical_summary(
        patient,
        {"risk_score": 5, "risk_level": "High"},
    )

    assert "70-year-old" in paragraph
    assert "Lakshmi" in paragraph
    assert "High Risk" in paragraph


def test_clinical_summary_handles_missing_data(
    generator,
    empty_patient,
):

    paragraph = generator._clinical_summary(
        empty_patient,
        {"risk_score": 0, "risk_level": "Low"},
    )

    assert "Not reported" in paragraph
    assert "none" in paragraph
