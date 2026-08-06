"""
The transcription guard against language misdetection.

transcribe() itself needs a Whisper model, so these tests stub it
and exercise only transcribe_guarded()'s retry decision.
"""

import pytest

from conftest import skip_without

skip_without(
    "faster_whisper",
    "faster-whisper unavailable on this host",
)

from config import PRIMARY_AUDIO_LANGUAGE  # noqa: E402
from speech.transcriber import SpeechTranscriber  # noqa: E402

ROMANIZED_TELUGU = (
    "No Peru Lakshmi. No 70 Samchral. Gatamudu Rozruluga Naku "
    "Daggu Peryu Telekpati Jhuram Wunnai."
)


@pytest.fixture
def transcriber():
    """
    A SpeechTranscriber with no model loaded.
    """

    return object.__new__(SpeechTranscriber)


def _stub_transcribe(results):
    """
    Return a transcribe() stand-in that replays canned results and
    records the languages it was called with.
    """

    calls = []
    queue = list(results)

    def transcribe(audio_path, language=None):
        calls.append(language)
        return dict(queue.pop(0))

    return transcribe, calls


def test_genuine_english_is_not_retried(transcriber):

    transcriber.transcribe, calls = _stub_transcribe([
        {
            "transcript": "I have had a fever for three days.",
            "language": "en",
            "language_probability": 0.95,
        },
    ])

    speech = transcriber.transcribe_guarded("audio.wav")

    assert calls == [None]
    assert speech["language"] == "en"
    assert speech["warnings"] == []


def test_romanized_transliteration_triggers_forced_retry(transcriber):

    transcriber.transcribe, calls = _stub_transcribe([
        {
            "transcript": ROMANIZED_TELUGU,
            "language": "en",
            "language_probability": 0.62,
        },
        {
            "transcript": "నా పేరు లక్ష్మి. నాకు దగ్గు ఉంది.",
            "language": PRIMARY_AUDIO_LANGUAGE,
            "language_probability": 1.0,
        },
    ])

    speech = transcriber.transcribe_guarded("audio.wav")

    # First auto-detected, then forced.
    assert calls == [None, PRIMARY_AUDIO_LANGUAGE]

    assert speech["language"] == PRIMARY_AUDIO_LANGUAGE
    assert speech["transcript"].startswith("నా పేరు")

    # The clinician is told the guard fired.
    assert len(speech["warnings"]) == 1
    assert PRIMARY_AUDIO_LANGUAGE in speech["warnings"][0]


def test_native_script_detection_is_left_alone(transcriber):

    transcriber.transcribe, calls = _stub_transcribe([
        {
            "transcript": "నా పేరు లక్ష్మి.",
            "language": "te",
            "language_probability": 0.99,
        },
    ])

    speech = transcriber.transcribe_guarded("audio.wav")

    assert calls == [None]
    assert speech["language"] == "te"
    assert speech["warnings"] == []


def test_unsupported_language_triggers_forced_retry(transcriber):
    """
    A Latin-script misdetection does not always land on "en" --
    Whisper can pick any language the translator has no mapping
    for, which would pass through verbatim just the same.
    """

    transcriber.transcribe, calls = _stub_transcribe([
        {
            "transcript": ROMANIZED_TELUGU,
            "language": "id",
            "language_probability": 0.4,
        },
        {
            "transcript": "నా పేరు లక్ష్మి.",
            "language": PRIMARY_AUDIO_LANGUAGE,
            "language_probability": 1.0,
        },
    ])

    speech = transcriber.transcribe_guarded("audio.wav")

    assert calls == [None, PRIMARY_AUDIO_LANGUAGE]
    assert speech["language"] == PRIMARY_AUDIO_LANGUAGE
    assert len(speech["warnings"]) == 1
    assert "'id'" in speech["warnings"][0]


def test_supported_language_is_not_retried(transcriber):

    transcriber.transcribe, calls = _stub_transcribe([
        {
            "transcript": "मुझे बुखार है।",
            "language": "hi",
            "language_probability": 0.97,
        },
    ])

    speech = transcriber.transcribe_guarded("audio.wav")

    assert calls == [None]
    assert speech["language"] == "hi"
    assert speech["warnings"] == []


def test_empty_transcript_is_not_retried(transcriber):

    transcriber.transcribe, calls = _stub_transcribe([
        {
            "transcript": "",
            "language": "en",
            "language_probability": 0.5,
        },
    ])

    speech = transcriber.transcribe_guarded("audio.wav")

    assert calls == [None]
    assert speech["warnings"] == []
