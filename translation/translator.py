import re

from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
)

from config import (
    DEFAULT_TARGET_LANGUAGE,
    LANGUAGE_MAP,
    MAX_TRANSLATION_LENGTH,
    TRANSLATION_CHUNK_MAX_WORDS,
    TRANSLATION_MODEL,
)
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

        logger.info(
            "Loading translation model: %s",
            self.model_name,
        )

        try:

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name
            )

            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name
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
        """

        if not text.strip():

            logger.warning(
                "Received empty transcript."
            )

            return ""

        # --------------------------------------------------
        # English does not require translation
        # --------------------------------------------------

        if language == "en":

            logger.info(
                "Input language is English. "
                "Skipping translation."
            )

            return text

        # --------------------------------------------------
        # Validate supported language
        # --------------------------------------------------

        if language not in LANGUAGE_MAP:

            logger.error(
                "Unsupported language: %s",
                language,
            )

            raise ValueError(
                f"Unsupported language: {language}"
            )

        source_language = LANGUAGE_MAP[language]

        logger.info(
            "Translating %s → %s",
            source_language,
            target_language,
        )

        # --------------------------------------------------
        # Translate chunk by chunk
        # --------------------------------------------------
        #
        # NLLB is a sentence-level model. Feeding it a long
        # unpunctuated transcript in a single pass makes it
        # silently drop clauses, so the transcript is split
        # into sentence-sized chunks and each chunk is
        # translated independently.
        # --------------------------------------------------

        chunks = self._split_into_chunks(text)

        logger.info(
            "Translating %d chunk(s).",
            len(chunks),
        )

        try:

            self.tokenizer.src_lang = source_language

            translated_chunks = []

            for chunk in chunks:

                inputs = self.tokenizer(
                    chunk,
                    return_tensors="pt",
                )

                generated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(
                        target_language
                    ),
                    max_length=MAX_TRANSLATION_LENGTH,
                )

                translated = self.tokenizer.batch_decode(
                    generated_tokens,
                    skip_special_tokens=True,
                )

                translated_chunks.append(
                    translated[0].strip()
                )

            logger.info(
                "Translation completed successfully."
            )

            return " ".join(translated_chunks)

        except Exception:

            logger.exception(
                "Translation failed."
            )

            raise

    @staticmethod
    def _split_into_chunks(
        text: str,
        max_words: int = TRANSLATION_CHUNK_MAX_WORDS,
    ) -> list:
        """
        Split a transcript into sentence-sized chunks.

        The text is first split on sentence-ending
        punctuation (including the Indic danda). Whisper
        often emits Indic text with no punctuation at all,
        so any sentence still longer than ``max_words`` is
        split further into fixed-size word chunks.

        Parameters
        ----------
        text : str
            Transcript text.

        max_words : int
            Maximum words per chunk.

        Returns
        -------
        list
            Non-empty text chunks in original order.
        """

        sentences = re.split(
            r"(?<=[.!?।؟])\s+",
            text.strip(),
        )

        chunks = []

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            words = sentence.split()

            if len(words) <= max_words:
                chunks.append(sentence)
                continue

            for start in range(0, len(words), max_words):
                chunks.append(
                    " ".join(words[start:start + max_words])
                )

        return chunks