from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
)

from config import (
    DEFAULT_TARGET_LANGUAGE,
    LANGUAGE_MAP,
    MAX_TRANSLATION_LENGTH,
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

        try:

            self.tokenizer.src_lang = source_language

            inputs = self.tokenizer(
                text,
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

            logger.info(
                "Translation completed successfully."
            )

            return translated[0]

        except Exception:

            logger.exception(
                "Translation failed."
            )

            raise