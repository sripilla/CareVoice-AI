"""
The speech-to-English contract.

Everything downstream of this point -- summarization, entity
extraction, risk scoring, reporting -- works on English text and does
not care how that English was produced. Isolating the front end
behind one method is what makes the backends interchangeable.
"""

from dataclasses import dataclass, field


@dataclass
class SpeechResult:
    """
    The output every pipeline must produce.

    Attributes
    ----------
    english_transcript : str
        English text. This is what the rest of the pipeline consumes.

    original_transcript : str
        The consultation in the language it was spoken, for the
        clinician to check against. May be empty for backends that
        translate directly and are configured to skip the extra pass.

    detected_language : str
        Whisper-style two-letter code, or "unknown".

    language_probability : float
        Detection confidence in 0..1. Zero when unknown.

    warnings : list[str]
        Non-fatal problems worth surfacing to the clinician, such as
        an unsupported language or a skipped stage.
    """

    english_transcript: str
    original_transcript: str = ""
    detected_language: str = "unknown"
    language_probability: float = 0.0
    warnings: list = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "english_transcript": self.english_transcript,
            "original_transcript": self.original_transcript,
            "detected_language": self.detected_language,
            "language_probability": self.language_probability,
            "warnings": list(self.warnings),
        }


class SpeechPipeline:
    """
    Base class for speech-to-English backends.
    """

    #: Shown in logs, the dashboard and benchmark output.
    label = "unnamed pipeline"

    def to_english(self, audio_path: str) -> SpeechResult:
        """
        Turn a recording into English text.
        """

        raise NotImplementedError
