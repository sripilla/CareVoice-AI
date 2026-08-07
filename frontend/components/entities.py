import streamlit as st


def render_entities():
    """
    Display extracted medical information.
    """

    st.subheader("🩺 Medical Information")

    report = st.session_state.get("report", {})
    patient = report.get("patient", {})

    symptoms = patient.get("symptoms", [])
    conditions = patient.get("conditions", [])
    medications = patient.get("medications", [])
    duration = patient.get("duration", "")

    # Symptoms
    st.markdown("**Symptoms**")
    if symptoms:
        for symptom in symptoms:
            st.write(f"• {symptom}")
    else:
        st.write("-")

    # Conditions
    st.markdown("**Conditions**")
    if conditions:
        for condition in conditions:
            st.write(f"• {condition}")
    else:
        st.write("-")

    # Medications
    st.markdown("**Medications**")
    if medications:
        for medication in medications:
            st.write(f"• {medication}")
    else:
        st.write("-")

    # Duration
    st.markdown("**Duration**")
    if duration:
        st.write(f"• {duration}")
    else:
        st.write("-")