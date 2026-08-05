"""
End-to-end pipeline run against the sample Telugu recording.

Marked slow: this loads Whisper, NLLB and BART, downloading several
GB on first run. Excluded from the default suite -- run it with
`pytest -m slow`.
"""

import pytest

from conftest import skip_without
from config import DEFAULT_AUDIO_FILE

pytestmark = pytest.mark.slow

skip_without(
    "faster_whisper",
    "Speech stack unavailable on this host",
)


@pytest.fixture(scope="module")
def engine():

    from careinsight.engine import CareVoiceEngine

    return CareVoiceEngine()


@pytest.fixture(scope="module")
def result(engine):

    if not DEFAULT_AUDIO_FILE.exists():
        pytest.skip(f"Sample audio missing: {DEFAULT_AUDIO_FILE}")

    return engine.process_audio(str(DEFAULT_AUDIO_FILE))


def test_returns_every_field(result):

    assert set(result) >= {
        "report_id",
        "original_transcript",
        "detected_language",
        "language_probability",
        "english_transcript",
        "summary",
        "patient",
        "risk",
        "clinical_report",
        "warnings",
    }


def test_detects_telugu(result):

    assert result["detected_language"] == "te"
    assert result["language_probability"] > 0.5


def test_transcribes_and_translates(result):

    assert result["original_transcript"].strip()
    assert result["english_transcript"].strip()

    # The translation should actually be English, not a pass-through
    # of the Telugu source.
    assert (
        result["english_transcript"]
        != result["original_transcript"]
    )


def test_produces_a_summary_and_risk_level(result):

    assert result["summary"].strip()
    assert result["risk"]["risk_level"] in {
        "Low",
        "Medium",
        "High",
    }
    assert isinstance(result["risk"]["risk_score"], int)


def test_persists_the_report(engine, result):

    stored = engine.database.get_report_by_id(
        result["report_id"]
    )

    assert stored is not None
    assert stored["detected_language"] == "te"


def test_report_renders_as_pdf(result):

    from utils.pdf import build_report_pdf

    assert build_report_pdf(result).startswith(b"%PDF-")
