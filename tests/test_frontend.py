"""
Streamlit dashboard smoke tests.

AppTest executes the real script in-process, so these catch the
usual dashboard breakages -- a bad API call, a mis-keyed widget, a
crash on empty data -- without a browser or a running backend.
"""

import json

import pytest

from conftest import skip_without

skip_without("streamlit", "Streamlit unavailable on this host")

from streamlit.testing.v1 import AppTest  # noqa: E402

APP = "frontend/streamlit_app.py"


class FakeResponse:
    """
    Minimal stand-in for an httpx.Response.
    """

    def __init__(self, payload, content=b""):
        self._payload = payload
        self.content = content
        self.status_code = 200
        self.text = json.dumps(payload) if payload else ""

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


@pytest.fixture
def stored_report():

    return {
        "id": 1,
        "timestamp": "01-01-2026 10:00",
        "patient_name": "Lakshmi",
        "age": 70,
        "symptoms": "fever, cough",
        "conditions": "Hypertension",
        "medications": "bp medicine",
        "duration": "three days",
        "summary": "Patient reports fever and cough.",
        "risk_score": 5,
        "risk_level": "High",
        "clinical_report": "CAREVOICE AI CLINICAL REPORT",
        "detected_language": "te",
        "original_transcript": "నాకు జ్వరం ఉంది.",
        "english_transcript": "I have a fever.",
    }


@pytest.fixture
def offline_backend(monkeypatch):
    """
    Patch httpx so the dashboard sees an unreachable backend.

    Simulated rather than relying on nothing listening on the port:
    otherwise these tests pass or fail depending on whether someone
    happens to have the API running.
    """

    import httpx

    def refuse(url, **kwargs):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(httpx, "get", refuse)
    monkeypatch.setattr(httpx, "delete", refuse)
    monkeypatch.setattr(httpx, "post", refuse)


@pytest.fixture
def live_backend(monkeypatch, stored_report):
    """
    Patch httpx so the dashboard sees a healthy backend.
    """

    import httpx

    def fake_get(url, **kwargs):

        if url.endswith("/pdf"):
            return FakeResponse(None, content=b"%PDF-1.4 fake")

        if "/reports/" in url:
            return FakeResponse(stored_report)

        if url.endswith("/reports"):
            return FakeResponse(
                [
                    {
                        "id": 1,
                        "timestamp": "01-01-2026 10:00",
                        "patient_name": "Lakshmi",
                        "age": 70,
                        "risk_level": "High",
                    }
                ]
            )

        return FakeResponse(
            {"message": "Welcome", "status": "Running"}
        )

    monkeypatch.setattr(httpx, "get", fake_get)


# ==========================================================
# Backend offline
# ==========================================================

def test_runs_without_a_backend(offline_backend):
    """
    A clinician opening the dashboard before starting the API
    should get a clear message, not a stack trace.
    """

    app = AppTest.from_file(APP, default_timeout=60).run()

    assert not app.exception
    assert "Backend offline" in [
        error.value for error in app.sidebar.error
    ]


def test_history_page_reports_an_offline_backend(offline_backend):

    app = AppTest.from_file(APP, default_timeout=60).run()

    app.sidebar.radio[0].set_value("Report History").run()

    assert not app.exception
    assert any(
        "Cannot reach the CareVoice API" in error.value
        for error in app.error
    )


def test_about_page_renders_offline(offline_backend):

    app = AppTest.from_file(APP, default_timeout=60).run()

    app.sidebar.radio[0].set_value("About").run()

    assert not app.exception
    assert "About CareVoice AI" in [
        title.value for title in app.title
    ]

    # The clinical disclaimer must always be present.
    assert app.warning


# ==========================================================
# Backend online
# ==========================================================

def test_new_consultation_page_with_a_live_backend(live_backend):

    app = AppTest.from_file(APP, default_timeout=60).run()

    assert not app.exception
    assert "New Consultation" in [
        title.value for title in app.title
    ]
    assert app.sidebar.success


def test_history_page_lists_and_opens_a_report(live_backend):

    app = AppTest.from_file(APP, default_timeout=60).run()

    app.sidebar.radio[0].set_value("Report History").run()

    assert not app.exception
    assert not app.error

    # The selected report's details are rendered.
    metric_values = [metric.value for metric in app.metric]

    assert "Lakshmi" in metric_values


def test_history_page_filters_are_present(live_backend):

    app = AppTest.from_file(APP, default_timeout=60).run()

    app.sidebar.radio[0].set_value("Report History").run()

    assert len(app.text_input) == 1
    assert app.selectbox[0].options == [
        "All",
        "Low",
        "Medium",
        "High",
    ]
