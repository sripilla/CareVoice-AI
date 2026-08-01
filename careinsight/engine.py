from speech.transcriber import SpeechTranscriber
from translation.translator import Translator
from careinsight.summarizer import MedicalSummarizer
from careinsight.extractor import MedicalExtractor
from careinsight.risk_assessor import RiskAssessor
from careinsight.report_generator import ReportGenerator
from database.database import DatabaseManager


class CareVoiceEngine:

    def __init__(self):

        print("\n========== Initializing CareVoice AI ==========")

        self.transcriber = SpeechTranscriber(
            model_name="large-v3"
        )

        self.translator = Translator()

        self.summarizer = MedicalSummarizer()

        self.extractor = MedicalExtractor()

        self.risk_assessor = RiskAssessor()

        self.report_generator = ReportGenerator()

        self.report_generator = ReportGenerator()

        self.database = DatabaseManager()

        print("\nAll modules loaded successfully.\n")



    def process_audio(self, audio_path: str):

        # =====================================================
        # STEP 1 : Speech Recognition
        # =====================================================

        print("========== STEP 1 : Speech Recognition ==========\n")

        telugu_text = self.transcriber.transcribe(audio_path)

        # =====================================================
        # STEP 2 : Translation
        # =====================================================

        print("\n========== STEP 2 : Translation ==========\n")

        english_text = self.translator.translate(
            telugu_text
        )

        print(english_text)

        # =====================================================
        # STEP 3 : Summarization
        # =====================================================

        print("\n========== STEP 3 : Summarization ==========\n")

        summary = self.summarizer.summarize_text(
            english_text
        )

        print(summary)

        # =====================================================
        # STEP 4 : Medical Information Extraction
        # =====================================================

        print(
            "\n========== STEP 4 : Medical Entity Extraction ==========\n"
        )

        patient = self.extractor.extract(
            english_text
        )

        for key, value in patient.items():
            print(f"{key}: {value}")

        # =====================================================
        # STEP 5 : Risk Assessment
        # =====================================================

        print("\n========== STEP 5 : Risk Assessment ==========\n")

        risk = self.risk_assessor.assess(
            patient
        )

        print(risk)

        # =====================================================
        # STEP 6 : Clinical Report Generation
        # =====================================================

        print(
            "\n========== STEP 6 : Clinical Report Generation ==========\n"
        )

        clinical_report = self.report_generator.generate(
            summary=summary,
            patient=patient,
            risk=risk,
        )

        # =====================================================
        # Final Output
        # =====================================================


        report = {
            "telugu_transcript": telugu_text,
            "english_transcript": english_text,
            "summary": summary,
            "patient": patient,
            "risk": risk,
            "clinical_report": clinical_report,
        }

        self.database.save_report(report)

        return report