import pytest

from careinsight.risk_assessor import RiskAssessor


@pytest.fixture
def assessor():
    return RiskAssessor()


def test_low_risk_patient(assessor):
    """
    Young patient with no symptoms or conditions.
    """

    patient = {
        "age": 25,
        "symptoms": [],
        "conditions": [],
    }

    result = assessor.assess(patient)

    assert result["risk_score"] == 0
    assert result["risk_level"] == "Low"


def test_elderly_patient_has_higher_risk(assessor):
    """
    Elderly patient should receive age risk points.
    """

    patient = {
        "age": 70,
        "symptoms": [],
        "conditions": [],
    }

    result = assessor.assess(patient)

    assert result["risk_score"] >= 1
    assert result["risk_level"] in ["Low", "Medium", "High"]


def test_patient_with_symptoms(assessor):
    """
    Symptoms should increase the risk score.
    """

    patient = {
        "age": 30,
        "symptoms": ["cough", "fever"],
        "conditions": [],
    }

    result = assessor.assess(patient)

    assert result["risk_score"] > 0


def test_patient_with_conditions(assessor):
    """
    Medical conditions should contribute to the risk score.
    """

    patient = {
        "age": 30,
        "symptoms": [],
        "conditions": ["Hypertension", "Diabetes"],
    }

    result = assessor.assess(patient)

    assert result["risk_score"] > 0


def test_high_risk_patient(assessor):
    """
    Multiple risk factors should produce a High risk level.
    """

    patient = {
        "age": 70,
        "symptoms": ["cough", "fever"],
        "conditions": ["Hypertension", "Diabetes"],
    }

    result = assessor.assess(patient)

    assert result["risk_level"] == "High"


def test_empty_patient_dictionary(assessor):
    """
    Empty patient input should not raise an exception.
    """

    result = assessor.assess({})

    assert "risk_score" in result
    assert "risk_level" in result


def test_unknown_symptoms_are_ignored(assessor):
    """
    Unknown symptoms should not contribute to the score.
    """

    patient = {
        "age": 25,
        "symptoms": ["unknown_symptom"],
        "conditions": [],
    }

    result = assessor.assess(patient)

    assert result["risk_score"] == 0


def test_unknown_conditions_are_ignored(assessor):
    """
    Unknown conditions should not contribute to the score.
    """

    patient = {
        "age": 25,
        "symptoms": [],
        "conditions": ["unknown_condition"],
    }

    result = assessor.assess(patient)

    assert result["risk_score"] == 0