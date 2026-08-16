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

    engine._save_report = MagicMock(
        return_value=1
    )

    # ------------------------------------------------------
    # Doctor-provided patient details
    # ------------------------------------------------------

    patient_details = {
        "patient_id": "P001",
        "patient_name": "Lakshmi",
        "age": 70,
        "blood_pressure": "140/90",
        "weight": 65,
        "blood_sugar": 150,
    }

    # ------------------------------------------------------
    # Execute
    # ------------------------------------------------------

    report = engine.process_audio(
        audio_path="dummy.wav",
        patient_details=patient_details,
    )

    # ------------------------------------------------------
    # Verify pipeline output
    # ------------------------------------------------------

    assert report["original_transcript"] == "నాకు జ్వరం ఉంది"

    assert report["detected_language"] == "te"

    assert report["english_transcript"] == "I have fever."

    assert report["summary"] == "Patient reports fever."

    assert report["patient"]["patient_id"] == "P001"

    assert report["patient"]["patient_name"] == "Lakshmi"

    assert report["patient"]["age"] == 70

    assert report["patient"]["blood_pressure"] == "140/90"

    assert report["patient"]["weight"] == 65

    assert report["patient"]["blood_sugar"] == 150

    assert report["patient"]["symptoms"] == ["fever"]

    assert report["patient"]["conditions"] == ["Diabetes"]

    assert report["patient"]["duration"] == "3 days"

    assert report["risk"]["risk_score"] == 5

    assert report["risk"]["risk_level"] == "High"

    assert report["clinical_report"] == "Clinical Report"

    assert report["consultation_id"] == 1

    # ------------------------------------------------------
    # Verify important pipeline calls
    # ------------------------------------------------------

    engine.transcriber.transcribe.assert_called_once_with(
        "dummy.wav"
    )

    engine.translator.translate.assert_called_once_with(
        "నాకు జ్వరం ఉంది",
        "te",
    )

    engine.summarizer.summarize_text.assert_called_once_with(
        "I have fever."
    )

    engine.extractor.extract.assert_called_once_with(
        "I have fever."
    )

    engine.risk_assessor.assess.assert_called_once_with(
        report["patient"]
    )

    engine._save_report.assert_called_once()