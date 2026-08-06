"""
Central configuration for CareVoice AI.

Values here are the defaults. Anything read through ``_env`` can be
overridden with an environment variable or an entry in a local ``.env``
file (see ``.env.example``) without editing this module.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


def _env(name: str, default: str) -> str:
    """
    Read an environment override, falling back to the default.
    """

    value = os.getenv(name)

    return value if value else default


# ==========================================================
# Project Paths
# ==========================================================

UPLOAD_DIR = BASE_DIR / "uploads"

DATABASE_PATH = Path(
    _env(
        "CAREVOICE_DATABASE_PATH",
        str(BASE_DIR / "database" / "carevoice.db"),
    )
)

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

# Base URL the Streamlit dashboard uses to reach the FastAPI backend.
API_URL = _env(
    "CAREVOICE_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

# The dashboard waits this long for /analyze. Measured: the bundled
# 30-second Telugu sample takes ~320s end to end with large-v3 on
# CPU, so the ceiling needs generous headroom for real consultations.
# Lower it on a GPU box, where the same run takes seconds.
API_TIMEOUT_SECONDS = float(
    _env("CAREVOICE_API_TIMEOUT", "1800")
)

# ==========================================================
# Logging
# ==========================================================

LOG_LEVEL = "INFO"

LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ==========================================================
# Compute
# ==========================================================

# "auto" picks cuda -> mps -> cpu. Override with cuda / mps / cpu.
DEVICE = _env("CAREVOICE_DEVICE", "auto")

# "auto" resolves per-device in utils.device.resolve_dtype:
# cuda -> float16, mps -> float32, cpu -> float32.
DTYPE = _env("CAREVOICE_DTYPE", "auto")

# ==========================================================
# Pipeline Selection
# ==========================================================

# Which speech-to-English front end the engine uses.
#
#   cascade  Whisper -> NLLB. The original two-stage design. An ASR
#            slip becomes a confidently wrong English phrase, because
#            the translator cannot tell corrupt input from good.
#
#   seamless SeamlessM4T v2 translates speech straight to English.
#            There is no intermediate transcript to corrupt, which is
#            the failure this project actually hit.
#
#   indic    Whisper -> IndicTrans2. Keeps the two stages but uses a
#            translator purpose-built for Indian languages.
#            IndicTrans2 is a gated Hugging Face repo: accept the
#            terms on its model page and set HF_TOKEN.
#
PIPELINE = _env("CAREVOICE_PIPELINE", "cascade")

# ==========================================================
# Speech Recognition (Whisper)
# ==========================================================

# "medium" keeps CPU inference and the first-run download tolerable.
# Accuracy on Indian languages is noticeably better with "large-v3" --
# set CAREVOICE_WHISPER_MODEL=large-v3 for demos and evaluation.
WHISPER_MODEL = _env("CAREVOICE_WHISPER_MODEL", "medium")

# "auto" follows CAREVOICE_DEVICE. Note that CTranslate2 has no Metal
# backend, so this resolves to CPU on Apple Silicon regardless.
WHISPER_DEVICE = _env("CAREVOICE_WHISPER_DEVICE", "auto")

WHISPER_COMPUTE_TYPE = _env(
    "CAREVOICE_WHISPER_COMPUTE_TYPE",
    "int8",
)

DEFAULT_BEAM_SIZE = 5
DEFAULT_TEMPERATURE = 0.0
DEFAULT_VAD_FILTER = False
DEFAULT_CONDITION_ON_PREVIOUS_TEXT = False

# Whisper sometimes misdetects Indian-language audio as English and
# emits a romanized transliteration instead of native script. When a
# transcript detected as "en" fails the English heuristic
# (utils/language.py), transcription is retried with this language
# forced so the translator receives native-script text.
PRIMARY_AUDIO_LANGUAGE = _env("CAREVOICE_PRIMARY_LANGUAGE", "te")

# Minimum fraction of common-English tokens for a transcript to be
# accepted as English.
ENGLISH_WORD_RATIO_THRESHOLD = 0.35

# ==========================================================
# Translation (NLLB)
# ==========================================================

TRANSLATION_MODEL = "facebook/nllb-200-distilled-600M"

DEFAULT_TARGET_LANGUAGE = "eng_Latn"

MAX_TRANSLATION_LENGTH = 512

# NLLB truncates anything past its input window, which would silently
# drop most of a real consultation. Transcripts longer than this are
# split on sentence boundaries and translated chunk by chunk.
TRANSLATION_CHUNK_CHARS = 400

# ==========================================================
# SeamlessM4T (direct speech -> English)
# ==========================================================

SEAMLESS_MODEL = _env(
    "CAREVOICE_SEAMLESS_MODEL",
    "facebook/seamless-m4t-v2-large",
)

# SeamlessM4T returns no language ID, but the clinical report shows
# the detected language and the native-script transcript needs a
# target language. A tiny Whisper handles detection in about a second
# and costs ~75 MB, which is cheaper than any alternative.
LANGID_MODEL = _env("CAREVOICE_LANGID_MODEL", "tiny")

# Also transcribe in the source language so the clinician can check
# the original words. Costs a second generation pass; set
# CAREVOICE_SEAMLESS_NATIVE=0 to skip it.
SEAMLESS_NATIVE_TRANSCRIPT = _env(
    "CAREVOICE_SEAMLESS_NATIVE",
    "1",
) not in ("0", "false", "False")

# Whisper language code -> SeamlessM4T language code.
SEAMLESS_LANGUAGE_MAP = {
    "te": "tel",
    "kn": "kan",
    "hi": "hin",
    "ta": "tam",
    "ml": "mal",
    "mr": "mar",
    "bn": "ben",
    "gu": "guj",
    "pa": "pan",
    "ur": "urd",
    "en": "eng",
}

# ==========================================================
# IndicTrans2
# ==========================================================

INDICTRANS2_MODEL = _env(
    "CAREVOICE_INDICTRANS2_MODEL",
    "ai4bharat/indictrans2-indic-en-dist-200M",
)

# Whisper language code -> IndicTrans2 (FLORES-style) code.
INDICTRANS2_LANGUAGE_MAP = {
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

MEDICAL_DISCLAIMER = (
    "Research prototype for clinical decision support only. "
    "This is not a medical device. All output is machine generated "
    "and must be reviewed by a qualified clinician before use."
)

# ==========================================================
# PDF Report
# ==========================================================

# ReportLab ships only Latin-1 base fonts, so an Indic-capable TrueType
# font must be registered to render the original-script transcript.
# Nirmala UI covers Telugu, Devanagari, Tamil, Kannada and more.
# Note: ReportLab does not perform OpenType complex-script shaping, so
# conjuncts render imperfectly. The English report is unaffected.
INDIC_FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/Nirmala.ttc"),
    Path("C:/Windows/Fonts/NirmalaUI.ttf"),
    Path("/usr/share/fonts/truetype/lohit-telugu/Lohit-Telugu.ttf"),
    Path("/System/Library/Fonts/Supplemental/Kohinoor.ttc"),
]

INDIC_FONT_NAME = "CareVoiceIndic"

RISK_COLORS = {
    "Low": "#1a7f37",
    "Medium": "#bf8700",
    "High": "#cf222e",
}

# ==========================================================
# Database
# ==========================================================

DATABASE_TIMESTAMP_FORMAT = "%d-%m-%Y %H:%M"

# ==========================================================
# API
# ==========================================================

# faster-whisper decodes through PyAV, so every container ffmpeg
# understands works without a separate conversion step. Browser
# recordings arrive as .wav or .webm depending on the client.
SUPPORTED_AUDIO_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".ogg",
    ".webm",
    ".flac",
}

MAX_UPLOAD_BYTES = 100 * 1024 * 1024

# Uploads are deleted after processing by default (they are patient
# audio). Set CAREVOICE_KEEP_UPLOADS=1 while evaluating models, so the
# same recording can be replayed through different pipelines.
KEEP_UPLOADS = _env("CAREVOICE_KEEP_UPLOADS", "") not in (
    "",
    "0",
    "false",
    "False",
)