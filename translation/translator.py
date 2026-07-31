from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


class Translator:

    def __init__(self):

        print("Loading Translation Model...")

        self.model_name = "facebook/nllb-200-distilled-600M"

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)

        print("Translation Model Loaded!")

    def translate(
        self,
        text,
        src_lang="tel_Telu",
        tgt_lang="eng_Latn",
    ):

        self.tokenizer.src_lang = src_lang

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
        )

        generated_tokens = self.model.generate(
            **inputs,
            forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(tgt_lang),
            max_length=512,
        )

        translated = self.tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True,
        )

        return translated[0]