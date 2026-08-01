import sqlite3
from datetime import datetime
from pathlib import Path

from config import (
    DATABASE_PATH,
    DATABASE_TIMESTAMP_FORMAT,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """
    SQLite database manager for CareVoice AI.
    """

    CREATE_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS patient_reports (

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

    INSERT_REPORT_QUERY = """
    INSERT INTO patient_reports (

        timestamp,
        patient_name,
        age,
        symptoms,
        conditions,
        medications,
        duration,
        summary,
        risk_score,
        risk_level,
        clinical_report

    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    GET_ALL_REPORTS_QUERY = """
    SELECT
        id,
        timestamp,
        patient_name,
        age,
        risk_level
    FROM patient_reports
    ORDER BY id DESC
    """

    GET_REPORT_QUERY = """
    SELECT *
    FROM patient_reports
    WHERE id = ?
    """

    DELETE_REPORT_QUERY = """
    DELETE FROM patient_reports
    WHERE id = ?
    """

    REPORT_COUNT_QUERY = """
    SELECT COUNT(*)
    FROM patient_reports
    """

    def __init__(
        self,
        db_path: str = str(DATABASE_PATH),
    ):
        """
        Initialize the SQLite database.
        """

        self.db_path = db_path

        Path(self.db_path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        logger.info(
            "Connecting to database: %s",
            self.db_path,
        )

        try:

            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
            )

            self.connection.row_factory = sqlite3.Row

            self.cursor = self.connection.cursor()

            self.create_table()

            logger.info(
                "Database initialized successfully."
            )

        except Exception:

            logger.exception(
                "Failed to initialize database."
            )

            raise

    # ======================================================
    # Table Initialization
    # ======================================================

    def create_table(self):
        """
        Create the patient_reports table.
        """

        self.cursor.execute(
            self.CREATE_TABLE_QUERY
        )

        self.connection.commit()

    # ======================================================
    # Insert
    # ======================================================

    def save_report(
        self,
        report: dict,
    ):
        """
        Save a clinical report.
        """

        patient = report["patient"]
        risk = report["risk"]

        timestamp = datetime.now().strftime(
            DATABASE_TIMESTAMP_FORMAT
        )

        self.cursor.execute(
            self.INSERT_REPORT_QUERY,
            (
                timestamp,
                patient["patient_name"],
                patient["age"],
                ", ".join(patient["symptoms"]),
                ", ".join(patient["conditions"]),
                ", ".join(patient["medications"]),
                patient["duration"],
                report["summary"],
                risk["risk_score"],
                risk["risk_level"],
                report["clinical_report"],
            ),
        )

        self.connection.commit()

        logger.info(
            "Clinical report saved successfully."
        )

    # ======================================================
    # Read
    # ======================================================

    def get_all_reports(self):
        """
        Return all reports.
        """

        self.cursor.execute(
            self.GET_ALL_REPORTS_QUERY
        )

        return self.cursor.fetchall()

    def get_report_by_id(
        self,
        report_id: int,
    ):
        """
        Return a report by ID.
        """

        self.cursor.execute(
            self.GET_REPORT_QUERY,
            (report_id,),
        )

        return self.cursor.fetchone()

    def get_report_count(self) -> int:
        """
        Return the total number of reports.
        """

        self.cursor.execute(
            self.REPORT_COUNT_QUERY
        )

        return self.cursor.fetchone()[0]

    # ======================================================
    # Delete
    # ======================================================

    def delete_report(
        self,
        report_id: int,
    ):
        """
        Delete a report.
        """

        self.cursor.execute(
            self.DELETE_REPORT_QUERY,
            (report_id,),
        )

        self.connection.commit()

        logger.info(
            "Deleted report with ID %d",
            report_id,
        )

    # ======================================================
    # Cleanup
    # ======================================================

    def close(self):
        """
        Close the database connection.
        """

        self.connection.close()

        logger.info(
            "Database connection closed."
        )