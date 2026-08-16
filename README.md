🏥 CareVoice AI

Multilingual Clinical Speech Analysis, Patient Consultation Management and Intelligent Report Generation

<p align="center">

AI-powered healthcare assistant that processes multilingual patient
consultations and converts speech into structured clinical insights,
risk assessments, reports, prescriptions, and consultation history.

</p>

📌 Project Overview

CareVoice AI is an end-to-end AI-powered healthcare application
designed to support the processing of multilingual patient
consultations.

The application allows a doctor or healthcare user to enter patient
details, including identity and clinical measurements, upload or record
consultation audio, and process the conversation through an AI/NLP
pipeline.

The system:

Accepts multilingual consultation audio.

Converts speech into text using Faster-Whisper.

Automatically detects the spoken language.

Translates the conversation into English.

Generates a concise clinical summary.

Extracts structured medical information.

Combines AI-extracted clinical information with doctor-provided
patient details.

Performs rule-based clinical risk assessment.

Generates a structured clinical report.

Stores patients, consultations, measurements, reports, and
prescriptions in SQLite.

Provides REST APIs and a Streamlit-based user interface for
interacting with the system.

Supports consultation history retrieval and prescription management.

Note: CareVoice AI is an academic NLP project and is intended to
assist with information processing. It is not a substitute for
professional medical diagnosis or clinical decision-making.

🎯 Objectives

Convert multilingual patient speech into text.

Automatically detect the spoken language.

Translate multilingual consultations into English.

Extract important clinical information such as:

Symptoms

Medical conditions

Medications

Duration

Generate concise clinical summaries.

Combine doctor-provided patient information with AI-extracted
clinical information.

Record clinical measurements such as:

Blood pressure

Weight

Blood sugar

Perform patient risk assessment.

Generate structured clinical reports.

Store patient and consultation information in a relational SQLite
database.

Maintain consultation history.

Support prescription creation and retrieval.

Provide REST APIs for application integration.

Provide an interactive Streamlit interface for the consultation
workflow.

✨ Features

🎙 Multilingual Consultation Processing

Audio upload support

Audio recording workflow

Multilingual speech recognition

Automatic language detection

English translation

🩺 Clinical Information Processing

Medical entity extraction

Symptom extraction

Condition extraction

Medication extraction

Duration extraction

Clinical text summarization

Doctor-provided patient information integration

⚠️ Risk Assessment

Rule-based clinical risk assessment

Risk score generation

Risk-level classification

Handling of unknown symptoms and conditions

📄 Clinical Reporting

Structured clinical report generation

Patient information section

Clinical measurements section

AI-generated conversation summary

Extracted symptoms, conditions, and medications

Risk assessment section

👩‍⚕️ Patient and Consultation Management

Patient storage

Patient updates when new consultations are added

Consultation storage

Consultation retrieval by ID

Consultation retrieval by patient

Consultation deletion

Consultation history support

💊 Prescription Management

Prescription storage

Prescription retrieval

Integration with patient consultations

💾 Database

SQLite database integration

Separate handling of patients and consultations

Clinical measurements stored with consultations

Prescription persistence

⚡ Backend and APIs

FastAPI backend

REST API routes

Pydantic schemas

Interactive Swagger documentation

🖥 Frontend

Streamlit-based interface

Modular component architecture

Patient information form

Audio uploader/recorder

Analysis progress display

Transcript and translation views

Summary and medical entity views

Risk assessment view

Clinical report view

Consultation history

Prescription interface

🧪 Testing

The project uses PyTest for unit and integration-style testing of
major components.

Current automated test coverage includes:

Database operations

Patient operations

Consultation operations

Clinical measurements

Prescription operations

Risk assessment

Report generation

End-to-end engine orchestration with mocked AI components

Current test status:

20 passed

🤖 AI Models and Processing Components

Stage                    Model / Technology

Speech Recognition       Faster-Whisper (large-v3)
Language Detection       Whisper built-in language detection
Machine Translation      Meta NLLB-200 Distilled 600M
Clinical Summarization   Facebook BART Large CNN
Medical NLP              spaCy (en_core_web_sm) + EntityRuler
Risk Assessment          Rule-based clinical engine
Report Generation        Template-based generator

🏗 System Architecture

                         ┌─────────────────────────────┐
                         │     Doctor / Healthcare     │
                         │          User               │
                         └──────────────┬──────────────┘
                                        │
                     ┌──────────────────┴──────────────────┐
                     ▼                                     ▼
        Doctor-Provided Patient Details          Consultation Audio
        - Patient ID                            - Upload
        - Name                                  - Record
        - Age
        - Blood Pressure
        - Weight
        - Blood Sugar
                     │                                     │
                     └──────────────────┬──────────────────┘
                                        ▼
                         Faster-Whisper Speech Recognition
                                        │
                                        ▼
                         Automatic Language Detection
                                        │
                                        ▼
                           NLLB-200 Translation
                                        │
                                        ▼
                              English Transcript
                                        │
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
                 spaCy + EntityRuler             BART Summarizer
              Clinical Information Extraction    Clinical Summary
                         │                             │
                         └──────────────┬──────────────┘
                                        ▼
                       Combine Patient + Clinical Data
                                        │
                                        ▼
                       Rule-Based Risk Assessment
                                        │
                                        ▼
                         Clinical Report Generator
                                        │
                     ┌──────────────────┴──────────────────┐
                     ▼                                     ▼
              SQLite Database                       FastAPI REST API
         Patients / Consultations /                Reports / Data
         Measurements / Prescriptions                     │
                     │                                     ▼
                     └──────────────────────────► Streamlit Dashboard
                                                   - Consultation
                                                   - Results
                                                   - History
                                                   - Prescription

🔄 Complete Workflow

1. Enter Patient Details
        │
        ▼
2. Enter Clinical Measurements
        │
        ▼
3. Upload or Record Consultation Audio
        │
        ▼
4. Speech Recognition
        │
        ▼
5. Language Detection
        │
        ▼
6. Translation to English
        │
        ▼
7. Clinical Summarization
        │
        ▼
8. Medical Entity Extraction
        │
        ▼
9. Combine Patient + Extracted Clinical Data
        │
        ▼
10. Risk Assessment
        │
        ▼
11. Clinical Report Generation
        │
        ▼
12. Save Patient and Consultation
        │
        ▼
13. Store Measurements and Prescription
        │
        ▼
14. View Report / History / Prescription

🛠 Technology Stack

Programming Language

Python 3.11+

Speech Processing

Faster-Whisper

CTranslate2

Machine Translation

Meta NLLB-200 Distilled 600M

Natural Language Processing

spaCy

EntityRuler

Deep Learning

Facebook BART Large CNN

PyTorch

Hugging Face Transformers

Backend

FastAPI

Uvicorn

Pydantic

Database

SQLite

Frontend

Streamlit

Testing

PyTest

pytest-cov

📁 Project Structure

CareVoice-AI/
│
├── api/
│   ├── __init__.py
│   ├── app.py
│   ├── routes.py
│   └── schemas.py
│
├── careinsight/
│   ├── __init__.py
│   ├── engine.py
│   ├── extractor.py
│   ├── medical_patterns.py
│   ├── report_generator.py
│   ├── risk_assessor.py
│   └── summarizer.py
│
├── database/
│   ├── __init__.py
│   ├── database.py
│   └── carevoice.db
│
├── speech/
│   ├── __init__.py
│   └── transcriber.py
│
├── translation/
│   ├── __init__.py
│   └── translator.py
│
├── frontend/
│   ├── __init__.py
│   ├── constants.py
│   │
│   ├── components/
│   │   ├── __init__.py
│   │   ├── entities.py
│   │   ├── history.py
│   │   ├── patient_form.py
│   │   ├── prescription.py
│   │   ├── progress.py
│   │   ├── report.py
│   │   ├── risk.py
│   │   ├── sidebar.py
│   │   ├── speaker.py
│   │   ├── summary.py
│   │   ├── transcript.py
│   │   ├── translation.py
│   │   └── uploader.py
│   │
│   ├── helpers/
│   │   ├── __init__.py
│   │   └── file_handler.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── analysis_service.py
│       ├── file_service.py
│       ├── history_service.py
│       └── prescription_service.py
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
│
├── tests/
│   ├── test_database.py
│   ├── test_engine.py
│   ├── test_report_generator.py
│   └── test_risk_assessor.py
│
├── config.py
├── main.py
├── pytest.ini
├── requirements.txt
└── README.md

__pycache__ directories are generated automatically by Python and
are not part of the source structure.

🧩 Core Modules

careinsight/engine.py

The main orchestration layer.

It coordinates:

Audio
  ↓
Transcription
  ↓
Translation
  ↓
Summarization
  ↓
Clinical Information Extraction
  ↓
Combine Patient + Clinical Data
  ↓
Risk Assessment
  ↓
Report Generation
  ↓
Database Storage

The main pipeline accepts:

process_audio(
    audio_path,
    patient_details,
)

careinsight/extractor.py

Extracts structured clinical information from the English transcript,
including:

Symptoms

Conditions

Medications

Duration

careinsight/summarizer.py

Generates a concise summary of the translated consultation.

careinsight/risk_assessor.py

Calculates:

Risk score

Risk level

using the available patient and clinical information.

careinsight/report_generator.py

Creates a formatted clinical report containing:

Patient identity

Clinical measurements

Clinical summary

Conversation summary

Symptoms

Conditions

Medications

Duration

Risk score

Risk level

database/database.py

Manages persistent storage for application data, including:

Patients

Consultations

Consultation measurements

Prescriptions

speech/transcriber.py

Handles multilingual speech recognition using Faster-Whisper.

translation/translator.py

Translates detected multilingual text into English using NLLB-200.

📥 Example Consultation Input

Doctor-Provided Patient Details

{
  "patient_id": "P001",
  "patient_name": "Lakshmi",
  "age": 70,
  "blood_pressure": "140/90",
  "weight": 65,
  "blood_sugar": 150
}

Patient Audio Content

Example Telugu speech:

నాకు మూడు రోజులుగా జ్వరం ఉంది. దగ్గు కూడా ఉంది.

📤 Example Pipeline Output

{
  "consultation_id": 1,
  "original_transcript": "నాకు మూడు రోజులుగా జ్వరం ఉంది. దగ్గు కూడా ఉంది.",
  "detected_language": "te",
  "english_transcript": "I have had a fever for three days. I also have a cough.",
  "summary": "Patient reports fever and cough for three days.",
  "patient": {
    "patient_id": "P001",
    "patient_name": "Lakshmi",
    "age": 70,
    "blood_pressure": "140/90",
    "weight": 65,
    "blood_sugar": 150,
    "symptoms": [
      "fever",
      "cough"
    ],
    "conditions": [
      "Hypertension",
      "Diabetes"
    ],
    "medications": [
      "Paracetamol"
    ],
    "duration": "three days"
  },
  "risk": {
    "risk_score": 5,
    "risk_level": "High"
  },
  "clinical_report": "..."
}

⚙️ Installation

1. Clone the Repository

git clone https://github.com/<your-username>/CareVoice-AI.git
cd CareVoice-AI

Replace <your-username> with your GitHub username.

2. Create a Virtual Environment

python -m venv .venv

macOS / Linux

source .venv/bin/activate

Windows

.venv\Scripts\activate

3. Install Dependencies

pip install -r requirements.txt

If required, install the spaCy language model:

python -m spacy download en_core_web_sm

▶️ Running the Project

Command Line

Run the application pipeline:

python main.py

FastAPI Backend

Start the API server:

uvicorn api.app:app --reload

By default, the API will be available locally.

Swagger UI

http://127.0.0.1:8000/docs

ReDoc

http://127.0.0.1:8000/redoc

Streamlit Frontend

Run the Streamlit application using the project's configured application
entry point.

For example, if your Streamlit entry file is streamlit_app.py in the
project root:

streamlit run streamlit_app.py

If the entry point is moved or renamed, update the command accordingly.

📡 REST API

The FastAPI application contains API routes and Pydantic schemas for
interacting with CareVoice AI.

The exact available endpoints can be explored through the interactive
Swagger documentation after starting the backend:

http://127.0.0.1:8000/docs

🧪 Testing

CareVoice AI uses PyTest for automated testing.

Run All Tests

pytest -v

Current project test suite:

20 passed

Test Database Operations

pytest tests/test_database.py -v

This covers operations including:

Empty database

Save and retrieve patient

Save consultation

Retrieve consultation by ID

Save consultation measurements

Retrieve consultations by patient

Update patient information

Save and retrieve prescriptions

Delete consultation

Test Risk Assessment

pytest tests/test_risk_assessor.py -v

This validates:

Low-risk patients

Elderly patient risk

Symptom-based risk

Condition-based risk

High-risk patients

Empty patient data

Unknown symptoms

Unknown conditions

Test Report Generation

pytest tests/test_report_generator.py -v

This validates:

Complete clinical report generation

Missing measurement handling

Test End-to-End Engine Orchestration

pytest tests/test_engine.py -v

The engine test mocks heavy AI components and validates the complete
orchestration flow:

Transcription
→ Translation
→ Summarization
→ Clinical Extraction
→ Patient Data Combination
→ Risk Assessment
→ Report Generation
→ Database Save

🖥 User Interface Workflow

The frontend is designed around the patient consultation workflow.

New Consultation
      │
      ├── Enter Patient Details
      ├── Enter Clinical Measurements
      ├── Record or Upload Audio
      │
      ▼
Start Analysis
      │
      ▼
Analysis Progress
      │
      ├── Speech Recognition
      ├── Language Detection
      ├── Translation
      ├── Summarization
      ├── Medical Information Extraction
      ├── Risk Assessment
      └── Report Generation
      │
      ▼
Consultation Results
      │
      ├── Transcript
      ├── Translation
      ├── Summary
      ├── Medical Entities
      ├── Risk Assessment
      └── Clinical Report
      │
      ├── Consultation History
      └── Prescription Management

🔒 Important Disclaimer

CareVoice AI is developed for academic and research purposes as part
of an NLP project.

The application:

Does not provide a medical diagnosis.

Does not replace a qualified doctor or healthcare professional.

Does not guarantee the clinical accuracy of AI-generated
transcripts, translations, summaries, extracted entities, or risk
assessments.

Should not be used as the sole basis for treatment or emergency
medical decisions.

All clinical output should be reviewed by a qualified healthcare
professional.

🔮 Future Enhancements

Potential future improvements include:

📊 Enhanced doctor dashboard and analytics

📄 Improved PDF report download and formatting

🔍 Advanced patient history search and filtering

🏥 Electronic Health Record (EHR) integration

🤖 Retrieval-Augmented Generation (RAG) for medical question
answering

🧠 LLM-assisted clinical decision support

📈 Machine learning-based risk prediction

🌐 Expanded multilingual language support

🔐 Authentication and role-based access control

🐳 Docker containerization

☸️ Kubernetes deployment experiments

☁️ Cloud deployment using AWS or Azure

📡 Production API deployment

📊 Model evaluation using larger clinical or domain-specific
datasets

🧪 Expanded automated test coverage

🔄 CI/CD integration

📱 Improved responsive UI experience

📚 References and Technologies

This project integrates open-source AI models and frameworks including:

OpenAI Whisper

Faster-Whisper

CTranslate2

Meta NLLB-200

Facebook BART

spaCy

Hugging Face Transformers

PyTorch

FastAPI

Pydantic

Uvicorn

Streamlit

SQLite

PyTest

📄 License

This project was developed for academic purposes as part of the
Natural Language Processing Minor Specialisation.

Please review the licenses of all third-party models and libraries
before using the project in a production environment.

⭐ Acknowledgements

CareVoice AI integrates and builds upon the open-source ecosystem,
including:

OpenAI

Faster-Whisper contributors

Meta AI

Hugging Face

spaCy

FastAPI community

Streamlit community

PyTest community

<p align="center">

Built as an academic NLP project to explore the integration of
multilingual speech processing, machine translation, natural language
processing, clinical information extraction, and intelligent healthcare
workflow support.

</p>