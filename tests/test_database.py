from database.database import DatabaseManager


def sample_report():
    return {
        "summary": "Patient reports fever.",

        "patient": {
            "patient_name": "Lakshmi",
            "age": 70,
            "symptoms": ["fever"],
            "conditions": ["Diabetes"],
            "medications": ["Paracetamol"],
            "duration": "3 days",
        },

        "risk": {
            "risk_score": 5,
            "risk_level": "High",
        },

        "clinical_report": "Clinical Report",
    }


def test_save_report(tmp_path):
    """
    Verify that a clinical report is saved successfully.
    """

    db_file = tmp_path / "test.db"

    db = DatabaseManager(db_path=str(db_file))

    db.save_report(sample_report())

    assert db.get_report_count() == 1

    db.close()


def test_get_report_by_id(tmp_path):
    """
    Verify that a saved report can be retrieved.
    """

    db_file = tmp_path / "test.db"

    db = DatabaseManager(db_path=str(db_file))

    db.save_report(sample_report())

    report = db.get_report_by_id(1)

    assert report["patient_name"] == "Lakshmi"

    assert report["risk_level"] == "High"

    db.close()


def test_delete_report(tmp_path):
    """
    Verify that deleting a report removes it from the database.
    """

    db_file = tmp_path / "test.db"

    db = DatabaseManager(db_path=str(db_file))

    db.save_report(sample_report())

    assert db.get_report_count() == 1

    db.delete_report(1)

    assert db.get_report_count() == 0

    db.close()


def test_empty_database(tmp_path):
    """
    Verify that a new database starts empty.
    """

    db_file = tmp_path / "test.db"

    db = DatabaseManager(db_path=str(db_file))

    assert db.get_report_count() == 0

    assert db.get_all_reports() == []

    db.close()