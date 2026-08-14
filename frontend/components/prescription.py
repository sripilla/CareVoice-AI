"""
Doctor prescription and guidelines component.
"""

import streamlit as st

from frontend.services.prescription_service import (
    PrescriptionService,
)


def render_prescription(
    consultation_id: int,
):
    """
    Render the doctor prescription and guidelines workflow
    for a selected consultation.
    """

    st.divider()

    st.subheader("💊 Doctor Prescription & Guidelines")

    service = PrescriptionService()

    existing_prescription = service.get_prescription(
        consultation_id
    )

    # ----------------------------------------------------------
    # Existing Prescription
    # ----------------------------------------------------------

    if existing_prescription is not None:

        existing_prescription = dict(
            existing_prescription
        )

        st.info(
            "A prescription already exists for this "
            "consultation."
        )

        st.caption(
            "Patient language: "
            f"{existing_prescription['patient_language']}"
        )

        st.markdown("### Prescription")

        col1, col2 = st.columns(2)

        with col1:

            st.text_area(
                "English Prescription",
                value=existing_prescription[
                    "english_prescription"
                ] or "",
                height=180,
                disabled=True,
                key=(
                    f"existing_english_prescription_"
                    f"{consultation_id}"
                ),
            )

        with col2:

            st.text_area(
                "Translated Prescription",
                value=existing_prescription[
                    "translated_prescription"
                ] or "",
                height=180,
                disabled=True,
                key=(
                    f"existing_translated_prescription_"
                    f"{consultation_id}"
                ),
            )

        st.markdown("### Doctor Guidelines")

        col1, col2 = st.columns(2)

        with col1:

            st.text_area(
                "English Guidelines",
                value=existing_prescription[
                    "english_guidelines"
                ] or "",
                height=180,
                disabled=True,
                key=(
                    f"existing_english_guidelines_"
                    f"{consultation_id}"
                ),
            )

        with col2:

            st.text_area(
                "Translated Guidelines",
                value=existing_prescription[
                    "translated_guidelines"
                ] or "",
                height=180,
                disabled=True,
                key=(
                    f"existing_translated_guidelines_"
                    f"{consultation_id}"
                ),
            )

        return

    # ----------------------------------------------------------
    # New Prescription Input
    # ----------------------------------------------------------

    st.caption(
        "The patient's language is automatically taken "
        "from the consultation audio."
    )

    english_prescription = st.text_area(
        "Prescription (English)",
        placeholder=(
            "Example:\n"
            "Paracetamol 500 mg\n"
            "Take one tablet twice daily after food."
        ),
        height=180,
        key=f"english_prescription_{consultation_id}",
    )

    english_guidelines = st.text_area(
        "Doctor Guidelines (English)",
        placeholder=(
            "Example:\n"
            "Drink plenty of water.\n"
            "Take adequate rest."
        ),
        height=180,
        key=f"english_guidelines_{consultation_id}",
    )

    generate = st.button(
        "🌐 Generate Translation",
        type="primary",
        key=f"generate_prescription_{consultation_id}",
    )

    # ----------------------------------------------------------
    # Generate Translation
    # ----------------------------------------------------------

    if generate:

        if (
            not english_prescription.strip()
            and not english_guidelines.strip()
        ):

            st.warning(
                "Please enter a prescription or doctor "
                "guidelines."
            )

        else:

            try:

                with st.spinner(
                    "Translating into the patient's "
                    "detected language..."
                ):

                    prescription = (
                        service.translate_prescription(
                            consultation_id=consultation_id,
                            english_prescription=(
                                english_prescription.strip()
                            ),
                            english_guidelines=(
                                english_guidelines.strip()
                            ),
                        )
                    )

                st.session_state[
                    f"generated_prescription_{consultation_id}"
                ] = prescription

                st.success(
                    "Translation generated successfully."
                )

                st.rerun()

            except Exception as e:

                st.exception(e)

    # ----------------------------------------------------------
    # Display Generated Translation
    # ----------------------------------------------------------

    prescription = st.session_state.get(
        f"generated_prescription_{consultation_id}"
    )

    if prescription is None:

        return

    st.divider()

    st.caption(
        "Detected patient language: "
        f"**{prescription['patient_language']}**"
    )

    st.markdown("### Prescription")

    col1, col2 = st.columns(2)

    with col1:

        st.text_area(
            "English Prescription",
            value=prescription[
                "english_prescription"
            ],
            height=180,
            disabled=True,
            key=(
                f"generated_english_prescription_"
                f"{consultation_id}"
            ),
        )

    with col2:

        st.text_area(
            "Translated Prescription",
            value=prescription[
                "translated_prescription"
            ],
            height=180,
            disabled=True,
            key=(
                f"generated_translated_prescription_"
                f"{consultation_id}"
            ),
        )

    st.markdown("### Doctor Guidelines")

    col1, col2 = st.columns(2)

    with col1:

        st.text_area(
            "English Guidelines",
            value=prescription[
                "english_guidelines"
            ],
            height=180,
            disabled=True,
            key=(
                f"generated_english_guidelines_"
                f"{consultation_id}"
            ),
        )

    with col2:

        st.text_area(
            "Translated Guidelines",
            value=prescription[
                "translated_guidelines"
            ],
            height=180,
            disabled=True,
            key=(
                f"generated_translated_guidelines_"
                f"{consultation_id}"
            ),
        )

    # ----------------------------------------------------------
    # Save Prescription
    # ----------------------------------------------------------

    save = st.button(
        "💾 Save Prescription",
        type="primary",
        key=f"save_prescription_{consultation_id}",
    )

    if save:

        try:

            prescription_id = service.save_prescription(
                prescription
            )

            st.success(
                f"Prescription saved successfully "
                f"(ID: {prescription_id})."
            )

            st.session_state.pop(
                f"generated_prescription_{consultation_id}",
                None,
            )

            st.rerun()

        except Exception as e:

            st.exception(e)