from datetime import datetime


class ReportGenerator:

    def generate(self, summary, patient, risk):

        # ==========================================
        # Patient Information
        # ==========================================

        name = patient["patient_name"] or "Unknown"
        age = patient["age"] or "Unknown"
        duration = patient["duration"] or "Not specified"

        symptoms = ", ".join(patient["symptoms"]) or "Not reported"
        conditions = ", ".join(patient["conditions"]).lower() or "none"
        medications = ", ".join(patient["medications"]) or "none"

        # ==========================================
        # Formatted Lists
        # ==========================================

        symptoms_text = (
            "\n".join(
                f"- {symptom}"
                for symptom in patient["symptoms"]
            )
            if patient["symptoms"]
            else "- None"
        )

        conditions_text = (
            "\n".join(
                f"- {condition}"
                for condition in patient["conditions"]
            )
            if patient["conditions"]
            else "- None"
        )

        medications_text = (
            "\n".join(
                f"- {medicine}"
                for medicine in patient["medications"]
            )
            if patient["medications"]
            else "- None"
        )

        # ==========================================
        # Timestamp
        # ==========================================

        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M")

        # ==========================================
        # Report
        # ==========================================

        report = f"""
============================================================
                CAREVOICE AI CLINICAL REPORT
============================================================

Generated On : {timestamp}

------------------------------------------------------------
Clinical Summary
------------------------------------------------------------

A {age}-year-old patient ({name}) reports
{symptoms} for {duration}.

The patient has {conditions}
and is currently taking {medications}.

Based on the extracted clinical information,
the patient is classified as

{risk['risk_level']} Risk
(Risk Score: {risk['risk_score']}).

------------------------------------------------------------
Conversation Summary (BART)
------------------------------------------------------------

{summary}

------------------------------------------------------------
Extracted Medical Information
------------------------------------------------------------

Patient Name : {name}
Age          : {age}

Symptoms
{symptoms_text}

Conditions
{conditions_text}

Medications
{medications_text}

Duration
- {duration}

------------------------------------------------------------
Risk Assessment
------------------------------------------------------------

Risk Score : {risk['risk_score']}
Risk Level : {risk['risk_level']}

============================================================
"""

        return report