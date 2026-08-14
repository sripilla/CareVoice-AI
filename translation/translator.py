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

    Supports:

    - Patient language → English
    - English → Patient language
    """

    ENGLISH_LANGUAGE_CODE = "eng_Latn"

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
        Translate text from a Whisper detected language
        into the target language.

        This is used by the existing consultation workflow.

        Parameters
        ----------
        text : str
            Original transcript.

        language : str
            Whisper detected language code
            (te, kn, hi, en, ...).

        target_language : str
            NLLB target language code.
        """

        if not text.strip():

            logger.warning(
                "Received empty text for translation."
            )

            return ""

        # --------------------------------------------------
        # English input with English target
        # --------------------------------------------------

        if (
            language == "en"
            and target_language == self.ENGLISH_LANGUAGE_CODE
        ):

            logger.info(
                "Input is already English. "
                "Skipping translation."
            )

            return text

        # --------------------------------------------------
        # Validate supported source language
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

        return self._translate(
            text=text,
            source_language=source_language,
            target_language=target_language,
        )

    def translate_from_english(
        self,
        text: str,
        target_language: str,
    ) -> str:
        """
        Translate English text into the patient's
        detected language.

        Parameters
        ----------
        text : str
            English prescription or doctor guidelines.

        target_language : str
            Whisper detected patient language code
            (te, kn, hi, en, ...).
        """

        if not text.strip():

            logger.warning(
                "Received empty English text for translation."
            )

            return ""

        # --------------------------------------------------
        # English patient
        # --------------------------------------------------

        if target_language == "en":

            logger.info(
                "Patient language is English. "
                "Skipping translation."
            )

            return text

        # --------------------------------------------------
        # Validate supported patient language
        # --------------------------------------------------

        if target_language not in LANGUAGE_MAP:

            logger.error(
                "Unsupported target language: %s",
                target_language,
            )

            raise ValueError(
                f"Unsupported language: {target_language}"
            )

        nllb_target_language = LANGUAGE_MAP[
            target_language
        ]

        return self._translate(
            text=text,
            source_language=self.ENGLISH_LANGUAGE_CODE,
            target_language=nllb_target_language,
        )

    def _translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> str:
        """
        Perform translation using NLLB.

        Parameters
        ----------
        text : str
            Text to translate.

        source_language : str
            NLLB source language code.

        target_language : str
            NLLB target language code.
        """

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
                forced_bos_token_id=(
                    self.tokenizer.convert_tokens_to_ids(
                        target_language
                    )
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