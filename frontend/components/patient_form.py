import streamlit as st

from frontend.services.patient_service import (
    get_patient_by_id,
)


def render_patient_form():
    """
    Render the patient profile and clinical details form.

    Returns
    -------
    tuple
        patient_details : dict or None
        start_consultation : bool
    """

    st.subheader("👤 Patient Profile")

    # ==========================================================
    # Patient ID
    # ==========================================================

    patient_id = st.text_input(
        "Patient ID",
        placeholder="Example: P001",
        key="patient_id_input",
    )

    load_patient = st.button(
        "Load Patient",
    )

    # ==========================================================
    # Load Existing Patient
    # ==========================================================

    if load_patient:

        if not patient_id.strip():

            st.warning(
                "Please enter a Patient ID."
            )

        else:

            patient = get_patient_by_id(
                patient_id.strip()
            )

            if patient is None:

                st.session_state.patient_loaded = False
                st.session_state.patient_name_input = ""
                st.session_state.patient_age_input = None

                st.info(
                    "New patient. Please enter the "
                    "patient details below."
                )

            else:

                st.session_state.patient_loaded = True
                st.session_state.patient_name_input = (
                    patient["patient_name"]
                )
                st.session_state.patient_age_input = (
                    patient["age"]
                )

                st.success(
                    "Existing patient profile loaded."
                )

    # ==========================================================
    # Patient Details
    # ==========================================================

    patient_name = st.text_input(
        "Patient Name",
        placeholder="Enter patient name",
        key="patient_name_input",
    )

    age = st.number_input(
        "Age",
        min_value=0,
        max_value=120,
        value=st.session_state.get(
            "patient_age_input",
            None,
        ),
        step=1,
        key="patient_age_input",
    )

    # ==========================================================
    # Clinical Measurements
    # ==========================================================

    st.subheader("🩺 Clinical Measurements")

    st.caption(
        "Optional — enter available measurements for "
        "this consultation."
    )

    blood_pressure = st.text_input(
        "Blood Pressure",
        placeholder="Example: 120/80 mmHg",
    )

    weight = st.number_input(
        "Weight (kg)",
        min_value=0.0,
        value=None,
        step=0.1,
    )

    blood_sugar = st.number_input(
        "Blood Sugar (mg/dL)",
        min_value=0.0,
        value=None,
        step=0.1,
    )

    # ==========================================================
    # Start Consultation
    # ==========================================================

    start_consultation = st.button(
        "Start Consultation",
        type="primary",
    )

    patient_details = None

    if start_consultation:

        if not patient_id.strip():

            st.warning(
                "Please enter a Patient ID."
            )

        elif not patient_name.strip():

            st.warning(
                "Please enter the patient name."
            )

        elif age is None:

            st.warning(
                "Please enter the patient's age."
            )

        else:

            patient_details = {
                "patient_id": patient_id.strip(),
                "patient_name": patient_name.strip(),
                "age": age,
                "blood_pressure": (
                    blood_pressure.strip() or None
                ),
                "weight": weight,
                "blood_sugar": blood_sugar,
            }

    return patient_details, start_consultation