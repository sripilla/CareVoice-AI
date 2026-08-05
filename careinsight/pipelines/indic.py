"""
Whisper for speech, IndicTrans2 for translation.

Still a cascade, so it inherits the compounding-error weakness, but
it replaces NLLB with a translator built specifically for the 22
scheduled Indian languages. Useful as the middle option and as
evidence for how much of the failure is translation versus ASR.

IndicTrans2 is a *gated* Hugging Face repo. Accept the terms on the
model page while logged in, then export HF_TOKEN.
"""

from config import (
    DEVICE,
    DTYPE,
    INDICTRANS2_LANGUAGE_MAP,
    INDICTRANS2_MODEL,
    TRANSLATION_CHUNK_CHARS,
)
from careinsight.pipelines.base import SpeechPipeline, SpeechResult
from speech.transcriber import SpeechTranscriber
from utils.device import describe, resolve_device, resolve_dtype
from utils.logger import get_logger

logger = get_logger(__name__)

GATED_HELP = (
    "IndicTrans2 is a gated Hugging Face repo. Visit "
    "https://huggingface.co/ai4bharat/indictrans2-indic-en-dist-200M "
    "while signed in, accept the terms, then set HF_TOKEN in your "
    "environment."
)


class IndicPipeline(SpeechPipeline):
    """
    Speech -> native transcript -> English via IndicTrans2.
    """

    label = "Whisper -> IndicTrans2"

    def __init__(
        self,
        model_name: str = INDICTRANS2_MODEL,
    ):

        import torch
        from transformers import (
            AutoModelForSeq2SeqLM,
            AutoTokenizer,
        )

        self.torch = torch

        self.transcriber = SpeechTranscriber()

        self.device = resolve_device(DEVICE)
        self.dtype = resolve_dtype(self.device, DTYPE)

        logger.info(
            "Loading %s on %s",
            model_name,
            describe(self.device, self.dtype),
        )

        try:

            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True,
            )

            self.model = (
                AutoModelForSeq2SeqLM.from_pretrained(
                    model_name,
                    trust_remote_code=True,
                    dtype=self.dtype,
                )
                .to(self.device)
                .eval()
            )

        except OSError as error:

            if "gated" in str(error).lower() or "401" in str(error):
                logger.error(GATED_HELP)

            raise

        # The official preprocessor normalises scripts and masks
        # entities before translation. It measurably improves output,
        # so warn rather than silently doing without.
        self.processor = _load_indic_processor()

        logger.info("IndicTrans2 pipeline ready.")

    # ======================================================
    # Public API
    # ======================================================

    def to_english(self, audio_path: str) -> SpeechResult:

        logger.info("Step 1: Speech Recognition")

        speech = self.transcriber.transcribe(audio_path)

        transcript = speech["transcript"]
        language = speech["language"]

        warnings = []

        if not transcript.strip():

            return SpeechResult(
                english_transcript="",
                original_transcript="",
                detected_language=language,
                language_probability=speech[
                    "language_probability"
                ],
                warnings=["No speech was detected in the audio."],
            )

        if language == "en":
            english = transcript

        elif language not in INDICTRANS2_LANGUAGE_MAP:

            warnings.append(
                f"'{language}' is not supported by IndicTrans2. The "
                "transcript was not translated, so the summary, "
                "extracted entities and risk score are unreliable."
            )

            english = transcript

        else:

            logger.info("Step 2: Translation (IndicTrans2)")

            english = self._translate(
                transcript,
                INDICTRANS2_LANGUAGE_MAP[language],
            )

        return SpeechResult(
            english_transcript=english,
            original_transcript=transcript,
            detected_language=language,
            language_probability=speech["language_probability"],
            warnings=warnings,
        )

    # ======================================================
    # Helpers
    # ======================================================

    def _translate(self, text: str, source_language: str) -> str:

        chunks = _chunk(text)

        logger.info("Translating %d chunk(s).", len(chunks))

        return " ".join(
            self._translate_chunk(chunk, source_language)
            for chunk in chunks
        ).strip()

    def _translate_chunk(
        self,
        chunk: str,
        source_language: str,
    ) -> str:

        target = "eng_Latn"

        if self.processor is not None:

            prepared = self.processor.preprocess_batch(
                [chunk],
                src_lang=source_language,
                tgt_lang=target,
            )

        else:
            prepared = [f"{source_language} {target} {chunk}"]

        inputs = self.tokenizer(
            prepared,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=256,
        ).to(self.device)

        with self.torch.no_grad():
            generated = self.model.generate(
                **inputs,
                max_length=256,
                num_beams=5,
            )

        decoded = self.tokenizer.batch_decode(
            generated.cpu(),
            skip_special_tokens=True,
        )

        if self.processor is not None:
            decoded = self.processor.postprocess_batch(
                decoded,
                lang=target,
            )

        return decoded[0]


def _load_indic_processor():
    """
    Return IndicTransToolkit's processor, or None with a warning.
    """

    try:
        from IndicTransToolkit import IndicProcessor

        return IndicProcessor(inference=True)

    except ImportError:

        logger.warning(
            "IndicTransToolkit is not installed; falling back to raw "
            "language tags. Translation quality will be lower than "
            "IndicTrans2's published numbers. Install with: "
            "pip install IndicTransToolkit"
        )

        return None


def _chunk(text: str) -> list:
    """
    Split on sentence boundaries to stay inside the model window.
    """

    import re

    text = text.strip()

    if len(text) <= TRANSLATION_CHUNK_CHARS:
        return [text]

    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?।॥])\s+", text)
        if sentence.strip()
    ]

    chunks = []
    current = ""

    for sentence in sentences:

        if len(sentence) > TRANSLATION_CHUNK_CHARS:

            if current:
                chunks.append(current)
                current = ""

            chunks.append(sentence)
            continue

        candidate = (
            f"{current} {sentence}".strip()
            if current
            else sentence
        )

        if len(candidate) > TRANSLATION_CHUNK_CHARS:
            chunks.append(current)
            current = sentence
        else:
            current = candidate

    if current:
        chunks.append(current)

    return chunks
