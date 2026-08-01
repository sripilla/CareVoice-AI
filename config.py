"""
Central configuration for CareVoice AI.
Modify project-wide settings here.
"""

from pathlib import Path

# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "uploads"
DATABASE_PATH = BASE_DIR / "database" / "carevoice.db"
REPORTS_DIR = BASE_DIR / "reports"

DEFAULT_AUDIO_FILE = (
    BASE_DIR / "data" / "raw_audio" / "telugu" / "TE001.wav"
)

# ==========================================================
# Application
# ==========================================================

APP_NAME = "CareVoice AI API"
APP_DESCRIPTION = "AI-powered multilingual clinical assistant"
APP_VERSION = "1.0.0"

# ==========================================================
# Logging
# ==========================================================

LOG_LEVEL = "INFO"

LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ==========================================================
# Speech Recognition (Whisper)
# ==========================================================

WHISPER_MODEL = "large-v3"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"

DEFAULT_BEAM_SIZE = 5
DEFAULT_TEMPERATURE = 0.0
DEFAULT_VAD_FILTER = False
DEFAULT_CONDITION_ON_PREVIOUS_TEXT = False

# ==========================================================
# Translation (NLLB)
# ==========================================================

TRANSLATION_MODEL = "facebook/nllb-200-distilled-600M"

DEFAULT_TARGET_LANGUAGE = "eng_Latn"

MAX_TRANSLATION_LENGTH = 512

# Whisper language code -> NLLB language code

LANGUAGE_MAP = {
    "te": "tel_Telu",
    "kn": "kan_Knda",
    "hi": "hin_Deva",
    "ta": "tam_Taml",
    "ml": "mal_Mlym",
    "mr": "mar_Deva",
    "bn": "ben_Beng",
    "gu": "guj_Gujr",
    "pa": "pan_Guru",
    "ur": "urd_Arab",
}

# ==========================================================
# Summarization (BART)
# ==========================================================

SUMMARIZER_MODEL = "facebook/bart-large-cnn"

SUMMARY_MAX_INPUT_LENGTH = 1024
SUMMARY_MAX_LENGTH = 80
SUMMARY_MIN_LENGTH = 30
SUMMARY_NUM_BEAMS = 4

# ==========================================================
# Translation Cleanup
# ==========================================================

UNWANTED_TRANSLATION_PHRASES = [
    "during the appendix",
    "I drink only coughing",
    "I am drinking rum",
]

# ==========================================================
# Medical Extraction
# ==========================================================

DISEASE_MAP = {
    "blood pressure": "Hypertension",
    "high blood pressure": "Hypertension",
    "hypertension": "Hypertension",
    "diabetes": "Diabetes",
    "asthma": "Asthma",
}

BP_MEDICATIONS = {
    "blood pressure medicine",
    "bp medicine",
}

# ==========================================================
# Risk Assessment
# ==========================================================

AGE_RISK_THRESHOLD = 60
AGE_RISK_SCORE = 1

SYMPTOM_RISK_SCORES = {
    "fever": 1,
    "cough": 1,
    "breathlessness": 2,
}

CONDITION_RISK_SCORES = {
    "Diabetes": 1,
    "Hypertension": 1,
}

LOW_RISK_MAX = 1
MEDIUM_RISK_MAX = 3

# ==========================================================
# Report Generation
# ==========================================================

REPORT_TITLE = "CAREVOICE AI CLINICAL REPORT"

REPORT_SEPARATOR = "=" * 60
REPORT_SUB_SEPARATOR = "-" * 60

REPORT_DATE_FORMAT = "%d-%m-%Y %H:%M"

# ==========================================================
# Database
# ==========================================================

DATABASE_TIMESTAMP_FORMAT = "%d-%m-%Y %H:%M"

# ==========================================================
# API
# ==========================================================

SUPPORTED_AUDIO_EXTENSIONS = {
    ".wav",
}