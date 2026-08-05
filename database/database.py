import sqlite3
import threading
from contextlib import contextmanager
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

    # Columns added after the original schema shipped. Existing
    # databases are upgraded in place by _migrate(); the table is
    # never dropped or recreated.
    ADDED_COLUMNS = {
        "detected_language": "TEXT",
        "original_transcript": "TEXT",
        "english_transcript": "TEXT",
    }

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
        clinical_report,
        detected_language,
        original_transcript,
        english_transcript

    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

        # FastAPI runs the sync endpoints in a threadpool, so
        # several requests can reach this object at once. The
        # connection is shared with check_same_thread=False and
        # every statement is serialized through this lock.
        self._lock = threading.Lock()

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
    # Connection Handling
    # ======================================================

    @contextmanager
    def _cursor(self):
        """
        Yield a short-lived cursor under the connection lock.

        A cursor per statement avoids the interleaving that a
        single shared cursor suffers under concurrent requests.
        """

        with self._lock:

            cursor = self.connection.cursor()

            try:
                yield cursor

            finally:
                cursor.close()

    # ======================================================
    # Table Initialization
    # ======================================================

    def create_table(self):
        """
        Create the patient_reports table and bring an existing
        one up to the current schema.
        """

        with self._cursor() as cursor:

            cursor.execute(self.CREATE_TABLE_QUERY)

            self._migrate(cursor)

            self.connection.commit()

    def _migrate(
        self,
        cursor,
    ):
        """
        Add any columns missing from an older database.

        Idempotent: re-running it against a current database is a
        no-op, and no existing data is touched.
        """

        cursor.execute(
            "PRAGMA table_info(patient_reports)"
        )

        existing = {
            row["name"]
            for row in cursor.fetchall()
        }

        for column, column_type in self.ADDED_COLUMNS.items():

            if column in existing:
                continue

            logger.info(
                "Migrating database: adding column '%s'.",
                column,
            )

            cursor.execute(
                "ALTER TABLE patient_reports "
                f"ADD COLUMN {column} {column_type}"
            )

    # ======================================================
    # Insert
    # ======================================================

    def save_report(
        self,
        report: dict,
    ) -> int:
        """
        Save a clinical report.

        Returns
        -------
        int
            The new report's row ID, so callers can link straight
            to it -- the PDF download needs it.
        """

        patient = report["patient"]
        risk = report["risk"]

        timestamp = datetime.now().strftime(
            DATABASE_TIMESTAMP_FORMAT
        )

        with self._cursor() as cursor:

            cursor.execute(
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
                    report.get("detected_language"),
                    report.get("original_transcript"),
                    report.get("english_transcript"),
                ),
            )

            report_id = cursor.lastrowid

            self.connection.commit()

        logger.info(
            "Clinical report saved successfully (id=%d).",
            report_id,
        )

        return report_id

    # ======================================================
    # Read
    # ======================================================

    def get_all_reports(self):
        """
        Return all reports.
        """

        with self._cursor() as cursor:

            cursor.execute(
                self.GET_ALL_REPORTS_QUERY
            )

            return cursor.fetchall()

    def get_report_by_id(
        self,
        report_id: int,
    ):
        """
        Return a report by ID.
        """

        with self._cursor() as cursor:

            cursor.execute(
                self.GET_REPORT_QUERY,
                (report_id,),
            )

            return cursor.fetchone()

    def search_reports(
        self,
        name: str | None = None,
        risk_level: str | None = None,
    ):
        """
        Return report summaries filtered by patient name and/or
        risk level. Both filters are optional.
        """

        query = [
            "SELECT id, timestamp, patient_name, age, risk_level",
            "FROM patient_reports",
        ]

        conditions = []
        parameters: list = []

        if name:
            conditions.append("patient_name LIKE ?")
            parameters.append(f"%{name}%")

        if risk_level:
            conditions.append("risk_level = ?")
            parameters.append(risk_level)

        if conditions:
            query.append(
                "WHERE " + " AND ".join(conditions)
            )

        query.append("ORDER BY id DESC")

        with self._cursor() as cursor:

            cursor.execute(
                "\n".join(query),
                parameters,
            )

            return cursor.fetchall()

    def get_report_count(self) -> int:
        """
        Return the total number of reports.
        """

        with self._cursor() as cursor:

            cursor.execute(
                self.REPORT_COUNT_QUERY
            )

            return cursor.fetchone()[0]

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

        with self._cursor() as cursor:

            cursor.execute(
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
