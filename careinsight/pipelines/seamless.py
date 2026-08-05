"""
SeamlessM4T v2: speech straight to English, no intermediate text.

Why this exists
---------------
The cascade produced this, from a patient saying "I have had a
headache for two days":

    Telugu speech
      -> ASR heard  రెండ్ రోల్   (not a word; "two days" mangled)
      -> NLLB read that as a name and wrote "the Red Roll"

NLLB had no way to know its input was corrupt, so it produced fluent
nonsense. Translating the audio directly removes the step where a
mis-spelt Telugu word can be re-interpreted as an unrelated English
one.
"""

from config import (
    DEVICE,
    DTYPE,
    LANGID_MODEL,
    SEAMLESS_LANGUAGE_MAP,
    SEAMLESS_MODEL,
    SEAMLESS_NATIVE_TRANSCRIPT,
)
from careinsight.pipelines.base import SpeechPipeline, SpeechResult
from utils.device import describe, resolve_device, resolve_dtype
from utils.logger import get_logger

logger = get_logger(__name__)

SAMPLE_RATE = 16000


class SeamlessPipeline(SpeechPipeline):
    """
    Direct speech-to-text translation.
    """

    label = "SeamlessM4T v2 (direct speech -> English)"

    def __init__(
        self,
        model_name: str = SEAMLESS_MODEL,
    ):

        import torch
        from transformers import (
            AutoProcessor,
            SeamlessM4Tv2ForSpeechToText,
        )

        self.torch = torch

        self.device = resolve_device(DEVICE)
        self.dtype = resolve_dtype(self.device, DTYPE)

        logger.info(
            "Loading %s on %s",
            model_name,
            describe(self.device, self.dtype),
        )

        try:

            self.processor = AutoProcessor.from_pretrained(
                model_name
            )

            self.model = (
                SeamlessM4Tv2ForSpeechToText.from_pretrained(
                    model_name,
                    dtype=self.dtype,
                )
                .to(self.device)
                .eval()
            )

        except Exception:

            logger.exception(
                "Failed to load SeamlessM4T. On Apple Silicon set "
                "PYTORCH_ENABLE_MPS_FALLBACK=1; if memory is tight "
                "try CAREVOICE_DTYPE=float16."
            )

            raise

        # SeamlessM4T reports no language ID of its own, and the
        # clinical report needs one. A tiny Whisper answers that in
        # about a second.
        self._langid = _LanguageDetector(LANGID_MODEL)

        logger.info("SeamlessM4T pipeline ready.")

    # ======================================================
    # Public API
    # ======================================================

    def to_english(self, audio_path: str) -> SpeechResult:

        warnings = []

        audio = _load_audio(audio_path)

        logger.info("Step 1: Language detection")

        language, probability = self._langid.detect(audio_path)

        logger.info("Step 2: Direct speech -> English")

        english = self._generate(audio, "eng")

        original = ""

        if SEAMLESS_NATIVE_TRANSCRIPT:

            source = SEAMLESS_LANGUAGE_MAP.get(language)

            if source is None:

                warnings.append(
                    f"'{language}' has no SeamlessM4T mapping, so the "
                    "original-language transcript was not produced. "
                    "The English translation is unaffected."
                )

            elif source == "eng":
                original = english

            else:
                logger.info(
                    "Step 3: Native transcript (%s)",
                    source,
                )
                original = self._generate(audio, source)

        if not english.strip():
            warnings.append(
                "No speech was detected in the audio."
            )

        return SpeechResult(
            english_transcript=english,
            original_transcript=original,
            detected_language=language,
            language_probability=probability,
            warnings=warnings,
        )

    # ======================================================
    # Helpers
    # ======================================================

    def _generate(self, audio, target_language: str) -> str:
        """
        Run one generation pass for a given target language.
        """

        inputs = self.processor(
            audios=audio,
            sampling_rate=SAMPLE_RATE,
            return_tensors="pt",
        )

        inputs = {
            key: (
                value.to(self.device, self.dtype)
                if value.is_floating_point()
                else value.to(self.device)
            )
            for key, value in inputs.items()
        }

        with self.torch.no_grad():
            generated = self.model.generate(
                **inputs,
                tgt_lang=target_language,
            )

        return self.processor.batch_decode(
            generated.cpu(),
            skip_special_tokens=True,
        )[0].strip()


class _LanguageDetector:
    """
    Whisper used only for its language identification.
    """

    def __init__(self, model_name: str):

        from faster_whisper import WhisperModel

        logger.info(
            "Loading language detector: Whisper %s",
            model_name,
        )

        # CTranslate2 has no Metal backend, so this always runs on
        # CPU. At "tiny" that costs about a second.
        self.model = WhisperModel(
            model_name,
            device="cpu",
            compute_type="int8",
        )

    def detect(self, audio_path: str):

        _, info = self.model.transcribe(
            audio_path,
            beam_size=1,
        )

        logger.info(
            "Detected language: %s (confidence %.2f)",
            info.language,
            info.language_probability,
        )

        return info.language, info.language_probability


def _load_audio(audio_path: str):
    """
    Decode any supported container to 16 kHz mono float32.

    Reuses faster-whisper's PyAV-backed decoder, so no ffmpeg binary
    or extra dependency is required.
    """

    from faster_whisper.audio import decode_audio

    return decode_audio(audio_path, sampling_rate=SAMPLE_RATE)
