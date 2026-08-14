"""
Patient consultation history component.
"""

from datetime import datetime

import streamlit as st

from frontend.services.history_service import (
    get_consultation,
    get_patient_history,
)


def render_history():
    """
    Search and display patient consultation history.
    """

    st.subheader("🔎 Search Patient History")

    patient_id = st.text_input(
        "Patient ID",
        placeholder="Enter Patient ID",
    )

    search = st.button(
        "Search History",
        type="primary",
    )

    # ----------------------------------------------------------
    # Search Patient
    # ----------------------------------------------------------

    if search:

        if not patient_id.strip():

            st.warning(
                "Please enter a Patient ID."
            )

        else:

            patient, consultations = get_patient_history(
                patient_id.strip()
            )

            if patient is None:

                st.session_state.history_patient = None
                st.session_state.history_consultations = []
                st.session_state.selected_history_consultation = None

                st.warning(
                    "No patient found with this Patient ID."
                )

            else:

                st.session_state.history_patient = (
                    dict(patient)
                )

                st.session_state.history_consultations = [
                    dict(consultation)
                    for consultation in consultations
                ]

                st.session_state.selected_history_consultation = None

                st.success(
                    "Patient history loaded successfully."
                )

    # ----------------------------------------------------------
    # Display Patient Information
    # ----------------------------------------------------------

    patient = st.session_state.get(
        "history_patient"
    )

    if patient is None:

        return

    st.divider()

    st.subheader("👤 Patient Information")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Patient ID",
            patient["patient_id"],
        )

    with col2:

        st.metric(
            "Patient Name",
            patient["patient_name"],
        )

    with col3:

        st.metric(
            "Age",
            patient["age"],
        )

    # ----------------------------------------------------------
    # Consultation List
    # ----------------------------------------------------------

    consultations = st.session_state.get(
        "history_consultations",
        [],
    )

    st.divider()

    st.subheader("📋 Consultation History")

    if not consultations:

        st.info(
            "No consultations found for this patient."
        )

        return

    consultation_options = {
        consultation["consultation_id"]: (
            f"Consultation #{consultation['consultation_id']} "
            f"— {consultation['timestamp']} "
            f"— {consultation['risk_level']} Risk"
        )
        for consultation in consultations
    }

    selected_id = st.selectbox(
        "Select a consultation",
        options=list(consultation_options.keys()),
        format_func=lambda consultation_id: (
            consultation_options[consultation_id]
        ),
    )

    # ----------------------------------------------------------
    # Load Selected Consultation
    # ----------------------------------------------------------

    if selected_id is not None:

        consultation = get_consultation(
            selected_id
        )

        if consultation is not None:

            st.session_state.selected_history_consultation = (
                dict(consultation)
            )

    consultation = st.session_state.get(
        "selected_history_consultation"
    )

    if consultation is None:

        return

    # ----------------------------------------------------------
    # Consultation Details
    # ----------------------------------------------------------

    st.divider()

    st.subheader("🩺 Consultation Details")

    detail_col1, detail_col2, detail_col3 = st.columns(3)

    with detail_col1:

        st.metric(
            "Consultation ID",
            consultation["consultation_id"],
        )

    with detail_col2:

        st.metric(
            "Detected Language",
            consultation["detected_language"] or "Unknown",
        )

    with detail_col3:

        st.metric(
            "Risk Level",
            consultation["risk_level"] or "Unknown",
        )

    st.caption(
        f"Consultation Date: "
        f"{consultation['timestamp']}"
    )

    # ----------------------------------------------------------
    # Clinical Report
    # ----------------------------------------------------------

    st.subheader("📄 Clinical Report")

    clinical_report = consultation.get(
        "clinical_report",
        "",
    )

    st.text_area(
        "Saved Clinical Report",
        value=clinical_report,
        height=450,
        disabled=True,
    )

    # ----------------------------------------------------------
    # Download
    # ----------------------------------------------------------

    if clinical_report:

        st.download_button(
            label="📥 Download Clinical Report",
            data=clinical_report,
            file_name=(
                f"carevoice_consultation_"
                f"{consultation['consultation_id']}_"
                f"{datetime.now():%Y%m%d_%H%M%S}.txt"
            ),
            mime="text/plain",
            type="primary",
        )