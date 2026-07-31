import re
import spacy

from careinsight.medical_patterns import patterns


class MedicalExtractor:

    def __init__(self):

        self.nlp = spacy.load("en_core_web_sm")

        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe(
                "entity_ruler",
                before="ner",
            )
            ruler.add_patterns(patterns)

    def extract(self, text: str):

        doc = self.nlp(text)

        data = {
            "patient_name": None,
            "age": None,
            "symptoms": [],
            "conditions": [],
            "medications": [],
            "duration": None,
        }

        # ============================================
        # Patient Name (Regex Priority)
        # ============================================

        name = re.search(
            r"\bMy name is\s+([A-Z][a-zA-Z]*)",
            text,
            re.IGNORECASE,
        )

        if name:
            data["patient_name"] = name.group(1)

        # ============================================
        # spaCy PERSON Fallback
        # ============================================

        if data["patient_name"] is None:

            for ent in doc.ents:

                if ent.label_ == "PERSON":
                    data["patient_name"] = ent.text
                    break

        # ============================================
        # Disease Normalization
        # ============================================

        disease_map = {
            "blood pressure": "Hypertension",
            "high blood pressure": "Hypertension",
            "hypertension": "Hypertension",
            "diabetes": "Diabetes",
            "asthma": "Asthma",
        }

        # ============================================
        # Medical Entity Extraction
        # ============================================

        for ent in doc.ents:

            text_entity = ent.text.lower().strip()
            lemma_entity = ent.lemma_.lower().strip()

            # ---------- Symptoms ----------

            if ent.label_ == "SYMPTOM":

                symptom = lemma_entity

                if symptom not in [
                    s.lower()
                    for s in data["symptoms"]
                ]:
                    data["symptoms"].append(symptom)

            # ---------- Diseases ----------

            elif ent.label_ == "DISEASE":

                disease = disease_map.get(
                    text_entity,
                    ent.text.title(),
                )

                if disease not in data["conditions"]:
                    data["conditions"].append(disease)

            # ---------- Medications ----------

            elif ent.label_ == "MEDICATION":

                medicine = text_entity

                if medicine not in [
                    m.lower()
                    for m in data["medications"]
                ]:
                    data["medications"].append(medicine)

        # ============================================
        # Infer Hypertension from Medication
        # ============================================

        bp_medicines = {
            "blood pressure medicine",
            "bp medicine",
        }

        if any(
            med.lower() in bp_medicines
            for med in data["medications"]
        ):
            if "Hypertension" not in data["conditions"]:
                data["conditions"].append("Hypertension")

        # ============================================
        # Age
        # ============================================

        age = re.search(
            r"(\d+)\s*years?\s*old",
            text,
            re.IGNORECASE,
        )

        if age:
            data["age"] = int(age.group(1))

        # ============================================
        # Duration
        # ============================================

        duration = re.search(
            r"(\d+\s*(day|days|week|weeks|month|months))",
            text,
            re.IGNORECASE,
        )

        if duration:

            data["duration"] = duration.group(1)

        else:

            word_duration = re.search(
                r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\s+"
                r"(day|days|week|weeks|month|months)\b",
                text,
                re.IGNORECASE,
            )

            if word_duration:
                data["duration"] = word_duration.group(0)

        return data