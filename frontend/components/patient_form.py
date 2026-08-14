import streamlit as st


def render_patient_form():
    """
    Render the patient details form.

    Returns
    -------
    tuple
        patient_details : dict or None
        start_consultation : bool
    """

    st.subheader("👤 Patient Details")

    patient_id = st.text_input(
        "Patient ID",
        placeholder="Example: P001",
    )

    patient_name = st.text_input(
        "Patient Name",
        placeholder="Enter patient name",
    )

    age = st.number_input(
        "Age",
        min_value=0,
        max_value=120,
        value=None,
        step=1,
    )

    start_consultation = st.button(
        "Start Consultation",
        type="primary",
    )

    patient_details = None

    if start_consultation:

        if not patient_id.strip():

            st.warning("Please enter a Patient ID.")

        elif not patient_name.strip():

            st.warning("Please enter the patient name.")

        elif age is None:

            st.warning("Please enter the patient's age.")

        else:

            patient_details = {
                "patient_id": patient_id.strip(),
                "patient_name": patient_name.strip(),
                "age": age,
            }

    return patient_details, start_consultation