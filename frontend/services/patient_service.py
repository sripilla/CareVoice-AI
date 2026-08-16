"""
Service layer for patient operations.
"""

from database.database import DatabaseManager


def get_patient_by_id(
    patient_id: str,
):
    """
    Return a patient by Patient ID.
    """

    db = DatabaseManager()

    try:

        return db.get_patient_by_id(
            patient_id
        )

    finally:

        db.close()