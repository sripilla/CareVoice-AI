import streamlit as st


LANGUAGE_MAP = {
    "en": "English",
    "te": "Telugu",
    "hi": "Hindi",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
}


def render_entities():
    """
    Display patient information and extracted medical information.
    """

    report = st.session_state.get("report", {})

    patient = report.get("patient", {})

    language_code = report.get("detected_language", "")
    language = LANGUAGE_MAP.get(language_code, language_code.upper())

    # ------------------------------------------------------------------
    # Patient Information
    # ------------------------------------------------------------------

    st.subheader("👤 Patient Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Patient Name",
            patient.get("patient_name", "-"),
        )

    with col2:
        age = patient.get("age")

        st.metric(
            "Age",
            f"{age} Years" if age else "-",
        )

    with col3:
        st.metric(
            "Language",
            language if language else "-",
        )

    st.divider()

    # ------------------------------------------------------------------
    # Medical Information
    # ------------------------------------------------------------------

    st.subheader("🩺 Medical Information")

    symptoms = patient.get("symptoms", [])
    conditions = patient.get("conditions", [])
    medications = patient.get("medications", [])
    duration = patient.get("duration", "")

    left, right = st.columns(2)

    with left:

        st.markdown("### Symptoms")

        if symptoms:
            for symptom in symptoms:
                st.write(f"• {symptom}")
        else:
            st.write("-")

        st.markdown("### Conditions")

        if conditions:
            for condition in conditions:
                st.write(f"• {condition}")
        else:
            st.write("-")

    with right:

        st.markdown("### Medications")

        if medications:
            for medication in medications:
                st.write(f"• {medication}")
        else:
            st.write("-")

        st.markdown("### Duration")

        if duration:
            st.write(f"• {duration}")
        else:
            st.write("-")