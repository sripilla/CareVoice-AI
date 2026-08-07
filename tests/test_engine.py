from unittest.mock import MagicMock

from careinsight.engine import CareVoiceEngine


def test_process_audio_pipeline():

    engine = CareVoiceEngine()

    # ------------------------------------------------------
    # Mock all pipeline components
    # ------------------------------------------------------

    engine.transcriber.transcribe = MagicMock(
        return_value={
            "transcript": "నాకు జ్వరం ఉంది",
            "language": "te",
        }
    )

    engine.translator.translate = MagicMock(
        return_value="I have fever."
    )

    engine.summarizer.summarize_text = MagicMock(
        return_value="Patient reports fever."
    )

    engine.extractor.extract = MagicMock(
        return_value={
            "patient_name": "Lakshmi",
            "age": 70,
            "symptoms": ["fever"],
            "conditions": ["Diabetes"],
            "medications": [],
            "duration": "3 days",
        }
    )

    engine.risk_assessor.assess = MagicMock(
        return_value={
            "risk_score": 5,
            "risk_level": "High",
        }
    )

    engine.report_generator.generate = MagicMock(
        return_value="Clinical Report"
    )

    engine.database.save_report = MagicMock()

    # ------------------------------------------------------
    # Execute
    # ------------------------------------------------------

    report = engine.process_audio("dummy.wav")

    # ------------------------------------------------------
    # Assertions
    # ------------------------------------------------------

    assert report["original_transcript"] == "నాకు జ్వరం ఉంది"

    assert report["detected_language"] == "te"

    assert report["english_transcript"] == "I have fever."

    assert report["summary"] == "Patient reports fever."

    assert report["patient"]["patient_name"] == "Lakshmi"

    assert report["risk"]["risk_level"] == "High"

    assert report["clinical_report"] == "Clinical Report"

    engine.database.save_report.assert_called_once()