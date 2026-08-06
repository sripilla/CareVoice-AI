from pathlib import Path

from faster_whisper import WhisperModel

from config import (
    DEFAULT_BEAM_SIZE,
    DEFAULT_CONDITION_ON_PREVIOUS_TEXT,
    DEFAULT_TEMPERATURE,
    DEFAULT_VAD_FILTER,
    LANGUAGE_MAP,
    PRIMARY_AUDIO_LANGUAGE,
    WHISPER_COMPUTE_TYPE,
    WHISPER_DEVICE,
    WHISPER_MODEL,
)
from utils.language import looks_like_english
from utils.logger import get_logger

logger = get_logger(__name__)

# CTranslate2 backends. Anything else has to be downgraded.
CT2_DEVICES = {"cpu", "cuda"}


def _resolve_whisper_device(
    device: str,
    compute_type: str,
) -> tuple:
    """
    Map a requested device onto something CTranslate2 supports.

    "auto" resolves through the shared device helper first, so a
    single CAREVOICE_DEVICE setting works across the whole stack;
    MPS is then downgraded to CPU because CTranslate2 cannot target
    Metal.
    """

    if device == "auto":

        from utils.device import resolve_device

        device = resolve_device("auto")

    if device in CT2_DEVICES:
        return device, compute_type

    if device == "mps":

        logger.info(
            "CTranslate2 has no Metal backend, so Whisper runs on "
            "CPU. Use CAREVOICE_PIPELINE=seamless for GPU-"
            "accelerated speech on Apple Silicon."
        )

    else:

        logger.warning(
            "Device '%s' is not supported by CTranslate2; using CPU.",
            device,
        )

    # int8 is the sensible CPU default; float16 is a GPU format.
    if compute_type == "float16":
        compute_type = "int8"

    return "cpu", compute_type


class SpeechTranscriber:
    """
    Speech-to-Text module using Faster Whisper.

    Automatically detects the spoken language and returns
    the transcript along with language metadata.
    """

    def __init__(self, model_name: str = WHISPER_MODEL):
        """
        Initialize the Faster Whisper model.
        """

        # CTranslate2 (which powers faster-whisper) only has CPU and
        # CUDA backends -- there is no Metal support, so on Apple
        # Silicon this runs on CPU no matter what the rest of the
        # stack does. That is a library limitation, not a tuning
        # choice: if you need GPU speech recognition on a Mac, use
        # the 'seamless' pipeline, which runs on MPS through
        # PyTorch.

        self.device, self.compute_type = _resolve_whisper_device(
            WHISPER_DEVICE,
            WHISPER_COMPUTE_TYPE,
        )

        logger.info(
            "Loading Faster Whisper model: %s (%s, %s)",
            model_name,
            self.device,
            self.compute_type,
        )

        try:
            self.model = WhisperModel(
                model_name,
                device=self.device,
                compute_type=self.compute_type,
            )

            logger.info("Whisper model loaded successfully.")

        except Exception:
            logger.exception("Failed to load Faster Whisper model.")
            raise

    def transcribe(
        self,
        audio_path: str,
        language: str = None,
    ) -> dict:
        """
        Transcribe an audio file.

        Parameters
        ----------
        audio_path : str
            Path to the audio file.

        language : str, optional
            Force transcription in this language instead of relying
            on Whisper's automatic detection.

        Returns
        -------
        dict
            {
                "transcript": "...",
                "language": "te",
                "language_probability": 0.99,
            }
        """

        logger.info("Transcribing audio: %s", audio_path)

        if language:
            logger.info(
                "Forcing transcription language: %s",
                language,
            )

        try:

            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=DEFAULT_BEAM_SIZE,
                vad_filter=DEFAULT_VAD_FILTER,
                condition_on_previous_text=(
                    DEFAULT_CONDITION_ON_PREVIOUS_TEXT
                ),
                temperature=DEFAULT_TEMPERATURE,
            )

            logger.info(
                "Detected language: %s (confidence %.2f)",
                info.language,
                info.language_probability,
            )

            transcript = []

            for segment in segments:

                logger.debug(
                    "[%.2fs -> %.2fs] %s",
                    segment.start,
                    segment.end,
                    segment.text,
                )

                transcript.append(segment.text)

            transcript_text = " ".join(transcript).strip()

            logger.info("Transcription completed successfully.")

            return {
                "transcript": transcript_text,
                "language": info.language,
                "language_probability": info.language_probability,
            }

        except Exception:
            logger.exception("Audio transcription failed.")
            raise

    def transcribe_guarded(self, audio_path: str) -> dict:
        """
        Transcribe with a guard against language misdetection.

        Whisper can misdetect Indian-language audio -- as English,
        where it emits a romanized transliteration, or as some other
        language the translator has no mapping for. Either way the
        transcript would pass downstream untranslated and corrupt
        every later stage, so transcription is retried with
        PRIMARY_AUDIO_LANGUAGE forced.

        Returns the usual transcribe() dict plus a "warnings" list.
        """

        speech = self.transcribe(audio_path)

        detected = speech["language"]

        warnings = []

        misdetected_english = (
            detected == "en"
            and not looks_like_english(speech["transcript"])
        )

        untranslatable = (
            detected != "en"
            and detected not in LANGUAGE_MAP
        )

        if speech["transcript"].strip() and (
            misdetected_english or untranslatable
        ):

            reason = (
                "the transcript did not look like English"
                if misdetected_english
                else "the translator has no mapping for it"
            )

            logger.warning(
                "Detected language '%s' is unusable (%s). "
                "Retrying with forced language: %s",
                detected,
                reason,
                PRIMARY_AUDIO_LANGUAGE,
            )

            warnings.append(
                f"The audio was detected as '{detected}' but "
                f"{reason}, so transcription was retried in "
                f"'{PRIMARY_AUDIO_LANGUAGE}'."
            )

            speech = self.transcribe(
                audio_path,
                language=PRIMARY_AUDIO_LANGUAGE,
            )

        speech["warnings"] = warnings

        return speech

    def save_transcript(
        self,
        transcript: str,
        output_path: str,
    ):
        """
        Save the transcript to a text file.

        Parameters
        ----------
        transcript : str
            Transcript text.

        output_path : str
            Destination file path.
        """

        output_file = Path(output_path)

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:

            with open(
                output_file,
                "w",
                encoding="utf-8",
            ) as file:

                file.write(transcript)

            logger.info(
                "Transcript saved to %s",
                output_file,
            )

        except Exception:
            logger.exception("Failed to save transcript.")
            raise