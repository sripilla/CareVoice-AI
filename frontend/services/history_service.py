"""
Service layer for patient consultation history.
"""

from database.database import DatabaseManager


def get_patient_history(
    patient_id: str,
):
    """
    Return patient details and all consultations
    associated with the Patient ID.
    """

    db = DatabaseManager()

    try:

        patient = db.get_patient_by_id(
            patient_id
        )

        if patient is None:

            return None, []

        consultations = db.get_consultations_by_patient_id(
            patient_id
        )

        return patient, consultations

    finally:

        db.close()


def get_consultation(
    consultation_id: int,
):
    """
    Return a complete consultation by Consultation ID.
    """

    db = DatabaseManager()

    try:

        return db.get_consultation_by_id(
            consultation_id
        )

    finally:

        db.close()