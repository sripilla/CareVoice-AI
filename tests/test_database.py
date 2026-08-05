"""
Persistence, including the in-place migration that upgrades a
database created before the transcript columns existed.
"""

import sqlite3

import pytest

from database.database import DatabaseManager

# The schema as it shipped originally, without the three columns
# added later.
LEGACY_SCHEMA = """
CREATE TABLE patient_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    patient_name TEXT,
    age INTEGER,
    symptoms TEXT,
    conditions TEXT,
    medications TEXT,
    duration TEXT,
    summary TEXT,
    risk_score INTEGER,
    risk_level TEXT,
    clinical_report TEXT
)
"""


@pytest.fixture
def database(tmp_path):

    manager = DatabaseManager(str(tmp_path / "test.db"))

    yield manager

    manager.close()


def test_save_returns_row_id(database, report):

    first = database.save_report(report)
    second = database.save_report(report)

    assert first == 1
    assert second == 2


def test_saved_report_round_trips(database, report):

    report_id = database.save_report(report)

    stored = database.get_report_by_id(report_id)

    assert stored["patient_name"] == "Lakshmi"
    assert stored["age"] == 70
    assert stored["symptoms"] == "fever, cough"
    assert stored["conditions"] == "Hypertension, Diabetes"
    assert stored["risk_level"] == "High"
    assert stored["risk_score"] == 5
    assert stored["detected_language"] == "te"
    assert (
        stored["english_transcript"]
        == report["english_transcript"]
    )
    assert (
        stored["original_transcript"]
        == report["original_transcript"]
    )


def test_missing_report_returns_none(database):

    assert database.get_report_by_id(999) is None


def test_count_and_delete(database, report):

    report_id = database.save_report(report)

    assert database.get_report_count() == 1

    database.delete_report(report_id)

    assert database.get_report_count() == 0
    assert database.get_report_by_id(report_id) is None


def test_get_all_reports_is_newest_first(database, report):

    database.save_report(report)
    database.save_report(report)

    reports = database.get_all_reports()

    assert [row["id"] for row in reports] == [2, 1]


def test_search_by_name_is_partial_and_case_insensitive(
    database,
    report,
):

    database.save_report(report)

    assert len(database.search_reports(name="aksh")) == 1
    assert len(database.search_reports(name="Ravi")) == 0


def test_search_by_risk_level(database, report):

    database.save_report(report)

    report["risk"] = {"risk_score": 0, "risk_level": "Low"}
    database.save_report(report)

    assert len(database.search_reports(risk_level="High")) == 1
    assert len(database.search_reports(risk_level="Low")) == 1
    assert len(database.search_reports(risk_level="Medium")) == 0


def test_search_combines_filters(database, report):

    database.save_report(report)

    assert (
        len(
            database.search_reports(
                name="Lakshmi",
                risk_level="High",
            )
        )
        == 1
    )

    assert (
        len(
            database.search_reports(
                name="Lakshmi",
                risk_level="Low",
            )
        )
        == 0
    )


def test_search_without_filters_returns_everything(
    database,
    report,
):

    database.save_report(report)

    assert len(database.search_reports()) == 1


# ==========================================================
# Migration
# ==========================================================

def test_migrates_legacy_database_without_losing_rows(tmp_path):

    db_path = tmp_path / "legacy.db"

    # Build a database on the old schema with one report in it.
    connection = sqlite3.connect(str(db_path))
    connection.execute(LEGACY_SCHEMA)
    connection.execute(
        "INSERT INTO patient_reports ("
        "timestamp, patient_name, age, symptoms, conditions, "
        "medications, duration, summary, risk_score, risk_level, "
        "clinical_report) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "01-01-2026 10:00",
            "Ravi",
            45,
            "fever",
            "Diabetes",
            "",
            "2 days",
            "summary",
            2,
            "Medium",
            "report",
        ),
    )
    connection.commit()
    connection.close()

    manager = DatabaseManager(str(db_path))

    try:

        stored = manager.get_report_by_id(1)

        # The pre-existing row survives...
        assert stored["patient_name"] == "Ravi"
        assert stored["risk_level"] == "Medium"

        # ...and the new columns exist, empty for old rows.
        assert stored["detected_language"] is None
        assert stored["original_transcript"] is None

    finally:
        manager.close()


def test_migration_is_idempotent(tmp_path, report):

    db_path = str(tmp_path / "repeat.db")

    first = DatabaseManager(db_path)
    first.save_report(report)
    first.close()

    # Opening again re-runs create_table() and _migrate().
    second = DatabaseManager(db_path)

    try:
        assert second.get_report_count() == 1
        assert second.get_report_by_id(1)["detected_language"] == "te"

    finally:
        second.close()
