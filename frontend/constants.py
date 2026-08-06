"""
Application constants for the Streamlit frontend.
"""

# --------------------------------------------------
# Application Information
# --------------------------------------------------

APP_TITLE = "🏥 CareVoice AI"

APP_SUBTITLE = "Multilingual Clinical Speech Analysis"

APP_VERSION = "1.0"


# --------------------------------------------------
# Navigation
# --------------------------------------------------

PAGE_NEW_CONSULTATION = "🏠 New Consultation"

PAGE_REPORT_HISTORY = "📋 Report History"

PAGE_ABOUT = "ℹ️ About"

PAGES = [
    PAGE_NEW_CONSULTATION,
    PAGE_REPORT_HISTORY,
    PAGE_ABOUT,
]


# --------------------------------------------------
# UI Labels
# --------------------------------------------------

UPLOAD_SECTION_TITLE = "🎙 Upload Patient Audio"

TRANSCRIPT_TITLE = "📝 Original Transcript"

TRANSLATION_TITLE = "🌐 English Translation"

SUMMARY_TITLE = "📄 AI Clinical Summary"

ENTITIES_TITLE = "🩺 Medical Information"

RISK_TITLE = "⚠️ Risk Assessment"

REPORT_TITLE = "📋 Clinical Report"


# --------------------------------------------------
# Default Messages
# --------------------------------------------------

WAITING_MESSAGE = "Waiting for analysis..."

NO_REPORT_MESSAGE = "No report generated."