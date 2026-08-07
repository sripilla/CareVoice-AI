from careinsight.report_generator import ReportGenerator


def test_generate_clinical_report():

    generator = ReportGenerator()

    patient = {
        "patient_name": "Lakshmi",
        "age": 70,
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
    # Verify important sections
    # --------------------------------------------------

    assert "CAREVOICE AI CLINICAL REPORT" in report

    assert "Clinical Summary" in report

    assert "Conversation Summary (BART)" in report

    assert "Extracted Medical Information" in report

    assert "Risk Assessment" in report

    # --------------------------------------------------
    # Verify patient information
    # --------------------------------------------------

    assert "Lakshmi" in report

    assert "70" in report

    assert "cough" in report

    assert "fever" in report

    assert "Hypertension" in report

    assert "Diabetes" in report

    assert "Paracetamol" in report

    # --------------------------------------------------
    # Verify risk information
    # --------------------------------------------------

    assert "Risk Score : 5" in report

    assert "Risk Level : High" in report

    # --------------------------------------------------
    # Verify summary
    # --------------------------------------------------

    assert summary in report