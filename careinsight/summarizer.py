import re

from transformers import AutoTokenizer
from transformers import AutoModelForSeq2SeqLM


class MedicalSummarizer:

    def __init__(self):

        print("Loading BART Summarizer...")

        self.model_name = "facebook/bart-large-cnn"

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name
        )

        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_name
        )

        print("BART Loaded Successfully!")

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

        unwanted_phrases = [
            "during the appendix",
            "I drink only coughing",
            "I am drinking rum",
        ]

        for phrase in unwanted_phrases:

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

        print("\n========== CLEANED TEXT ==========\n")
        print(cleaned_text)

        inputs = self.tokenizer(
            cleaned_text,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
        )

        summary_ids = self.model.generate(
            **inputs,
            max_length=80,
            min_length=30,
            num_beams=4,
            early_stopping=True,
        )

        summary = self.tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True,
        )

        return summary