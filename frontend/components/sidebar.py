"""
Sidebar component for CareVoice AI.
"""

import streamlit as st

from frontend.constants import (
    APP_TITLE,
    APP_SUBTITLE,
    APP_VERSION,
    PAGES,
)


def render_sidebar():
    """
    Render the application sidebar.

    Returns
    -------
    tuple
        (selected_page, show_processing_details)
    """

    with st.sidebar:

        # ---------------------------------------------------------
        # Branding
        # ---------------------------------------------------------

        st.title(APP_TITLE)
        st.caption(APP_SUBTITLE)
        st.caption(f"Version {APP_VERSION}")

        st.divider()

        # ---------------------------------------------------------
        # Navigation
        # ---------------------------------------------------------

        st.subheader("🧭 Navigation")

        page = st.radio(
            label="",
            options=PAGES,
            label_visibility="collapsed",
        )

        st.divider()

        # ---------------------------------------------------------
        # Processing Details
        # ---------------------------------------------------------

        st.subheader("⚙️ Settings")

        show_processing_details = st.checkbox(
            "Show Processing Details",
            value=False,
            help="Display the internal AI pipeline used during analysis.",
        )

        st.divider()

        # ---------------------------------------------------------
        # System Status
        # ---------------------------------------------------------

        st.subheader("📊 Status")

        st.success("🟢 System Ready")

        st.caption(
            "All AI services are available."
        )

        st.divider()

        st.caption("Developed for the NLP Minor Specialisation")

    return page, show_processing_details