"""
Shared fixtures.

Tests run from the repository root so that `config`, `careinsight`
and friends import as top-level packages.
"""

import importlib
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def skip_without(module: str, reason: str):
    """
    Import a native-backed dependency, or skip the whole module.

    pytest.importorskip only catches ImportError, but torch and
    CTranslate2 raise OSError when their compiled libraries cannot
    load -- on Windows that means the Microsoft Visual C++
    Redistributable is missing. Skipping keeps the failure visible
    without collapsing the rest of the suite.
    """

    try:
        return importlib.import_module(module)

    except (ImportError, OSError) as error:

        pytest.skip(
            f"{reason} ({module}: {error})",
            allow_module_level=True,
        )


@pytest.fixture
def patient():
    """
    A fully populated extraction result.
    """

    return {
        "patient_name": "Lakshmi",
        "age": 70,
        "symptoms": ["fever", "cough"],
        "conditions": ["Hypertension", "Diabetes"],
        "medications": ["bp medicine"],
        "duration": "three days",
    }


@pytest.fixture
def empty_patient():
    """
    What the extractor returns when nothing is recognised.
    """

    return {
        "patient_name": None,
        "age": None,
        "symptoms": [],
        "conditions": [],
        "medications": [],
        "duration": None,
    }


@pytest.fixture
def report(patient):
    """
    A complete pipeline report, as CareVoiceEngine builds it.
    """

    return {
        "original_transcript": (
            "నా పేరు లక్ష్మి. నాకు మూడు రోజులుగా జ్వరం ఉంది."
        ),
        "detected_language": "te",
        "language_probability": 0.98,
        "english_transcript": (
            "My name is Lakshmi. I have had a fever for three days."
        ),
        "summary": "Patient reports fever and cough for three days.",
        "patient": patient,
        "risk": {"risk_score": 5, "risk_level": "High"},
        "clinical_report": "CAREVOICE AI CLINICAL REPORT",
        "warnings": [],
    }
