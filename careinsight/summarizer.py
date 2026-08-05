import re

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from config import (
    DEVICE,
    DTYPE,
    SUMMARIZER_MODEL,
    SUMMARY_MAX_INPUT_LENGTH,
    SUMMARY_MAX_LENGTH,
    SUMMARY_MIN_LENGTH,
    SUMMARY_NUM_BEAMS,
    UNWANTED_TRANSLATION_PHRASES,
)
from utils.device import describe, resolve_device, resolve_dtype
from utils.logger import get_logger

logger = get_logger(__name__)


class MedicalSummarizer:
    """
    Abstractive summarization of the translated consultation
    using BART.
    """

    def __init__(
        self,
        model_name: str = SUMMARIZER_MODEL,
    ):
        """
        Initialize the summarization model.
        """

        self.model_name = model_name

        self.device = resolve_device(DEVICE)
        self.dtype = resolve_dtype(self.device, DTYPE)

        logger.info(
            "Loading summarization model: %s on %s",
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
                "Summarization model loaded successfully."
            )

        except Exception:

            logger.exception(
                "Failed to load summarization model."
            )

            raise

    def clean_text(self, text: str) -> str:
        """
        Clean translated text before summarization.
        """

        # ==========================================
        # Normalize whitespace
        # ==========================================

        text = re.sub(r"\s+", " ", text).strip()

        # ==========================================
        # Remove repeated "My name is ..."
        # Example:
        # My name is Lakshmi My name is Vishnu
        # ->
        # My name is Lakshmi
        # ==========================================

        text = re.sub(
            r"(My name is\s+[A-Za-z]+)(\s+My name is\s+[A-Za-z]+)+",
            r"\1",
            text,
            flags=re.IGNORECASE,
        )

        # ==========================================
        # Remove common translation artifacts
        # ==========================================

        for phrase in UNWANTED_TRANSLATION_PHRASES:

            text = re.sub(
                re.escape(phrase),
                "",
                text,
                flags=re.IGNORECASE,
            )

        # ==========================================
        # Remove duplicate consecutive words
        # Example:
        # cough cough
        # ->
        # cough
        # ==========================================

        text = re.sub(
            r"\b(\w+)(\s+\1)+\b",
            r"\1",
            text,
            flags=re.IGNORECASE,
        )

        # ==========================================
        # Normalize punctuation and whitespace
        # ==========================================

        text = re.sub(r"\s+", " ", text)

        text = re.sub(
            r"\s+([.,!?])",
            r"\1",
            text,
        )

        return text.strip()

    def summarize_text(self, text: str) -> str:
        """
        Generate a clinical summary using BART.
        """

        cleaned_text = self.clean_text(text)

        if not cleaned_text:

            logger.warning(
                "Received empty text for summarization."
            )

            return ""

        logger.debug(
            "Cleaned text for summarization: %s",
            cleaned_text,
        )

        inputs = self.tokenizer(
            cleaned_text,
            return_tensors="pt",
            truncation=True,
            max_length=SUMMARY_MAX_INPUT_LENGTH,
        )

        input_length = int(inputs["input_ids"].shape[1])

        inputs = inputs.to(self.device)

        # --------------------------------------------------
        # A short consultation carries less information than
        # SUMMARY_MIN_LENGTH tokens. Forcing BART to reach that
        # floor makes it pad the output with invented content,
        # so return the cleaned transcript instead -- at that
        # length it already is the summary.
        # --------------------------------------------------

        if input_length <= SUMMARY_MIN_LENGTH:

            logger.info(
                "Transcript is shorter than the summary floor "
                "(%d tokens); returning it unsummarized.",
                input_length,
            )

            return cleaned_text

        max_length = min(SUMMARY_MAX_LENGTH, input_length)

        min_length = min(SUMMARY_MIN_LENGTH, max_length - 1)

        summary_ids = self.model.generate(
            **inputs,
            max_length=max_length,
            min_length=min_length,
            num_beams=SUMMARY_NUM_BEAMS,
            early_stopping=True,
        )

        summary = self.tokenizer.decode(
            summary_ids[0].cpu(),
            skip_special_tokens=True,
        )

        logger.info("Clinical summary generated.")

        return summary.strip()
