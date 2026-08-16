from careinsight.report_generator import ReportGenerator


def test_generate_clinical_report():
    """
    Verify that a complete clinical report is generated
    with patient, clinical measurement, and risk information.
    """

    generator = ReportGenerator()

    patient = {
        "patient_id": "P001",
        "patient_name": "Lakshmi",
        "age": 70,
        "blood_pressure": "130/90",
        "weight": 85.0,
        "blood_sugar": 140,
        "symptoms": ["cough", "fever"],
        "conditions": ["Hypertension", "Diabetes"],
        "medications": ["Paracetamol"],
        "duration": "3 days",
    }

    risk = {
        "risk_score": 5,
        "risk_level": "High",
    }

    summary = (
        "Patient reports cough and fever for three days."
    )

    report = generator.generate(
        summary=summary,
        patient=patient,
        risk=risk,
    )

    # --------------------------------------------------
    # Verify report sections
    # --------------------------------------------------

    assert "CAREVOICE AI CLINICAL REPORT" in report
    assert "Clinical Summary" in report
    assert "Conversation Summary (BART)" in report
    assert "Patient and Clinical Information" in report
    assert "Risk Assessment" in report

    # --------------------------------------------------
    # Verify patient information
    # --------------------------------------------------

    assert "P001" in report
    assert "Lakshmi" in report
    assert "70" in report

    # --------------------------------------------------
    # Verify clinical measurements
    # --------------------------------------------------

    assert "130/90" in report
    assert "85.0 kg" in report
    assert "140 mg/dL" in report

    # --------------------------------------------------
    # Verify extracted medical information
    # --------------------------------------------------

    assert "cough" in report
    assert "fever" in report
    assert "Hypertension" in report
    assert "Diabetes" in report
    assert "Paracetamol" in report
    assert "3 days" in report

    # --------------------------------------------------
    # Verify risk information
    # --------------------------------------------------

    assert "Risk Score : 5" in report
    assert "Risk Level : High" in report

    # --------------------------------------------------
    # Verify conversation summary
    # --------------------------------------------------

    assert summary in report


def test_generate_report_with_missing_measurements():
    """
    Verify that missing clinical measurements are displayed
    as 'Not provided'.
    """

    generator = ReportGenerator()

    patient = {
        "patient_id": "P002",
        "patient_name": "Ravi",
        "age": 45,
        "blood_pressure": None,
        "weight": None,
        "blood_sugar": None,
        "symptoms": [],
        "conditions": [],
        "medications": [],
        "duration": "",
    }

    risk = {
        "risk_score": 0,
        "risk_level": "Low",
    }

    report = generator.generate(
        summary="No significant clinical findings.",
        patient=patient,
        risk=risk,
    )

    assert "Blood Pressure\n- Not provided" in report
    assert "Weight\n- Not provided" in report
    assert "Blood Sugar\n- Not provided" in report
    assert "Symptoms\n- None" in report
    assert "Conditions\n- None" in report
    assert "Existing Medications\n- None" in report
    assert "Duration\n- Not specified" in report
    assert "Risk Level : Low" in report