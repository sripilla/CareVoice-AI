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

# Temperature fallback ladder: when a segment decodes with poor
# confidence or compression, retry at progressively higher
# temperatures instead of dropping the remaining audio.
DEFAULT_TEMPERATURE = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)

# Strip silence and pauses (common in microphone recordings)
# before decoding to avoid early stopping and hallucination.
DEFAULT_VAD_FILTER = True

DEFAULT_CONDITION_ON_PREVIOUS_TEXT = False

# ==========================================================
# Specialist ASR Models (Indic fine-tunes)
# ==========================================================
#
# Vanilla Whisper hears low-resource Indic speech but misspells
# it (e.g. Kannada "jvara"/fever), which breaks translation and
# entity extraction downstream. When Whisper detects one of the
# languages below, transcription is re-run with a per-language
# Whisper model fine-tuned on native speech corpora
# (IIT Madras Speech Lab). Other languages keep using the
# default multilingual model. Specialist models are downloaded
# and loaded lazily, only for languages actually encountered.

SPECIALIST_ASR_MODELS = {
    "kn": "vasista22/whisper-kannada-medium",
    "te": "vasista22/whisper-telugu-medium",
    "hi": "vasista22/whisper-hindi-medium",
}

# Chunk length (seconds) for specialist transcription of audio
# longer than Whisper's 30-second window.
SPECIALIST_CHUNK_LENGTH_S = 30

# The specialist fine-tunes ship a 2023-era generation config
# that current transformers versions reject when forcing the
# language. All of the models above are whisper-medium
# fine-tunes, and every medium-family Whisper model shares the
# same tokenizer and vocabulary, so the base model's modern
# generation config is a drop-in replacement at load time.
# NOTE: if a large-v3 based fine-tune is ever added, its base
# must be used instead (large-v3 has an extended vocabulary).
SPECIALIST_GENERATION_CONFIG_BASE = "openai/whisper-medium"

# ==========================================================
# Translation (NLLB)
# ==========================================================

TRANSLATION_MODEL = "facebook/nllb-200-distilled-600M"

DEFAULT_TARGET_LANGUAGE = "eng_Latn"

MAX_TRANSLATION_LENGTH = 512

# NLLB is a sentence-level model: long unpunctuated transcripts
# get partially dropped. Transcripts are split on sentence
# punctuation first; any sentence longer than this word count
# is further split into fixed-size chunks before translation.
TRANSLATION_CHUNK_MAX_WORDS = 25

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