import streamlit as st


def render_risk():
    """
    Display patient risk assessment.
    """

    st.subheader("⚠️ Risk Assessment")

    report = st.session_state.get("report", {})
    risk = report.get("risk", {})

    risk_score = risk.get("risk_score")
    risk_level = risk.get("risk_level", "").strip()

    if risk_score is None:
        st.info("No risk assessment available.")
        return

    # ---------------------------------------------------------
    # Risk Banner
    # ---------------------------------------------------------

    if risk_level.lower() == "high":
        st.error("🔴 HIGH RISK")
        recommendation = (
            "Immediate physician consultation recommended."
        )

    elif risk_level.lower() == "medium":
        st.warning("🟡 MEDIUM RISK")
        recommendation = (
            "Patient should be monitored closely."
        )

    else:
        st.success("🟢 LOW RISK")
        recommendation = (
            "Routine follow-up recommended."
        )

    # ---------------------------------------------------------
    # Risk Details
    # ---------------------------------------------------------

    st.metric(
        label="Risk Score",
        value=f"{risk_score} / 5",
    )

    st.metric(
        label="Risk Level",
        value=risk_level,
    )

    st.caption(recommendation)