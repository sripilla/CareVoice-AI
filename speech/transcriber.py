from pathlib import Path

from faster_whisper import WhisperModel

from config import (
    DEFAULT_BEAM_SIZE,
    DEFAULT_CONDITION_ON_PREVIOUS_TEXT,
    DEFAULT_TEMPERATURE,
    DEFAULT_VAD_FILTER,
    WHISPER_COMPUTE_TYPE,
    WHISPER_DEVICE,
    WHISPER_MODEL,
)
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

    def transcribe(self, audio_path: str) -> dict:
        """
        Transcribe an audio file.

        Parameters
        ----------
        audio_path : str
            Path to the audio file.

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

        try:

            segments, info = self.model.transcribe(
                audio_path,
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