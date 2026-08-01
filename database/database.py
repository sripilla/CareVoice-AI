import sqlite3
from pathlib import Path
from datetime import datetime


class DatabaseManager:

    def __init__(self, db_path="database/carevoice.db"):

        self.db_path = db_path

        Path(self.db_path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.connection = sqlite3.connect(
            self.db_path
        )

        self.cursor = self.connection.cursor()

        self.create_table()

    def create_table(self):
        """
        Create the patient_reports table if it does not exist.
        """

        self.cursor.execute(
            """
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
        )

        self.connection.commit()

        print("Database initialized successfully.")

    def save_report(self, report):
        """
        Save a clinical report to the database.
        """

        patient = report["patient"]
        risk = report["risk"]

        timestamp = datetime.now().strftime(
            "%d-%m-%Y %H:%M"
        )

        self.cursor.execute(
            """
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
            """,
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

        print("Report saved successfully.")

    def get_all_reports(self):
        """
        Retrieve all stored reports.
        """

        self.cursor.execute(
            """
            SELECT
                id,
                patient_name,
                age,
                risk_level,
                timestamp
            FROM patient_reports
            ORDER BY id DESC
            """
        )

        return self.cursor.fetchall()

    def get_report(self, report_id):
        """
        Retrieve a single report by ID.
        """

        self.cursor.execute(
            """
            SELECT *
            FROM patient_reports
            WHERE id = ?
            """,
            (report_id,),
        )

        return self.cursor.fetchone()

    def close(self):
        """
        Close the database connection.
        """

        self.connection.close()