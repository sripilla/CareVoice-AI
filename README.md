# 🏥 CareVoice AI
### Multilingual Clinical Speech Analysis and Intelligent Report Generation

<p align="center">

AI-powered healthcare assistant that converts multilingual patient speech into structured clinical reports using Speech Recognition, Machine Translation, Natural Language Processing, and Deep Learning.

</p>

---

# 📌 Project Overview

CareVoice AI is an end-to-end AI-powered healthcare application designed to assist in processing multilingual clinical conversations.

The system accepts patient audio recordings in multiple Indian languages, automatically detects the spoken language, transcribes the speech into text, translates it into English, extracts important medical information, summarizes the conversation, assesses clinical risk, generates a structured clinical report, and stores the report for future retrieval through REST APIs.

This project demonstrates the integration of modern AI and NLP technologies including:

- Speech Recognition
- Machine Translation
- Natural Language Processing
- Deep Learning for Text Summarization
- Clinical Information Extraction
- REST API Development
- Database Integration

---

# 🎯 Objectives

- Convert multilingual patient speech into text.
- Automatically detect the spoken language.
- Translate conversations into English.
- Extract clinical entities such as:
  - Symptoms
  - Medical Conditions
  - Medications
  - Duration
  - Patient Information
- Generate concise clinical summaries.
- Perform patient risk assessment.
- Generate structured clinical reports.
- Store reports in a SQLite database.
- Provide REST APIs for report management.

---

# ✨ Features

- 🎙 Multilingual Speech Recognition
- 🔴 In-browser Microphone Recording
- 🌍 Automatic Language Detection
- 🌐 English Translation
- 🩺 Medical Entity Extraction
- 📝 Clinical Text Summarization
- ⚠️ Rule-based Risk Assessment
- 📄 Clinical Report Generation
- 🖨 PDF Report Download
- 🖥 Streamlit Clinician Dashboard
- 🔎 Report History Search & Filtering
- 💾 SQLite Database Storage
- ⚡ FastAPI REST API
- 📚 Interactive Swagger Documentation

Everything runs **locally**. No API keys, and no audio, transcript or
patient data leaves the machine.

---

# ⚠️ Medical Disclaimer

CareVoice AI is a **research prototype for clinical decision support
only. It is not a medical device.** Every output — transcript,
translation, summary, extracted entities and risk score — is machine
generated and must be reviewed by a qualified clinician before it is
relied upon. See [Known Limitations](#-known-limitations).

---

# 🤖 AI Models Used

| Stage | Model |
|--------|-------|
| Speech Recognition | Faster-Whisper (`medium` default, `large-v3` optional) |
| Language Detection | Whisper Built-in Language Detection |
| Machine Translation | Meta NLLB-200 Distilled 600M |
| Clinical Summarization | Facebook BART Large CNN |
| Medical NLP | spaCy (`en_core_web_sm`) + EntityRuler |
| Risk Assessment | Rule-Based Clinical Engine |
| Report Generation | Template-Based Generator |

---

# 🏗 System Architecture

```text
          Patient Audio (recorded live or uploaded)
                            │
                            ▼
         Faster-Whisper (Speech Recognition)
                            │
                            ▼
                Automatic Language Detection
                            │
                            ▼
             NLLB-200 Machine Translation
                            │
                            ▼
                  English Transcript
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
     spaCy + EntityRuler          BART Summarizer
  Medical Entity Extraction      Clinical Summary
                │                       │
                └───────────┬───────────┘
                            ▼
                 Rule-Based Risk Assessment
                            ▼
                 Clinical Report Generator
                            ▼
                     SQLite Database
                            ▼
                      FastAPI REST API
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
     Streamlit Dashboard (UI)      PDF Report Download
```

---

# 🛠 Technology Stack

## Programming Language

- Python 3.11+

## Speech Processing

- Faster-Whisper
- CTranslate2

## Machine Translation

- Meta NLLB-200 Distilled 600M

## Natural Language Processing

- spaCy
- EntityRuler

## Deep Learning

- Facebook BART Large CNN

## Backend

- FastAPI
- Uvicorn
- Pydantic

## Database

- SQLite

## Frontend (MVP)

- Streamlit

---

# 📁 Project Structure

```text
CareVoice-AI/
│
├── api/
│   ├── app.py               FastAPI app factory
│   ├── routes.py            REST endpoints
│   └── schemas.py           Pydantic request/response models
│
├── careinsight/
│   ├── engine.py            Pipeline orchestrator
│   ├── extractor.py         spaCy clinical entity extraction
│   ├── medical_patterns.py  EntityRuler patterns
│   ├── report_generator.py  Text report template
│   ├── risk_assessor.py     Rule-based risk scoring
│   └── summarizer.py        BART summarization
│
├── database/
│   └── database.py          SQLite manager + schema migration
│
├── speech/
│   └── transcriber.py       Faster-Whisper speech recognition
│
├── translation/
│   └── translator.py        NLLB-200 translation
│
├── frontend/
│   └── streamlit_app.py     Clinician dashboard (API client)
│
├── utils/
│   ├── logger.py            Central logging
│   └── pdf.py               PDF report rendering (ReportLab)
│
├── scripts/                 Ad-hoc module demos
├── tests/                   pytest suite
│
├── data/raw_audio/          Sample recordings
│
├── config.py                All settings, env-overridable
├── main.py                  CLI entrypoint
├── pytest.ini
├── .env.example
├── requirements.txt
└── README.md
```

`uploads/`, `reports/` and `database/carevoice.db` are created at
runtime and are git-ignored.

---

# 🚀 Workflow

1. Record the consultation in the dashboard, or upload audio.
2. Speech-to-Text using Faster-Whisper.
3. Detect spoken language.
4. Translate transcript into English.
5. Generate clinical summary.
6. Extract medical entities.
7. Assess patient risk.
8. Generate clinical report.
9. Store report in SQLite.
10. Review in the dashboard and download the PDF.

---

# 📡 REST API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Health Check |
| POST | `/analyze` | Analyze uploaded audio |
| GET | `/reports` | Retrieve reports (`?name=`, `?risk_level=`) |
| GET | `/reports/{id}` | Retrieve a report |
| GET | `/reports/{id}/pdf` | Download a report as PDF |
| DELETE | `/reports/{id}` | Delete a report |

Accepted audio formats: `.wav`, `.mp3`, `.m4a`, `.ogg`, `.webm`,
`.flac` (decoded through PyAV, so no manual conversion is needed).

---

# 📥 Example Input

Patient speaks in Telugu:

> నాకు మూడు రోజులుగా జ్వరం ఉంది. దగ్గు కూడా ఉంది.

---

# 📤 Example Output

```json
{
  "report_id": 12,
  "detected_language": "te",
  "language_probability": 0.98,
  "english_transcript": "I have had a fever for three days. I also have a cough.",
  "summary": "Patient reports fever and cough for three days.",
  "patient": {
    "patient_name": "Lakshmi",
    "age": 70,
    "symptoms": [
      "cough",
      "fever"
    ],
    "conditions": [
      "Hypertension",
      "Diabetes"
    ],
    "medications": [
      "medication"
    ],
    "duration": "three days"
  },
  "risk": {
    "risk_score": 5,
    "risk_level": "High"
  },
  "warnings": []
}
```

Use `report_id` to fetch the formatted PDF:
`GET /reports/12/pdf`.

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/<your-username>/CareVoice-AI.git
cd CareVoice-AI
```

---

## Create Virtual Environment

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

`en_core_web_sm` is pinned in `requirements.txt`, so no separate
`spacy download` step is needed.

### Windows prerequisite

PyTorch and CTranslate2 ship native libraries that require the
**Microsoft Visual C++ Redistributable**. Without it, importing
`torch` fails with `OSError: [WinError 126] ... c10.dll`. Install it
once:

```powershell
winget install --id Microsoft.VCRedist.2015+.x64
```

or download [vc_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe).

---

# ⚙️ Configuration

All settings live in `config.py` with working defaults. Anything you
want to change per machine can be set as an environment variable or in
a local `.env` file — copy `.env.example` to `.env` to start.

| Variable | Default | Purpose |
|---|---|---|
| `CAREVOICE_PIPELINE` | `cascade` | Speech→English backend: `cascade`, `seamless` or `indic` |
| `CAREVOICE_DEVICE` | `auto` | `auto` picks cuda → mps → cpu |
| `CAREVOICE_DTYPE` | `auto` | float16 on CUDA, float32 on MPS/CPU |
| `CAREVOICE_WHISPER_MODEL` | `medium` | Whisper size; use `large-v3` for best accuracy |
| `CAREVOICE_WHISPER_DEVICE` | `cpu` | `cpu` or `cuda` |
| `CAREVOICE_WHISPER_COMPUTE_TYPE` | `int8` | `int8` for CPU, `float16` for CUDA |
| `CAREVOICE_DATABASE_PATH` | `database/carevoice.db` | SQLite location |
| `CAREVOICE_API_URL` | `http://127.0.0.1:8000` | Where the dashboard finds the API |
| `CAREVOICE_API_TIMEOUT` | `1800` | Seconds the dashboard waits for `/analyze` |

The default Whisper model is `medium` to keep CPU inference and the
first-run download manageable. **`large-v3` is meaningfully more
accurate on Telugu, Kannada and other Indian languages** — use it for
demos and any accuracy evaluation:

```bash
CAREVOICE_WHISPER_MODEL=large-v3 uvicorn api.app:app
```

---

# 🔀 Pipeline Backends

The stages after translation — summarization, entity extraction, risk
scoring, reporting — all operate on English text and don't care how
that English was produced. So the speech front end is swappable:

| `CAREVOICE_PIPELINE` | Stack | Notes |
|---|---|---|
| `cascade` *(default)* | Whisper → NLLB | Two stages. An ASR slip becomes a confidently wrong English phrase, because the translator can't tell corrupt input from good. |
| `seamless` | SeamlessM4T v2, speech → English directly | **Recommended for Indian languages.** No intermediate transcript, so no compounding error. Runs on MPS/CUDA. |
| `indic` | Whisper → IndicTrans2 | Better translator, still a cascade. IndicTrans2 is a **gated** HF repo — accept its terms while signed in, then set `HF_TOKEN`. |

## Why this matters

A patient said *"I have had a headache for two days."* The cascade
produced:

```
Telugu speech
  → ASR heard  రెండ్ రోల్       (not a word — "two days" mangled)
  → NLLB wrote "the Red Roll"   (fluent, confident, wrong)
```

Downstream, zero symptoms were extracted and the patient was scored
**Low** risk. The same speaker in English was scored correctly. The
`seamless` backend removes the step where a mis-spelt Telugu word can
be re-read as an unrelated English one.

## Comparing them

```bash
python -m scripts.benchmark_models --list
python -m scripts.benchmark_models --audio your_recording.wav \
    --candidates cascade,seamless-pipeline
```

The benchmark drives the real pipeline classes, so whichever wins is
adopted by setting `CAREVOICE_PIPELINE` — no code change.

To keep a recording for repeat testing (uploads are deleted after
processing by default, since they're patient audio):

```bash
CAREVOICE_KEEP_UPLOADS=1 uvicorn api.app:app
```

---

# 🍎 Apple Silicon

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-mac.txt

export PYTORCH_ENABLE_MPS_FALLBACK=1     # required: MPS lacks some ops
export CAREVOICE_PIPELINE=seamless       # GPU-accelerated speech
```

**Note:** CTranslate2 — which powers faster-whisper — has **no Metal
backend**, so the `cascade` pipeline runs on CPU on macOS no matter
what `CAREVOICE_DEVICE` says. That's a library limitation, not a
tuning choice. The `seamless` and `indic` backends use PyTorch and do
run on the GPU.

---

# ▶️ Running the Project

The dashboard is a thin HTTP client over the API, so **start the
backend first**. Running them as separate processes is deliberate:
the models load once, in the API process only.

## 1. FastAPI Backend

```bash
uvicorn api.app:app --reload
```

First start downloads several GB of model weights and takes a while.

## 2. Streamlit Dashboard

In a second terminal:

```bash
streamlit run frontend/streamlit_app.py
```

Then record or upload a consultation, review the extracted findings
and risk level, and download the PDF.

## Command Line (no server)

```bash
python main.py
```

Runs the pipeline against the bundled sample recording.

---

# 📖 API Documentation

After starting FastAPI:

### Swagger UI

```
http://127.0.0.1:8000/docs
```

### ReDoc

```
http://127.0.0.1:8000/redoc
```

---

# 📊 Sample Pipeline

```text
Audio
   │
   ▼
Speech Recognition
   │
   ▼
Translation
   │
   ▼
Summarization
   │
   ▼
Medical Entity Extraction
   │
   ▼
Risk Assessment
   │
   ▼
Clinical Report
   │
   ▼
SQLite Storage
```

---

# 🧪 Testing

```bash
pytest
```

The default run covers risk scoring, persistence and its schema
migration, the text report, PDF rendering, every API endpoint (against
a stub engine) and the Streamlit dashboard (via `AppTest`). It loads no
model weights and finishes in seconds.

The end-to-end pipeline test is marked `slow` and excluded by default
because it loads Whisper, NLLB and BART:

```bash
pytest -m slow
```

Tests whose native dependencies are unavailable are **skipped with a
visible reason** rather than failing the run — if you see skips
mentioning `c10.dll`, install the Visual C++ Redistributable described
above.

Ad-hoc single-module demos live in `scripts/`. Run them as modules
from the repository root so the package imports resolve:

```bash
python -m scripts.demo_risk
python -m scripts.demo_translation
```

---

# 📌 Known Limitations

These are real constraints, not TODOs hidden in the code:

- **Summarization** uses `bart-large-cnn`, a *news* summarization
  model. Summaries read fluently but are not clinically validated —
  this is the weakest link in the pipeline.
- **Entity extraction** relies on ~35 hand-written EntityRuler patterns
  in `careinsight/medical_patterns.py`. Anything outside that
  vocabulary is missed. Moving to scispaCy/medspaCy is the
  highest-value upgrade available.
- **Risk scoring** is a simple additive rule set, not a validated
  clinical risk model.
- **Transcription accuracy** scales with Whisper model size; the
  default `medium` trades accuracy for speed.
- **Unsupported languages** degrade rather than fail: the transcript is
  passed through untranslated and the response carries a `warnings`
  entry noting that the downstream analysis is unreliable.
- **PDF Indic rendering** — ReportLab does not perform OpenType
  complex-script shaping, so the original-language transcript appendix
  renders conjuncts imperfectly. The English report is unaffected, and
  the dashboard displays the original script correctly.

---

# 🔮 Future Enhancements

- Clinical-domain summarization model
- scispaCy / medspaCy entity extraction
- Electronic Health Record (EHR) Integration
- Medical Question Answering using RAG
- Cloud Deployment (Docker + AWS/Azure)
- Authentication & Role-Based Access
- Machine Learning-Based Risk Prediction

---

# 📚 References

- Faster-Whisper
- Meta NLLB-200
- Facebook BART
- spaCy
- FastAPI
- SQLite
- Hugging Face Transformers
- PyTorch

---

# 📄 License

This project was developed for academic purposes as part of the **Natural Language Processing Minor Specialisation**.

---

## ⭐ Acknowledgements

This project integrates open-source AI models and frameworks including:

- OpenAI Whisper
- Faster-Whisper
- Meta AI
- Hugging Face
- spaCy
- FastAPI Community

---
