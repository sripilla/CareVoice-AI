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

        st.title(APP_TITLE)
        st.caption(APP_SUBTITLE)

        st.divider()

        page = st.radio(
            "Navigation",
            PAGES
        )

        st.divider()

        show_processing_details = st.checkbox(
            "Show Processing Details",
            value=False,
            help="Display the internal AI pipeline used during analysis."
        )

        st.divider()

        st.success("🟢 System Ready")
        st.caption(f"Version {APP_VERSION}")

    return page, show_processing_details