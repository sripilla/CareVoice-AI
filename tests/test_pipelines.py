"""
The pluggable speech-to-English layer.

These exercise the contract and the registry with stubs, so they run
without downloading any model.
"""

import pytest

from careinsight.pipelines import (
    PIPELINES,
    SpeechPipeline,
    SpeechResult,
    build_pipeline,
    get_pipeline_class,
)


# ==========================================================
# The contract
# ==========================================================

def test_result_defaults_are_safe():
    """
    A backend that only sets English must still produce every field
    the engine and the report expect.
    """

    result = SpeechResult(english_transcript="I have a fever.")

    data = result.as_dict()

    assert data["english_transcript"] == "I have a fever."
    assert data["original_transcript"] == ""
    assert data["detected_language"] == "unknown"
    assert data["language_probability"] == 0.0
    assert data["warnings"] == []


def test_result_as_dict_matches_engine_expectations(report):

    result = SpeechResult(
        english_transcript="English",
        original_transcript="తెలుగు",
        detected_language="te",
        language_probability=0.95,
        warnings=["a warning"],
    )

    data = result.as_dict()

    # The engine reads exactly these keys.
    assert set(data) == {
        "english_transcript",
        "original_transcript",
        "detected_language",
        "language_probability",
        "warnings",
    }


def test_as_dict_copies_warnings():
    """
    Callers append to the engine's warning list; that must not write
    back into the pipeline's own state.
    """

    result = SpeechResult(
        english_transcript="x",
        warnings=["first"],
    )

    data = result.as_dict()
    data["warnings"].append("second")

    assert result.warnings == ["first"]


def test_base_pipeline_requires_implementation():

    with pytest.raises(NotImplementedError):
        SpeechPipeline().to_english("audio.wav")


# ==========================================================
# The registry
# ==========================================================

def test_every_backend_is_registered():

    assert set(PIPELINES) == {"cascade", "seamless", "indic"}


def test_unknown_pipeline_is_rejected_clearly():

    with pytest.raises(ValueError) as error:
        get_pipeline_class("does-not-exist")

    message = str(error.value)

    assert "does-not-exist" in message

    # The message should list the valid options.
    for name in PIPELINES:
        assert name in message


def test_pipeline_name_is_normalized():

    from careinsight.pipelines.cascade import CascadePipeline

    assert get_pipeline_class("  CASCADE ") is CascadePipeline


@pytest.mark.parametrize("name", sorted(PIPELINES))
def test_backends_are_importable_and_labelled(name):
    """
    Import each backend class without instantiating it -- catches
    syntax errors and bad imports without loading model weights.
    """

    pipeline_class = get_pipeline_class(name)

    assert issubclass(pipeline_class, SpeechPipeline)
    assert pipeline_class.label
    assert pipeline_class.label != SpeechPipeline.label


def test_build_pipeline_uses_the_registry(monkeypatch):

    built = {}

    class StubPipeline(SpeechPipeline):
        label = "stub"

        def __init__(self):
            built["yes"] = True

        def to_english(self, audio_path):
            return SpeechResult(english_transcript="stub")

    monkeypatch.setitem(
        PIPELINES,
        "stub",
        (__name__, "StubPipeline"),
    )

    monkeypatch.setattr(
        f"{__name__}.StubPipeline",
        StubPipeline,
        raising=False,
    )

    import sys

    sys.modules[__name__].StubPipeline = StubPipeline

    pipeline = build_pipeline("stub")

    assert built.get("yes")
    assert isinstance(pipeline, StubPipeline)


# ==========================================================
# Cascade warning propagation
# ==========================================================

def test_cascade_merges_transcriber_and_translator_warnings():
    """
    The misdetection guard's warning and any translation warning
    must both reach the SpeechResult the engine consumes.
    """

    from careinsight.pipelines.cascade import CascadePipeline

    pipeline = object.__new__(CascadePipeline)

    class StubTranscriber:
        def transcribe_guarded(self, audio_path):
            return {
                "transcript": "నా పేరు లక్ష్మి.",
                "language": "te",
                "language_probability": 1.0,
                "warnings": ["retried in 'te'"],
            }

    class StubTranslator:
        def translate_with_meta(self, text, language):
            return {
                "text": "My name is Lakshmi.",
                "translated": True,
                "warnings": ["translator warning"],
            }

    pipeline.transcriber = StubTranscriber()
    pipeline.translator = StubTranslator()

    result = pipeline.to_english("audio.wav")

    assert result.english_transcript == "My name is Lakshmi."
    assert result.warnings == [
        "retried in 'te'",
        "translator warning",
    ]


# ==========================================================
# Engine integration
# ==========================================================

def test_engine_consumes_any_pipeline(monkeypatch, tmp_path):
    """
    The engine must work with a backend it has never seen, proving
    the front end really is swappable.
    """

    from careinsight.pipelines.base import SpeechResult as Result

    class FakePipeline(SpeechPipeline):
        label = "fake"

        def to_english(self, audio_path):
            return Result(
                english_transcript=(
                    "My name is Ravi. I am 70 years old. "
                    "I have had a fever and cough for three days."
                ),
                original_transcript="నా పేరు రవి",
                detected_language="te",
                language_probability=0.97,
                warnings=["pipeline warning"],
            )

    import careinsight.engine as engine_module

    monkeypatch.setattr(
        engine_module,
        "build_pipeline",
        lambda name=None: FakePipeline(),
    )

    # Stub the English-side models so nothing is downloaded.
    monkeypatch.setattr(
        engine_module,
        "MedicalSummarizer",
        lambda: type(
            "S",
            (),
            {"summarize_text": lambda self, text: "A summary."},
        )(),
    )

    class FakeExtractor:
        def extract(self, text):
            return {
                "patient_name": "Ravi",
                "age": 70,
                "symptoms": ["fever", "cough"],
                "conditions": [],
                "medications": [],
                "duration": "three days",
            }

    monkeypatch.setattr(
        engine_module,
        "MedicalExtractor",
        FakeExtractor,
    )

    monkeypatch.setattr(
        engine_module,
        "DatabaseManager",
        lambda: _StubDatabase(tmp_path),
    )

    engine = engine_module.CareVoiceEngine()

    report = engine.process_audio("consultation.wav")

    assert report["detected_language"] == "te"
    assert report["language_probability"] == 0.97
    assert report["original_transcript"] == "నా పేరు రవి"
    assert "fever" in report["english_transcript"]

    # Warnings raised by the pipeline reach the response.
    assert "pipeline warning" in report["warnings"]

    # And the English-side stages still ran.
    # age 70 (1) + fever (1) + cough (1) = 3, the Medium ceiling.
    assert report["patient"]["patient_name"] == "Ravi"
    assert report["risk"]["risk_score"] == 3
    assert report["risk"]["risk_level"] == "Medium"
    assert report["report_id"] == 1


class _StubDatabase:
    """
    Real DatabaseManager against a temporary file.
    """

    def __init__(self, tmp_path):

        from database.database import DatabaseManager

        self._db = DatabaseManager(str(tmp_path / "pipelines.db"))

    def save_report(self, report):
        return self._db.save_report(report)

    def close(self):
        self._db.close()
