import streamlit as st


def render_risk():
    """
    Display patient risk assessment.
    """

    st.subheader("⚠️ Risk Assessment")

    report = st.session_state.get("report", {})
    risk = report.get("risk", {})

    risk_score = risk.get("risk_score", "-")
    risk_level = risk.get("risk_level", "-")

    st.metric(
        label="Risk Score",
        value=risk_score,
    )

    st.metric(
        label="Risk Level",
        value=risk_level,
    )