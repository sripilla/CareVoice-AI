import re

from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
)

from config import (
    DEFAULT_TARGET_LANGUAGE,
    DEVICE,
    DTYPE,
    LANGUAGE_MAP,
    MAX_TRANSLATION_LENGTH,
    TRANSLATION_CHUNK_CHARS,
    TRANSLATION_MODEL,
)
from utils.device import describe, resolve_device, resolve_dtype
from utils.language import looks_like_english
from utils.logger import get_logger

logger = get_logger(__name__)


class Translator:
    """
    Multilingual Translation module using
    Facebook NLLB-200.

    Automatically translates supported
    Indian languages into English.
    """

    def __init__(
        self,
        model_name: str = TRANSLATION_MODEL,
    ):
        """
        Initialize the translation model.
        """

        self.model_name = model_name

        self.device = resolve_device(DEVICE)
        self.dtype = resolve_dtype(self.device, DTYPE)

        logger.info(
            "Loading translation model: %s on %s",
            self.model_name,
            describe(self.device, self.dtype),
        )

        try:

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name
            )

            self.model = (
                AutoModelForSeq2SeqLM.from_pretrained(
                    self.model_name,
                    dtype=self.dtype,
                )
                .to(self.device)
                .eval()
            )

            logger.info(
                "Translation model loaded successfully."
            )

        except Exception:

            logger.exception(
                "Failed to load translation model."
            )

            raise

    def translate(
        self,
        text: str,
        language: str,
        target_language: str = DEFAULT_TARGET_LANGUAGE,
    ) -> str:
        """
        Translate text into English.

        Parameters
        ----------
        text : str
            Original transcript.

        language : str
            Whisper detected language
            (te, kn, hi, en, ...).

        target_language : str
            Target language.

        Returns
        -------
        str
            The translated text.
        """

        return self.translate_with_meta(
            text,
            language,
            target_language,
        )["text"]

    def translate_with_meta(
        self,
        text: str,
        language: str,
        target_language: str = DEFAULT_TARGET_LANGUAGE,
    ) -> dict:
        """
        Translate text into English, reporting whether the
        translation actually happened.

        An unsupported source language degrades to passing the
        original transcript through with a warning rather than
        failing the whole pipeline -- a partially useful report
        beats no report at all.

        Returns
        -------
        dict
            {
                "text": str,
                "translated": bool,
                "warnings": list[str],
            }
        """

        if not text.strip():

            logger.warning(
                "Received empty transcript."
            )

            return {
                "text": "",
                "translated": False,
                "warnings": [
                    "No speech was detected in the audio."
                ],
            }

        # --------------------------------------------------
        # English does not require translation
        # --------------------------------------------------

        if language == "en":

            warnings = []

            if not looks_like_english(text):

                logger.warning(
                    "Language reported as English but the text "
                    "does not look like English. It may be a "
                    "romanized transliteration."
                )

                warnings.append(
                    "The transcript was reported as English but "
                    "does not look like English (possibly a "
                    "romanized transliteration), so the summary, "
                    "extracted entities and risk score are "
                    "unreliable."
                )

            else:

                logger.info(
                    "Input language is English. "
                    "Skipping translation."
                )

            return {
                "text": text,
                "translated": False,
                "warnings": warnings,
            }

        # --------------------------------------------------
        # Unsupported language: degrade, do not fail
        # --------------------------------------------------

        if language not in LANGUAGE_MAP:

            logger.warning(
                "Unsupported language '%s'. Passing the "
                "transcript through untranslated.",
                language,
            )

            return {
                "text": text,
                "translated": False,
                "warnings": [
                    f"'{language}' is not a supported source "
                    "language. The transcript was not "
                    "translated, so the summary, extracted "
                    "entities and risk score are unreliable."
                ],
            }

        source_language = LANGUAGE_MAP[language]

        logger.info(
            "Translating %s -> %s",
            source_language,
            target_language,
        )

        try:

            self.tokenizer.src_lang = source_language

            chunks = self._chunk(text)

            logger.info(
                "Translating %d chunk(s).",
                len(chunks),
            )

            translated_chunks = [
                self._translate_chunk(
                    chunk,
                    target_language,
                )
                for chunk in chunks
            ]

            logger.info(
                "Translation completed successfully."
            )

            return {
                "text": " ".join(translated_chunks).strip(),
                "translated": True,
                "warnings": [],
            }

        except Exception:

            logger.exception(
                "Translation failed."
            )

            raise

    # ======================================================
    # Helper Methods
    # ======================================================

    def _translate_chunk(
        self,
        chunk: str,
        target_language: str,
    ) -> str:
        """
        Translate a single chunk that fits the model window.
        """

        import torch

        inputs = self.tokenizer(
            chunk,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_TRANSLATION_LENGTH,
        ).to(self.device)

        with torch.no_grad():
            generated_tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=(
                    self.tokenizer.convert_tokens_to_ids(
                        target_language
                    )
                ),
                max_length=MAX_TRANSLATION_LENGTH,
            )

        return self.tokenizer.batch_decode(
            generated_tokens.cpu(),
            skip_special_tokens=True,
        )[0]

    def _chunk(
        self,
        text: str,
    ) -> list[str]:
        """
        Split a transcript into sentence-aligned chunks that fit
        inside the model's input window.

        NLLB silently truncates anything longer, which would drop
        most of a real consultation.
        """

        text = text.strip()

        if len(text) <= TRANSLATION_CHUNK_CHARS:
            return [text]

        # Latin full stops plus the Devanagari danda / double danda.
        sentences = [
            sentence.strip()
            for sentence in re.split(
                r"(?<=[.!?।॥])\s+",
                text,
            )
            if sentence.strip()
        ]

        chunks: list[str] = []
        current = ""

        for sentence in sentences:

            # A single sentence longer than the window has no
            # safe split point; send it on its own and let the
            # tokenizer truncate that one sentence.

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