"""
Risk scoring is pure arithmetic over the extracted patient dict,
so it can be pinned down exactly.
"""

import pytest

from careinsight.risk_assessor import RiskAssessor
from config import (
    AGE_RISK_THRESHOLD,
    LOW_RISK_MAX,
    MEDIUM_RISK_MAX,
)


@pytest.fixture
def assessor():
    return RiskAssessor()


def test_empty_patient_is_low_risk(assessor, empty_patient):

    result = assessor.assess(empty_patient)

    assert result["risk_score"] == 0
    assert result["risk_level"] == "Low"


def test_scores_age_symptoms_and_conditions(assessor, patient):

    # 70 years (1) + fever (1) + cough (1)
    # + Hypertension (1) + Diabetes (1)
    result = assessor.assess(patient)

    assert result["risk_score"] == 5
    assert result["risk_level"] == "High"


@pytest.mark.parametrize(
    "age, expected",
    [
        (AGE_RISK_THRESHOLD - 1, 0),
        (AGE_RISK_THRESHOLD, 1),
        (AGE_RISK_THRESHOLD + 1, 1),
    ],
)
def test_age_threshold_is_inclusive(
    assessor,
    empty_patient,
    age,
    expected,
):

    empty_patient["age"] = age

    assert assessor.assess(empty_patient)["risk_score"] == expected


def test_missing_age_does_not_score(assessor, empty_patient):

    empty_patient["age"] = None

    assert assessor.assess(empty_patient)["risk_score"] == 0


def test_breathlessness_outweighs_other_symptoms(
    assessor,
    empty_patient,
):

    empty_patient["symptoms"] = ["breathlessness"]

    assert assessor.assess(empty_patient)["risk_score"] == 2


def test_unknown_symptoms_score_zero(assessor, empty_patient):

    empty_patient["symptoms"] = ["hiccups", "itching"]

    assert assessor.assess(empty_patient)["risk_score"] == 0


@pytest.mark.parametrize(
    "score, expected",
    [
        (0, "Low"),
        (LOW_RISK_MAX, "Low"),
        (LOW_RISK_MAX + 1, "Medium"),
        (MEDIUM_RISK_MAX, "Medium"),
        (MEDIUM_RISK_MAX + 1, "High"),
        (99, "High"),
    ],
)
def test_risk_level_boundaries(assessor, score, expected):

    assert assessor._risk_level(score) == expected


def test_assess_tolerates_missing_keys(assessor):

    result = assessor.assess({})

    assert result["risk_score"] == 0
    assert result["risk_level"] == "Low"
