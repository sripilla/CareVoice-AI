from pathlib import Path

import torch
from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio
from transformers import pipeline

from config import (
    DEFAULT_BEAM_SIZE,
    DEFAULT_CONDITION_ON_PREVIOUS_TEXT,
    DEFAULT_TEMPERATURE,
    DEFAULT_VAD_FILTER,
    SPECIALIST_ASR_MODELS,
    SPECIALIST_CHUNK_LENGTH_S,
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

        # Per-language fine-tuned models, loaded lazily on
        # first use and cached for the process lifetime.
        self._specialist_pipelines = {}

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

            # ----------------------------------------------
            # Specialist re-transcription
            # ----------------------------------------------
            #
            # The multilingual model is used for language
            # detection and as a fallback. For languages
            # with a fine-tuned Indic model available, the
            # audio is re-transcribed with that model, which
            # produces correctly spelled native-script text.
            # ----------------------------------------------

            if info.language in SPECIALIST_ASR_MODELS:

                specialist_text = self._transcribe_with_specialist(
                    audio_path,
                    info.language,
                )

                if specialist_text:
                    transcript_text = specialist_text

            logger.info("Transcription completed successfully.")

            return {
                "transcript": transcript_text,
                "language": info.language,
                "language_probability": info.language_probability,
            }

        except Exception:
            logger.exception("Audio transcription failed.")
            raise

    def _transcribe_with_specialist(
        self,
        audio_path: str,
        language: str,
    ) -> str:
        """
        Transcribe audio with a language-specific model.

        Any failure (download, load, or inference) is logged
        and an empty string is returned so the caller keeps
        the default multilingual transcript instead of
        failing the whole pipeline.

        Parameters
        ----------
        audio_path : str
            Path to the audio file.

        language : str
            Whisper language code (kn, te, hi, ...).

        Returns
        -------
        str
            Specialist transcript, or "" on failure.
        """

        try:

            asr = self._get_specialist_pipeline(language)

            # Decode with PyAV (same decoder Faster Whisper
            # uses) so no external ffmpeg binary is needed.
            audio = decode_audio(
                audio_path,
                sampling_rate=16000,
            )

            result = asr(
                {
                    "array": audio,
                    "sampling_rate": 16000,
                },
                generate_kwargs={
                    "language": language,
                    "task": "transcribe",
                },
            )

            specialist_text = result["text"].strip()

            logger.info(
                "Specialist transcription for '%s' "
                "completed successfully.",
                language,
            )

            return specialist_text

        except Exception:

            logger.exception(
                "Specialist transcription failed for '%s'. "
                "Falling back to the multilingual transcript.",
                language,
            )

            return ""

    def _get_specialist_pipeline(self, language: str):
        """
        Load (or fetch from cache) the fine-tuned ASR
        pipeline for a language.

        Parameters
        ----------
        language : str
            Whisper language code present in
            SPECIALIST_ASR_MODELS.

        Returns
        -------
        transformers.Pipeline
            Automatic speech recognition pipeline.
        """

        if language not in self._specialist_pipelines:

            model_name = SPECIALIST_ASR_MODELS[language]

            logger.info(
                "Loading specialist ASR model for '%s': %s",
                language,
                model_name,
            )

            self._specialist_pipelines[language] = pipeline(
                task="automatic-speech-recognition",
                model=model_name,
                chunk_length_s=SPECIALIST_CHUNK_LENGTH_S,
                device="cpu",
            )

            logger.info(
                "Specialist ASR model for '%s' loaded "
                "successfully.",
                language,
            )

        return self._specialist_pipelines[language]

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