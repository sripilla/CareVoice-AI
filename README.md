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
- 🌍 Automatic Language Detection
- 🌐 English Translation
- 🩺 Medical Entity Extraction
- 📝 Clinical Text Summarization
- ⚠️ Rule-based Risk Assessment
- 📄 Clinical Report Generation
- 💾 SQLite Database Storage
- ⚡ FastAPI REST API
- 📚 Interactive Swagger Documentation

---

# 🤖 AI Models Used

| Stage | Model |
|--------|-------|
| Speech Recognition | Faster-Whisper (large-v3) |
| Language Detection | Whisper Built-in Language Detection |
| Machine Translation | Meta NLLB-200 Distilled 600M |
| Clinical Summarization | Facebook BART Large CNN |
| Medical NLP | spaCy (`en_core_web_sm`) + EntityRuler |
| Risk Assessment | Rule-Based Clinical Engine |
| Report Generation | Template-Based Generator |

---

# 🏗 System Architecture

```text
                    Patient Audio (.wav)
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
                            ▼
                 Streamlit Dashboard (UI)
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
│   ├── __init__.py
│   ├── app.py
│   ├── routes.py
│   └── schemas.py
│
├── backend/
│
├── careinsight/
│   ├── engine.py
│   ├── extractor.py
│   ├── medical_patterns.py
│   ├── report_generator.py
│   ├── risk_assessor.py
│   └── summarizer.py
│
├── database/
│   ├── database.py
│   └── carevoice.db
│
├── speech/
│   └── transcriber.py
│
├── translation/
│   └── translator.py
│
├── frontend/
│   └── streamlit_app.py
│
├── utils/
│   ├── logger.py
│   └── pdf.py
│
├── data/
│   ├── raw_audio/
│   ├── transcripts/
│   └── metadata/
│
├── uploads/
├── reports/
├── tests/
│
├── config.py
├── main.py
├── requirements.txt
└── README.md
```

---

# 🚀 Workflow

1. Upload multilingual patient audio.
2. Speech-to-Text using Faster-Whisper.
3. Detect spoken language.
4. Translate transcript into English.
5. Generate clinical summary.
6. Extract medical entities.
7. Assess patient risk.
8. Generate clinical report.
9. Store report in SQLite.
10. Return report via FastAPI.

---

# 📡 REST API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Health Check |
| POST | `/analyze` | Analyze uploaded audio |
| GET | `/reports` | Retrieve all reports |
| GET | `/reports/{id}` | Retrieve a report |
| DELETE | `/reports/{id}` | Delete a report |

---

# 📥 Example Input

Patient speaks in Telugu:

> నాకు మూడు రోజులుగా జ్వరం ఉంది. దగ్గు కూడా ఉంది.

---

# 📤 Example Output

```json
{
  "detected_language": "te",
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
  }
}
```

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

---

# ▶️ Running the Project

## Command Line

```bash
python main.py
```

---

## FastAPI Backend

```bash
uvicorn api.app:app --reload
```

---

## Streamlit Frontend

```bash
streamlit run frontend/streamlit_app.py
```

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

The project includes individual test scripts for validating each module.

```text
test_translation.py
test_summary.py
test_extractor.py
test_risk.py
test_database.py
```

---

# 👥 Team Responsibilities

### Member 1

- Speech Recognition
- Language Detection
- Machine Translation

### Member 2

- Medical Entity Extraction
- Clinical Summarization

### Member 3

- Risk Assessment
- Clinical Report Generation
- Database Integration
- FastAPI Development

---

# 🔮 Future Enhancements

- Streamlit Dashboard
- PDF Report Download
- Doctor Dashboard
- Patient History Search
- Electronic Health Record (EHR) Integration
- Medical Question Answering using RAG
- Clinical Decision Support using LLMs
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
