from pathlib import Path

import torch
from faster_whisper import WhisperModel

from config import (
    DEFAULT_BEAM_SIZE,
    DEFAULT_CONDITION_ON_PREVIOUS_TEXT,
    DEFAULT_TEMPERATURE,
    DEFAULT_VAD_FILTER,
    WHISPER_MODEL,
)
from utils.logger import get_logger

logger = get_logger(__name__)


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

        # --------------------------------------------------
        # Device Configuration
        # --------------------------------------------------
        #
        # NOTE:
        # Although Apple Silicon (MPS) may be available,
        # Faster Whisper is intentionally run on CPU because
        # it provides more stable and predictable inference
        # for this project.
        #
        # If GPU support is required later, only this section
        # needs to be modified.
        # --------------------------------------------------

        self.device = "cpu"
        self.compute_type = "int8"

        if torch.backends.mps.is_available():
            logger.info(
                "Apple Silicon detected. "
                "Using CPU for stable Faster Whisper inference."
            )
        else:
            logger.info("CPU execution mode enabled.")

        logger.info("Loading Faster Whisper model: %s", model_name)

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
                condition_on_previous_text=DEFAULT_CONDITION_ON_PREVIOUS_TEXT,
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