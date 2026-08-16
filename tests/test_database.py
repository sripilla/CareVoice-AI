from database.database import DatabaseManager


def sample_report():
    """
    Return a sample consultation report for testing.
    """

    return {
        "original_transcript": "నాకు జ్వరం మరియు దగ్గు ఉంది.",
        "detected_language": "te",
        "english_transcript": (
            "I have fever and cough."
        ),
        "summary": (
            "Patient reports fever and cough."
        ),
        "patient": {
            "patient_id": "P001",
            "patient_name": "Lakshmi",
            "age": 70,
            "blood_pressure": "140/90",
            "weight": 65.5,
            "blood_sugar": 150.0,
            "symptoms": [
                "fever",
                "cough",
            ],
            "conditions": [
                "Diabetes",
            ],
            "medications": [
                "Paracetamol",
            ],
            "duration": "3 days",
        },
        "risk": {
            "risk_score": 5,
            "risk_level": "High",
        },
        "clinical_report": (
            "Clinical report for Lakshmi."
        ),
    }


def sample_prescription(consultation_id: int):
    """
    Return a sample prescription for testing.
    """

    return {
        "consultation_id": consultation_id,
        "english_prescription": (
            "Paracetamol 500 mg twice daily."
        ),
        "translated_prescription": (
            "పారాసిటమాల్ 500 మి.గ్రా రోజుకు రెండుసార్లు."
        ),
        "english_guidelines": (
            "Drink plenty of water and take rest."
        ),
        "translated_guidelines": (
            "ఎక్కువ నీరు తాగండి మరియు విశ్రాంతి తీసుకోండి."
        ),
        "patient_language": "te",
    }


def test_empty_database(tmp_path):
    """
    Verify that a newly created database contains
    no consultations.
    """

    db_file = tmp_path / "test.db"

    db = DatabaseManager(db_path=str(db_file))

    assert db.get_consultation_count() == 0

    assert (
        db.get_patient_by_id("P001")
        is None
    )

    db.close()


def test_save_and_get_patient(tmp_path):
    """
    Verify that a patient can be saved and retrieved.
    """

    db_file = tmp_path / "test.db"

    db = DatabaseManager(db_path=str(db_file))

    patient = sample_report()["patient"]

    db.save_patient(patient)

    saved_patient = db.get_patient_by_id(
        "P001"
    )

    assert saved_patient is not None

    assert saved_patient["patient_id"] == "P001"

    assert saved_patient["patient_name"] == "Lakshmi"

    assert saved_patient["age"] == 70

    db.close()


def test_save_consultation(tmp_path):
    """
    Verify that a consultation is saved successfully.
    """

    db_file = tmp_path / "test.db"

    db = DatabaseManager(db_path=str(db_file))

    consultation_id = db.save_consultation(
        sample_report()
    )

    assert consultation_id == 1

    assert db.get_consultation_count() == 1

    db.close()


def test_get_consultation_by_id(tmp_path):
    """
    Verify that a saved consultation can be retrieved
    with its consultation ID.
    """

    db_file = tmp_path / "test.db"

    db = DatabaseManager(db_path=str(db_file))

    consultation_id = db.save_consultation(
        sample_report()
    )

    consultation = db.get_consultation_by_id(
        consultation_id
    )

    assert consultation is not None

    assert (
        consultation["consultation_id"]
        == consultation_id
    )

    assert consultation["patient_id"] == "P001"

    assert consultation["detected_language"] == "te"

    assert (
        consultation["english_transcript"]
        == "I have fever and cough."
    )

    assert consultation["risk_score"] == 5

    assert consultation["risk_level"] == "High"

    db.close()


def test_consultation_measurements_are_saved(tmp_path):
    """
    Verify that optional clinical measurements are
    stored correctly.
    """

    db_file = tmp_path / "test.db"

    db = DatabaseManager(db_path=str(db_file))

    consultation_id = db.save_consultation(
        sample_report()
    )

    consultation = db.get_consultation_by_id(
        consultation_id
    )

    assert (
        consultation["blood_pressure"]
        == "140/90"
    )

    assert consultation["weight"] == 65.5

    assert consultation["blood_sugar"] == 150.0

    db.close()


def test_get_consultations_by_patient(tmp_path):
    """
    Verify that all consultations belonging to a patient
    can be retrieved.
    """

    db_file = tmp_path / "test.db"

    db = DatabaseManager(db_path=str(db_file))

    first_id = db.save_consultation(
        sample_report()
    )

    second_report = sample_report()

    second_report["summary"] = (
        "Patient reports improved symptoms."
    )

    second_id = db.save_consultation(
        second_report
    )

    consultations = (
        db.get_consultations_by_patient_id(
            "P001"
        )
    )

    assert len(consultations) == 2

    assert consultations[0]["consultation_id"] == second_id

    assert consultations[1]["consultation_id"] == first_id

    db.close()


def test_patient_is_updated_on_new_consultation(tmp_path):
    """
    Verify that saving another consultation for the same
    patient updates the patient record instead of creating
    a duplicate patient.
    """

    db_file = tmp_path / "test.db"

    db = DatabaseManager(db_path=str(db_file))

    db.save_consultation(
        sample_report()
    )

    updated_report = sample_report()

    updated_report["patient"]["patient_name"] = (
        "Lakshmi Devi"
    )

    updated_report["patient"]["age"] = 71

    db.save_consultation(updated_report)

    patient = db.get_patient_by_id("P001")

    assert patient["patient_name"] == "Lakshmi Devi"

    assert patient["age"] == 71

    assert db.get_consultation_count() == 2

    db.close()


def test_save_and_get_prescription(tmp_path):
    """
    Verify that a prescription can be saved and retrieved
    for a consultation.
    """

    db_file = tmp_path / "test.db"

    db = DatabaseManager(db_path=str(db_file))

    consultation_id = db.save_consultation(
        sample_report()
    )

    prescription_id = db.save_prescription(
        sample_prescription(consultation_id)
    )

    assert prescription_id == 1

    prescription = (
        db.get_prescription_by_consultation_id(
            consultation_id
        )
    )

    assert prescription is not None

    assert (
        prescription["consultation_id"]
        == consultation_id
    )

    assert prescription["patient_language"] == "te"

    assert (
        prescription["english_prescription"]
        == "Paracetamol 500 mg twice daily."
    )

    assert (
        prescription["english_guidelines"]
        == "Drink plenty of water and take rest."
    )

    db.close()


def test_delete_consultation(tmp_path):
    """
    Verify that deleting a consultation removes it from
    the database.
    """

    db_file = tmp_path / "test.db"

    db = DatabaseManager(db_path=str(db_file))

    consultation_id = db.save_consultation(
        sample_report()
    )

    assert db.get_consultation_count() == 1

    db.delete_consultation(consultation_id)

    assert db.get_consultation_count() == 0

    assert (
        db.get_consultation_by_id(consultation_id)
        is None
    )

    db.close()