"""
The original two-stage pipeline: Whisper transcribes, NLLB
translates.

Kept as the default so existing behaviour is unchanged, and as the
baseline every other backend is measured against.
"""

from careinsight.pipelines.base import SpeechPipeline, SpeechResult
from speech.transcriber import SpeechTranscriber
from translation.translator import Translator
from utils.logger import get_logger

logger = get_logger(__name__)


class CascadePipeline(SpeechPipeline):
    """
    Speech -> native transcript -> English.

    The weakness is structural: the translator receives text with no
    indication of how reliable it is, so a mis-heard word becomes a
    fluent, confident, wrong English phrase.
    """

    label = "Whisper -> NLLB (cascade)"

    def __init__(self):

        logger.info("Initializing cascade pipeline.")

        self.transcriber = SpeechTranscriber()
        self.translator = Translator()

    def to_english(self, audio_path: str) -> SpeechResult:

        logger.info("Step 1: Speech Recognition")

        speech = self.transcriber.transcribe(audio_path)

        logger.info("Step 2: Translation")

        translation = self.translator.translate_with_meta(
            speech["transcript"],
            speech["language"],
        )

        return SpeechResult(
            english_transcript=translation["text"],
            original_transcript=speech["transcript"],
            detected_language=speech["language"],
            language_probability=speech["language_probability"],
            warnings=translation["warnings"],
        )
