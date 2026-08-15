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

    CREATE_PATIENTS_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS patients (

        patient_id TEXT PRIMARY KEY,

        patient_name TEXT NOT NULL,

        age INTEGER NOT NULL,

        created_at TEXT NOT NULL,

        updated_at TEXT NOT NULL

    )
    """

    CREATE_CONSULTATIONS_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS consultations (

        consultation_id INTEGER PRIMARY KEY AUTOINCREMENT,

        patient_id TEXT NOT NULL,

        timestamp TEXT NOT NULL,

        blood_pressure TEXT,

        weight REAL,

        blood_sugar REAL,

        detected_language TEXT,

        original_transcript TEXT,

        english_transcript TEXT,

        summary TEXT,

        symptoms TEXT,

        conditions TEXT,

        medications TEXT,

        duration TEXT,

        risk_score INTEGER,

        risk_level TEXT,

        clinical_report TEXT,

        FOREIGN KEY (patient_id)
            REFERENCES patients(patient_id)

    )
    """

    CREATE_PRESCRIPTIONS_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS prescriptions (

        prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,

        consultation_id INTEGER NOT NULL UNIQUE,

        english_prescription TEXT,

        translated_prescription TEXT,

        english_guidelines TEXT,

        translated_guidelines TEXT,

        patient_language TEXT NOT NULL,

        created_at TEXT NOT NULL,

        FOREIGN KEY (consultation_id)
            REFERENCES consultations(consultation_id)

    )
    """

    INSERT_PATIENT_QUERY = """
    INSERT INTO patients (

        patient_id,
        patient_name,
        age,
        created_at,
        updated_at

    )

    VALUES (?, ?, ?, ?, ?)

    ON CONFLICT(patient_id)
    DO UPDATE SET

        patient_name = excluded.patient_name,
        age = excluded.age,
        updated_at = excluded.updated_at
    """

    INSERT_CONSULTATION_QUERY = """
    INSERT INTO consultations (

        patient_id,
        timestamp,
        blood_pressure,
        weight,
        blood_sugar,
        detected_language,
        original_transcript,
        english_transcript,
        summary,
        symptoms,
        conditions,
        medications,
        duration,
        risk_score,
        risk_level,
        clinical_report

    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    GET_PATIENT_QUERY = """
    SELECT *
    FROM patients
    WHERE patient_id = ?
    """

    GET_CONSULTATIONS_BY_PATIENT_QUERY = """
    SELECT
        consultation_id,
        patient_id,
        timestamp,
        risk_level
    FROM consultations
    WHERE patient_id = ?
    ORDER BY consultation_id DESC
    """

    GET_CONSULTATION_QUERY = """
    SELECT *
    FROM consultations
    WHERE consultation_id = ?
    """

    CONSULTATION_COUNT_QUERY = """
    SELECT COUNT(*)
    FROM consultations
    """

    DELETE_CONSULTATION_QUERY = """
    DELETE FROM consultations
    WHERE consultation_id = ?
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

            self._enable_foreign_keys()

            self.create_tables()

            logger.info(
                "Database initialized successfully."
            )

        except Exception:

            logger.exception(
                "Failed to initialize database."
            )

            raise

    # ======================================================
    # Database Initialization
    # ======================================================

    def _enable_foreign_keys(self):
        """
        Enable SQLite foreign key enforcement.
        """

        self.cursor.execute(
            "PRAGMA foreign_keys = ON"
        )

    def _add_consultation_columns_if_missing(self):
        """
        Add optional clinical measurement columns to an
        existing consultations table if they are missing.
        """

        self.cursor.execute(
            "PRAGMA table_info(consultations)"
        )

        existing_columns = {
            row["name"]
            for row in self.cursor.fetchall()
        }

        required_columns = {
            "blood_pressure": "TEXT",
            "weight": "REAL",
            "blood_sugar": "REAL",
        }

        for column_name, column_type in (
            required_columns.items()
        ):

            if column_name not in existing_columns:

                self.cursor.execute(
                    f"""
                    ALTER TABLE consultations
                    ADD COLUMN {column_name} {column_type}
                    """
                )

                logger.info(
                    "Added column %s to consultations table.",
                    column_name,
                )

    def create_tables(self):
        """
        Create the patient, consultation and prescription tables.
        """

        self.cursor.execute(
            self.CREATE_PATIENTS_TABLE_QUERY
        )

        self.cursor.execute(
            self.CREATE_CONSULTATIONS_TABLE_QUERY
        )

        self._add_consultation_columns_if_missing()

        self.cursor.execute(
            self.CREATE_PRESCRIPTIONS_TABLE_QUERY
        )

        self.connection.commit()

    # ======================================================
    # Patient Management
    # ======================================================

    def save_patient(
        self,
        patient: dict,
    ):
        """
        Create or update a patient record.
        """

        timestamp = datetime.now().strftime(
            DATABASE_TIMESTAMP_FORMAT
        )

        self.cursor.execute(
            self.INSERT_PATIENT_QUERY,
            (
                patient["patient_id"],
                patient["patient_name"],
                patient["age"],
                timestamp,
                timestamp,
            ),
        )

        self.connection.commit()

        logger.info(
            "Patient %s saved successfully.",
            patient["patient_id"],
        )

    def get_patient_by_id(
        self,
        patient_id: str,
    ):
        """
        Return a patient by Patient ID.
        """

        self.cursor.execute(
            self.GET_PATIENT_QUERY,
            (patient_id,),
        )

        return self.cursor.fetchone()

    # ======================================================
    # Consultation Management
    # ======================================================

    def save_consultation(
        self,
        report: dict,
    ):
        """
        Save a consultation and its clinical report.
        """

        patient = report["patient"]
        risk = report["risk"]

        timestamp = datetime.now().strftime(
            DATABASE_TIMESTAMP_FORMAT
        )

        self.save_patient(patient)

        self.cursor.execute(
            self.INSERT_CONSULTATION_QUERY,
            (
                patient["patient_id"],
                timestamp,
                patient.get("blood_pressure"),
                patient.get("weight"),
                patient.get("blood_sugar"),
                report["detected_language"],
                report["original_transcript"],
                report["english_transcript"],
                report["summary"],
                ", ".join(patient["symptoms"]),
                ", ".join(patient["conditions"]),
                ", ".join(patient["medications"]),
                patient["duration"],
                risk["risk_score"],
                risk["risk_level"],
                report["clinical_report"],
            ),
        )

        self.connection.commit()

        consultation_id = self.cursor.lastrowid

        logger.info(
            "Consultation %d saved for patient %s.",
            consultation_id,
            patient["patient_id"],
        )

        return consultation_id

    # ======================================================
    # Prescription Management
    # ======================================================

    def save_prescription(
        self,
        prescription: dict,
    ):
        """
        Save a prescription and doctor guidelines
        for a consultation.
        """

        timestamp = datetime.now().strftime(
            DATABASE_TIMESTAMP_FORMAT
        )

        query = """
        INSERT INTO prescriptions (

            consultation_id,
            english_prescription,
            translated_prescription,
            english_guidelines,
            translated_guidelines,
            patient_language,
            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        self.cursor.execute(
            query,
            (
                prescription["consultation_id"],
                prescription.get(
                    "english_prescription",
                    "",
                ),
                prescription.get(
                    "translated_prescription",
                    "",
                ),
                prescription.get(
                    "english_guidelines",
                    "",
                ),
                prescription.get(
                    "translated_guidelines",
                    "",
                ),
                prescription["patient_language"],
                timestamp,
            ),
        )

        self.connection.commit()

        prescription_id = self.cursor.lastrowid

        logger.info(
            "Prescription %d saved for consultation %d.",
            prescription_id,
            prescription["consultation_id"],
        )

        return prescription_id

    def get_prescription_by_consultation_id(
        self,
        consultation_id: int,
    ):
        """
        Return the prescription associated with
        a consultation.
        """

        query = """
        SELECT *
        FROM prescriptions
        WHERE consultation_id = ?
        """

        self.cursor.execute(
            query,
            (consultation_id,),
        )

        return self.cursor.fetchone()

    # ======================================================
    # Read
    # ======================================================

    def get_consultations_by_patient_id(
        self,
        patient_id: str,
    ):
        """
        Return all consultations for a patient.
        """

        self.cursor.execute(
            self.GET_CONSULTATIONS_BY_PATIENT_QUERY,
            (patient_id,),
        )

        return self.cursor.fetchall()

    def get_consultation_by_id(
        self,
        consultation_id: int,
    ):
        """
        Return a consultation by ID.
        """

        self.cursor.execute(
            self.GET_CONSULTATION_QUERY,
            (consultation_id,),
        )

        return self.cursor.fetchone()

    def get_consultation_count(self) -> int:
        """
        Return the total number of consultations.
        """

        self.cursor.execute(
            self.CONSULTATION_COUNT_QUERY
        )

        return self.cursor.fetchone()[0]

    # ======================================================
    # Delete
    # ======================================================

    def delete_consultation(
        self,
        consultation_id: int,
    ):
        """
        Delete a consultation.
        """

        self.cursor.execute(
            self.DELETE_CONSULTATION_QUERY,
            (consultation_id,),
        )

        self.connection.commit()

        logger.info(
            "Deleted consultation with ID %d",
            consultation_id,
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