"""
Endpoint behaviour, exercised against a stub engine so no model
weights are loaded.
"""

import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from database.database import DatabaseManager


class StubEngine:
    """
    Stands in for CareVoiceEngine: a real database, a canned
    pipeline result.
    """

    def __init__(self, db_path, report):

        self.database = DatabaseManager(str(db_path))
        self._report = report
        self.calls = []

    def process_audio(self, audio_path):

        self.calls.append(audio_path)

        result = dict(self._report)

        result["report_id"] = self.database.save_report(result)

        return result


@pytest.fixture
def engine(tmp_path, report):

    return StubEngine(tmp_path / "api.db", report)


@pytest.fixture
def client(engine):

    app = create_app(engine_factory=lambda: engine)

    with TestClient(app) as test_client:
        yield test_client


# ==========================================================
# Health
# ==========================================================

def test_health_check(client):

    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "Running"


# ==========================================================
# Analyze
# ==========================================================

def test_analyze_returns_the_full_report(client):

    response = client.post(
        "/analyze",
        files={"audio": ("consultation.wav", b"fake audio", "audio/wav")},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["report_id"] == 1
    assert body["detected_language"] == "te"
    assert body["patient"]["patient_name"] == "Lakshmi"
    assert body["risk"]["risk_level"] == "High"
    assert body["warnings"] == []


def test_analyze_accepts_the_widened_formats(client):

    for filename in [
        "a.wav",
        "b.mp3",
        "c.m4a",
        "d.webm",
        "e.ogg",
        "f.flac",
    ]:

        response = client.post(
            "/analyze",
            files={"audio": (filename, b"fake audio", "audio/*")},
        )

        assert response.status_code == 200, filename


def test_analyze_rejects_unsupported_formats(client):

    response = client.post(
        "/analyze",
        files={"audio": ("notes.txt", b"not audio", "text/plain")},
    )

    assert response.status_code == 400
    assert "Unsupported audio format" in response.json()["detail"]


def test_analyze_cleans_up_the_upload(client, engine):

    from pathlib import Path

    client.post(
        "/analyze",
        files={"audio": ("consultation.wav", b"fake audio", "audio/wav")},
    )

    assert not Path(engine.calls[0]).exists()


def test_analyze_reports_pipeline_failure_as_500(client, engine):

    def explode(audio_path):
        raise RuntimeError("model exploded")

    engine.process_audio = explode

    response = client.post(
        "/analyze",
        files={"audio": ("consultation.wav", b"fake audio", "audio/wav")},
    )

    assert response.status_code == 500


# ==========================================================
# Reports
# ==========================================================

def test_list_reports(client):

    client.post(
        "/analyze",
        files={"audio": ("a.wav", b"x", "audio/wav")},
    )

    response = client.get("/reports")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["patient_name"] == "Lakshmi"


def test_list_reports_filters_by_risk_level(client):

    client.post(
        "/analyze",
        files={"audio": ("a.wav", b"x", "audio/wav")},
    )

    assert len(client.get("/reports?risk_level=High").json()) == 1
    assert len(client.get("/reports?risk_level=Low").json()) == 0


def test_list_reports_filters_by_name(client):

    client.post(
        "/analyze",
        files={"audio": ("a.wav", b"x", "audio/wav")},
    )

    assert len(client.get("/reports?name=aksh").json()) == 1
    assert len(client.get("/reports?name=Ravi").json()) == 0


def test_get_report_detail(client):

    client.post(
        "/analyze",
        files={"audio": ("a.wav", b"x", "audio/wav")},
    )

    response = client.get("/reports/1")

    assert response.status_code == 200

    body = response.json()

    assert body["patient_name"] == "Lakshmi"
    assert body["detected_language"] == "te"
    assert body["english_transcript"].startswith("My name is")


def test_get_missing_report_is_404(client):

    assert client.get("/reports/999").status_code == 404


def test_delete_report(client):

    client.post(
        "/analyze",
        files={"audio": ("a.wav", b"x", "audio/wav")},
    )

    assert client.delete("/reports/1").status_code == 200
    assert client.get("/reports/1").status_code == 404


def test_delete_missing_report_is_404(client):

    assert client.delete("/reports/999").status_code == 404


# ==========================================================
# PDF
# ==========================================================

def test_download_report_pdf(client):

    client.post(
        "/analyze",
        files={"audio": ("a.wav", b"x", "audio/wav")},
    )

    response = client.get("/reports/1/pdf")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert (
        "carevoice_report_1.pdf"
        in response.headers["content-disposition"]
    )
    assert response.content.startswith(b"%PDF-")


def test_pdf_for_missing_report_is_404(client):

    assert client.get("/reports/999/pdf").status_code == 404
