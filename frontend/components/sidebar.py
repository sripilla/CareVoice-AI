"""
Sidebar component for CareVoice AI.
"""

import streamlit as st


def render_sidebar():
    """
    Render the application sidebar.

    Returns
    -------
    str
        Selected page.
    """

    with st.sidebar:

        st.title("🏥 CareVoice AI")

        st.caption("Clinical Speech Analysis")

        st.divider()

        page = st.radio(
            "Navigation",
            [
                "🏠 New Consultation",
                "📋 Report History",
                "ℹ️ About"
            ]
        )

        st.divider()

        st.success("🟢 System Ready")

        st.caption("Version 1.0")

    return page