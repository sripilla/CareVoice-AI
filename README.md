# 🏥 Multilingual Clinical Speech Analysis and Intelligent Report Generation

## 📌 Project Overview

This project is an AI-powered healthcare application that converts multilingual clinical speech into structured clinical reports.

The system accepts audio conversations in multiple Indian languages (such as Telugu, Hindi, Kannada, Tamil, and English), transcribes the speech into text, translates it into English, extracts important medical information, summarizes the conversation, assesses patient risk, generates a clinical report, and stores the report for future retrieval.

This project demonstrates the integration of **Speech Processing**, **Machine Translation**, **Natural Language Processing (NLP)**, **Deep Learning for NLP**, and **REST API Development**.

---

# 🎯 Objectives

* Convert multilingual speech into text.
* Detect the spoken language automatically.
* Translate conversations into English.
* Extract clinical entities such as symptoms, diseases, medications, and duration.
* Generate concise clinical summaries.
* Perform rule-based patient risk assessment.
* Generate structured clinical reports.
* Store reports in a database.
* Provide REST APIs for report management.

---

# 🎓  Requirements Covered

| Requirement                 | Module             |
| --------------------------- | ------------------ |
| Speech Processing           | Faster-Whisper     |
| Machine Translation         | IndicTrans2 / NLLB |
| Natural Language Processing | spaCy / SciSpaCy   |
| NLP with Deep Learning      | PEGASUS / BART     |
| Backend Development         | FastAPI            |
| Database                    | SQLite             |

---

# 🏗 System Architecture

```text
Patient Audio
      │
      ▼
Speech Recognition
      │
      ▼
Language Detection
      │
      ▼
Machine Translation
      │
      ▼
English Transcript
      │
 ┌────┴───────────┐
 ▼                ▼
Medical NLP    Deep Learning NLP
(Entity)       (Summarization)
      │            │
      └─────┬──────┘
            ▼
     Risk Assessment
            ▼
 Clinical Report Generator
            ▼
        SQLite Database
            ▼
        FastAPI REST API
```

---

# 🛠 Technology Stack

## Programming Language

* Python 3.11+

## Backend

* FastAPI
* Uvicorn

## Speech Processing

* Faster-Whisper (large-v3)

## Machine Translation

* IndicTrans2 *(preferred)*
* NLLB-200 *(alternative)*

## Natural Language Processing

* spaCy
* SciSpaCy
* EntityRuler

## Deep Learning NLP

* PEGASUS *(preferred)*
* BART *(alternative)*

## Database

* SQLite

## Report Generation

* Python Templates / Jinja2

---

# 📁 Project Structure

```text
MedicalSpeechAssistant/
│
├── main.py
├── config.py
├── requirements.txt
│
├── api/
│   ├── routes.py
│   └── schemas.py
│
├── speech/
│   └── transcriber.py
│
├── translation/
│   └── translator.py
│
├── nlp/
│   ├── entity_extractor.py
│   └── medical_patterns.json
│
├── summarization/
│   └── summarizer.py
│
├── risk/
│   └── risk_engine.py
│
├── report/
│   └── report_generator.py
│
├── database/
│   ├── database.py
│   └── models.py
│
├── data/
│   ├── raw_audio/
│   ├── transcripts/
│   └── reports/
│
└── tests/
```

---

# 🚀 Workflow

1. Upload multilingual patient audio.
2. Convert speech into text.
3. Detect spoken language.
4. Translate transcript into English.
5. Extract medical entities.
6. Generate clinical summary.
7. Perform risk assessment.
8. Generate structured report.
9. Store report in SQLite.
10. Return report through REST API.

---

# 📡 REST API Endpoints

| Method | Endpoint                        | Description                        |
| ------ | ------------------------------- | ---------------------------------- |
| POST   | `/api/v1/reports`               | Upload audio and generate a report |
| GET    | `/api/v1/reports`               | Retrieve all reports               |
| GET    | `/api/v1/reports/{id}`          | Retrieve a specific report         |
| GET    | `/api/v1/reports/{id}/download` | Download report                    |
| DELETE | `/api/v1/reports/{id}`          | Delete report                      |
| GET    | `/health`                       | Health check                       |

---

# 📥 Example Input

Patient speaks in Telugu:

> నాకు మూడు రోజులుగా జ్వరం ఉంది. దగ్గు కూడా ఉంది.

---

# 📤 Example Output

```json
{
  "language": "Telugu",
  "english_transcript": "I have had a fever for three days. I also have a cough.",
  "entities": {
    "symptoms": [
      "Fever",
      "Cough"
    ],
    "duration": "3 days"
  },
  "summary": "Patient reports fever and cough for three days.",
  "risk": "Medium"
}
```

---

# ▶️ Running the Project

## Clone Repository

```bash
git clone <repository-url>
cd MedicalSpeechAssistant
```

## Create Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Start the Server

```bash
uvicorn main:app --reload
```

---

# 📖 API Documentation

FastAPI automatically generates interactive API documentation.

* Swagger UI: `http://localhost:8000/docs`
* ReDoc: `http://localhost:8000/redoc`

---

# 👥 Team Responsibilities

### Member 1

* Speech Recognition
* Language Detection
* Machine Translation

### Member 2

* Medical Entity Extraction
* Text Summarization

### Member 3

* Risk Assessment
* Report Generation
* Database
* FastAPI Integration

---

# 🔮 Future Enhancements

* Speech Emotion Recognition
* Medical Question Answering using RAG
* Electronic Health Record (EHR) Integration
* Cloud Deployment
* Doctor Dashboard
* Multi-user Authentication
* PDF Report Generation
* Advanced Clinical Risk Prediction using Machine Learning

---

# 📚 References

* Faster-Whisper
* IndicTrans2
* spaCy
* SciSpaCy
* PEGASUS
* BART
* FastAPI
* SQLite

---

# 📄 License

This project is developed for academic and educational purposes as part of a B.Tech Artificial Intelligence & Machine Learning curriculum.
