"""
Clinical entity extraction.

Needs spaCy and en_core_web_sm, but no downloaded model weights,
so this stays in the fast suite.
"""

import pytest

from conftest import skip_without

skip_without("spacy", "spaCy unavailable on this host")

from careinsight.extractor import MedicalExtractor  # noqa: E402


@pytest.fixture(scope="module")
def extractor():
    return MedicalExtractor()


# ==========================================================
# Names
# ==========================================================

def test_extracts_name_from_self_introduction(extractor):

    data = extractor.extract("My name is Lakshmi.")

    assert data["patient_name"] == "Lakshmi"


def test_name_pattern_is_case_insensitive(extractor):

    data = extractor.extract("my name is Ravi and I am unwell.")

    assert data["patient_name"] == "Ravi"


# ==========================================================
# Age
# ==========================================================

@pytest.mark.parametrize(
    "text, expected",
    [
        ("I am 70 years old.", 70),
        ("She is 5 year old.", 5),
        ("He is 45years old.", 45),
    ],
)
def test_extracts_age(extractor, text, expected):

    assert extractor.extract(text)["age"] == expected


def test_missing_age_stays_none(extractor):

    assert extractor.extract("I have a fever.")["age"] is None


# ==========================================================
# Duration
# ==========================================================

@pytest.mark.parametrize(
    "text, expected",
    [
        ("I have had a fever for 3 days.", "3 days"),
        ("Coughing for 2 weeks.", "2 weeks"),
        ("Unwell for 6 months.", "6 months"),
    ],
)
def test_extracts_numeric_duration(extractor, text, expected):

    assert extractor.extract(text)["duration"] == expected


def test_extracts_spelled_out_duration(extractor):

    data = extractor.extract(
        "I have had a fever for three days."
    )

    assert data["duration"] == "three days"


# ==========================================================
# Symptoms, conditions, medications
# ==========================================================

def test_extracts_symptoms(extractor):

    data = extractor.extract(
        "I have a fever and a cough."
    )

    assert "fever" in data["symptoms"]
    assert "cough" in data["symptoms"]


def test_symptoms_are_deduplicated(extractor):

    data = extractor.extract(
        "I have a fever. The fever is high. Fever since Monday."
    )

    assert data["symptoms"].count("fever") == 1


def test_maps_colloquial_disease_names(extractor):
    """
    'blood pressure' should be recorded as Hypertension via
    DISEASE_MAP, not verbatim.
    """

    data = extractor.extract("I have blood pressure.")

    assert "Hypertension" in data["conditions"]


def test_infers_condition_from_medication(extractor):
    """
    A patient on BP medicine has hypertension even when they never
    name the condition.
    """

    data = extractor.extract(
        "I take bp medicine every morning."
    )

    assert "bp medicine" in data["medications"]
    assert "Hypertension" in data["conditions"]


def test_inferred_condition_is_not_duplicated(extractor):

    data = extractor.extract(
        "I have hypertension and I take bp medicine."
    )

    assert data["conditions"].count("Hypertension") == 1


# ==========================================================
# Degenerate input
# ==========================================================

def test_empty_text_returns_an_empty_record(extractor):

    data = extractor.extract("   ")

    assert data["patient_name"] is None
    assert data["age"] is None
    assert data["symptoms"] == []
    assert data["conditions"] == []
    assert data["medications"] == []
    assert data["duration"] is None


def test_extract_always_returns_every_key(extractor):

    data = extractor.extract("Hello there.")

    assert set(data) == {
        "patient_name",
        "age",
        "symptoms",
        "conditions",
        "medications",
        "duration",
    }
