# 🏥 CareVoice AI

### Multilingual Clinical Speech Analysis and Intelligent Consultation Management

<p align="center">

AI-powered healthcare application that converts multilingual patient speech into structured clinical information, risk assessments, clinical reports, prescriptions, and consultation history using Speech Recognition, Machine Translation, Natural Language Processing, and Deep Learning.

</p>

---

## 📌 Project Overview

**CareVoice AI** is an end-to-end multilingual clinical consultation assistant designed to help process patient-doctor conversations.

The system allows a doctor to enter patient details, record or upload consultation audio, and process the conversation through an AI-powered pipeline.

The application:

- Accepts multilingual patient consultation audio.
- Automatically detects the spoken language.
- Converts speech into text.
- Translates the conversation into English.
- Generates a clinical summary.
- Extracts structured medical information.
- Combines AI-extracted clinical data with doctor-provided patient details.
- Performs rule-based clinical risk assessment.
- Generates a structured clinical report.
- Stores patient and consultation information in SQLite.
- Supports prescription management.
- Supports consultation history retrieval.
- Provides REST APIs through FastAPI.
- Provides a Streamlit-based user interface.

CareVoice AI demonstrates the integration of multiple AI and NLP technologies into a complete healthcare-oriented application workflow.

> **Note:** CareVoice AI is an academic project and is not intended to replace professional medical diagnosis or clinical decision-making.

---

# 🎯 Objectives

The main objectives of CareVoice AI are:

- Convert multilingual patient speech into text.
- Automatically detect the language spoken by the patient.
- Translate multilingual consultations into English.
- Generate concise clinical summaries.
- Extract important clinical information from the consultation.
- Identify:
  - Symptoms
  - Medical conditions
  - Existing medications
  - Duration of symptoms
- Collect doctor-provided patient information.
- Store patient measurements such as:
  - Blood pressure
  - Weight
  - Blood sugar
- Combine structured patient information with AI-extracted clinical information.
- Perform rule-based patient risk assessment.
- Generate structured clinical reports.
- Store patients and consultations in a SQLite database.
- Save and retrieve prescriptions.
- Retrieve patient consultation history.
- Provide REST APIs for backend integration.
- Provide an interactive Streamlit frontend.

---

# ✨ Features

## 🎙 Multilingual Consultation Processing

- Upload consultation audio.
- Process multilingual patient speech.
- Automatic speech recognition using Faster-Whisper.
- Automatic spoken language detection.

## 🌍 Machine Translation

- Translate multilingual consultations into English.
- Uses Meta NLLB-200 for machine translation.

## 📝 Clinical Summarization

- Generates concise summaries of consultation text.
- Uses Facebook BART Large CNN.

## 🩺 Clinical Information Extraction

Extracts structured clinical information including:

- Symptoms
- Medical conditions
- Existing medications
- Duration

Uses spaCy and rule-based medical patterns.

## 👤 Patient Information Management

Doctor-provided patient information includes:

- Patient ID
- Patient Name
- Age
- Blood Pressure
- Weight
- Blood Sugar

The patient information is combined with the AI-extracted clinical information before risk assessment and report generation.

## ⚠️ Rule-Based Risk Assessment

The system evaluates clinical information and generates:

- Risk Score
- Risk Level

Unknown symptoms and conditions can be safely ignored by the risk assessment logic.

## 📄 Clinical Report Generation

Generates a structured clinical report containing:

- Clinical summary
- Conversation summary
- Patient information
- Clinical measurements
- Symptoms
- Conditions
- Existing medications
- Duration
- Risk assessment

## 💊 Prescription Management

Supports storing and retrieving consultation-related prescriptions.

## 📋 Consultation History

Supports:

- Retrieving previous consultations.
- Retrieving consultations by patient.
- Viewing consultation details.
- Accessing previous clinical reports and associated information.

## 💾 SQLite Database Storage

Stores structured healthcare information including:

- Patients
- Consultations
- Clinical information
- Measurements
- Prescriptions

## ⚡ FastAPI Backend

Provides REST APIs for application integration.

## 🖥 Streamlit Frontend

Provides an interactive user interface for:

- Patient information entry.
- Audio upload and processing.
- Consultation analysis.
- Transcript display.
- English translation.
- Clinical summary.
- Medical entity display.
- Risk assessment.
- Clinical report viewing.
- Prescription management.
- Consultation history.

## 🧪 Automated Testing

The project uses **pytest** for automated testing.

Current test coverage includes:

- Database operations
- Patient storage and retrieval
- Consultation storage and retrieval
- Consultation measurements
- Patient updates
- Prescription storage and retrieval
- Consultation deletion
- Risk assessment
- Unknown symptom handling
- Unknown condition handling
- Clinical report generation
- Missing measurement handling
- End-to-end engine pipeline with mocked AI components


## 🤖 **AI Models and Processing Components**

| Stage                      | Technology / Model                  |
| -------------------------- | ----------------------------------- |
| Speech Recognition         | Faster-Whisper                      |
| Speech Model               | Whisper `large-v3`                  |
| Language Detection         | Whisper Built-in Language Detection |
| Machine Translation        | Meta NLLB-200 Distilled 600M        |
| Clinical Summarization     | Facebook BART Large CNN             |
| Medical NLP                | spaCy `en_core_web_sm`              |
| Clinical Entity Extraction | EntityRuler + Medical Patterns      |
| Risk Assessment            | Rule-Based Clinical Engine          |
| Report Generation          | Template-Based Generator            |


## 🏗️ **System Architecture**

                         👤 Doctor
                            │
                            ▼
                 Patient Information Entry
                            │
                            ▼
                 🎙 Consultation Audio
                    Record / Upload
                            │
                            ▼
              Faster-Whisper Speech Recognition
                            │
                            ▼
                Automatic Language Detection
                            │
                            ▼
             Meta NLLB-200 Machine Translation
                            │
                            ▼
                     English Transcript
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
       Clinical Summarization      Medical Information
          BART Large CNN              Extraction
                                      spaCy + Rules
              │                           │
              └─────────────┬─────────────┘
                            ▼
                Combine Patient + Clinical Data
                            │
                            ▼
                 Rule-Based Risk Assessment
                            │
                            ▼
                 Clinical Report Generation
                            │
                    ┌───────┴────────┐
                    ▼                ▼
             SQLite Database      Prescription
                    │
                    ▼
          Consultation History Retrieval
                    │
                    ▼
          FastAPI REST API + Streamlit UI



## 🔄 Complete Consultation Workflow

```text
┌─────────────────────────────────────────────┐
│ 1. Doctor enters patient information        │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│ 2. Record or upload consultation audio      │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│ 3. Speech-to-Text using Faster-Whisper      │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│ 4. Automatic language detection             │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│ 5. Translation into English using NLLB-200  │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│ 6. Clinical summarization using BART        │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│ 7. Medical information extraction           │
│    using spaCy                              │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│ 8. Combine patient details with extracted   │
│    clinical information                     │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│ 9. Rule-based clinical risk assessment      │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│ 10. Generate structured clinical report     │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│ 11. Save patient and consultation to SQLite │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│ 12. Add prescription information            │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│ 13. Retrieve consultation history           │
│     when required                           │
└─────────────────────────────────────────────┘
```




# 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| 💻 Programming Language | Python 3.11+ |
| 🎙️ Speech Processing | Faster-Whisper, CTranslate2 |
| 🌍 Machine Translation | Meta NLLB-200 Distilled 600M |
| 🧠 Natural Language Processing | spaCy, EntityRuler, Rule-Based Medical Patterns |
| 🤖 Deep Learning | Facebook BART Large CNN, PyTorch, Hugging Face Transformers |
| ⚙️ Backend | FastAPI, Uvicorn, Pydantic |
| 🗄️ Database | SQLite |
| 🖥️ Frontend | Streamlit |
| 🧪 Testing | pytest, pytest-cov, unittest.mock |


## 📁 Project Structure

```text
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
│
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
```


## 🔄 Core Pipeline

The main orchestration logic is handled by `careinsight/engine.py`.

The `CareVoiceEngine` coordinates the complete AI pipeline.

```text
Audio
  │
  ▼
SpeechTranscriber
  │
  ▼
Translator
  │
  ▼
MedicalSummarizer
  │
  ▼
MedicalExtractor
  │
  ▼
Combine Patient Details
  │
  ▼
RiskAssessor
  │
  ▼
ReportGenerator
  │
  ▼
DatabaseManager
```

### 👤 **Patient Data**
The engine accepts:

```python
process_audio(audio_path, patient_details)
```

Patient details include information provided by the doctor before processing the consultation.

## 👤 Patient Data

Example doctor-provided patient details:

```json
{
  "patient_id": "P001",
  "patient_name": "Lakshmi",
  "age": 70,
  "blood_pressure": "140/90",
  "weight": 65,
  "blood_sugar": 150
}
```

The system combines this information with AI-extracted clinical information.

## 🩺 Example Consultation Input

Example patient speech in Telugu:

> నాకు మూడు రోజులుగా జ్వరం మరియు దగ్గు ఉంది.

## 📊 Example Pipeline Output

```json
{
  "consultation_id": 1,
  "original_transcript": "నాకు మూడు రోజులుగా జ్వరం మరియు దగ్గు ఉంది.",
  "detected_language": "te",
  "english_transcript": "I have had fever and cough for three days.",
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
      "Diabetes"
    ],
    "medications": [
      "Paracetamol"
    ],
    "duration": "3 days"
  },
  "risk": {
    "risk_score": 5,
    "risk_level": "High"
  },
  "clinical_report": "Generated Clinical Report"
}
```


## 🚀 Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/<your-username>/CareVoice-AI.git
cd CareVoice-AI
```

### 2️⃣ Create a Virtual Environment

```bash
python -m venv .venv
```

#### 🍎 macOS / Linux

```bash
source .venv/bin/activate
```

#### 🪟 Windows

```bash
.venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

## ▶️ Running the Project

### ▶️ Run the Main Application

```bash
python main.py
```

### 🚀 Run the FastAPI Backend

```bash
uvicorn api.app:app --reload
```

The API will be available locally on port `8000`.

### 🖥️ Run the Streamlit Frontend

```bash
streamlit run streamlit_app.py
```


## 🔄 Complete Consultation Workflow

The consultation flow includes:

```text
👤 Patient Information
        │
        ▼
🎙️ Record / Upload Consultation Audio
        │
        ▼
✨ Analyze Consultation
        │
        ▼
🗣️ Original Transcript
        │
        ▼
🌐 English Translation
        │
        ▼
📝 Clinical Summary
        │
        ▼
🩺 Extracted Medical Information
        │
        ▼
⚠️ Risk Assessment
        │
        ▼
📄 Clinical Report
        │
        ▼
💊 Prescription
        │
        ▼
📋 Consultation History
```

## 🗄️ Database Functionality

The SQLite database supports core consultation management functionality.

### The tested functionality includes:

- Creating an empty database
- Saving patients
- Retrieving patients
- Saving consultations
- Retrieving consultations by ID
- Saving consultation measurements
- Retrieving consultations by patient
- Updating patient information when a new consultation is added
- Saving prescriptions
- Retrieving prescriptions
- Deleting consultations

## 🧪 Testing

The project uses **pytest** for automated testing.

Run the complete test suite:

```bash
pytest -v
```

## 🚀 Future Enhancements

Potential future enhancements include:

- 📄 **PDF Clinical Report Download**  
  Enable doctors to download generated clinical reports in PDF format.

- 🎨 **Improved Streamlit Dashboard Styling**  
  Further enhance the user interface and overall user experience.

- 🌐 **Enhanced Multilingual Language Support**  
  Extend support to additional Indian and international languages.

- 🩺 **Improved Medical Entity Extraction**  
  Enhance extraction accuracy for symptoms, conditions, medications, durations, and other clinical entities.

- 🧠 **Domain-Specific Medical NLP Models**  
  Integrate specialized NLP models trained on medical and clinical datasets.

- 📊 **Data Refinement and Model Evaluation**  
  Use curated or custom clinical consultation datasets for improved performance, evaluation, and benchmarking.

- 🤖 **Machine Learning-Based Risk Prediction**  
  Replace or complement the current rule-based risk assessment with machine learning models.

- 🔐 **Doctor Authentication**  
  Add secure authentication for doctors and authorized users.

- 👥 **Role-Based Access Control**  
  Support different access levels for doctors, administrators, and other authorized users.

- 🔎 **Enhanced Patient History Search**  
  Provide advanced search and filtering capabilities for patient consultation history.

- 🏥 **Electronic Health Record (EHR) Integration**  
  Integrate with Electronic Health Record systems for improved clinical data management.

- 🔍 **Retrieval-Augmented Generation (RAG)**  
  Add RAG-based medical question-answering capabilities using trusted medical knowledge sources.

- ⚕️ **Clinical Decision Support Features**  
  Provide additional decision-support capabilities to assist healthcare professionals.

- 🐳 **Docker Containerization**  
  Containerize the application for easier deployment and environment consistency.

- ☸️ **Kubernetes Deployment**  
  Support scalable container orchestration and deployment.

- ☁️ **Cloud Deployment**  
  Deploy the application using cloud platforms such as AWS or Azure.

## 🎓 Academic and NLP Concepts Demonstrated

CareVoice AI demonstrates the practical integration of multiple **Natural Language Processing and AI concepts**:

### 🗣️ Speech and Language Processing

- **Automatic Speech Recognition (ASR)**  
  Converts recorded consultation audio into text using Faster-Whisper.

- **Language Identification**  
  Automatically detects the language of the consultation audio.

- **Neural Machine Translation (NMT)**  
  Translates multilingual consultation transcripts into English using NLLB-200.

- **Text Summarization**  
  Generates concise clinical summaries using the BART model.

### 🧠 Natural Language Processing

- **Named Entity Recognition (NER)**  
  Identifies important clinical information from consultation text.

- **Rule-Based Information Extraction**  
  Extracts symptoms, conditions, medications, durations, and other medical information using spaCy EntityRuler and custom medical patterns.

- **Clinical Text Processing**  
  Processes unstructured consultation text and transforms it into meaningful clinical information.

- **Structured Information Extraction**  
  Converts extracted information into structured data that can be used for reports and database storage.

### ⚕️ Clinical Intelligence

- **Rule-Based Classification**  
  Performs clinical risk assessment based on predefined rules and extracted patient information.

- **Deep Learning Model Integration**  
  Integrates transformer-based deep learning models for translation and clinical summarization.

### 🔄 Software Engineering and AI Integration

- **End-to-End NLP Pipeline Design**  
  Connects speech recognition, language detection, translation, summarization, medical information extraction, risk assessment, and report generation into a single workflow.

- **REST API Integration**  
  Uses FastAPI to expose backend functionality through API endpoints.

- **Database Persistence**  
  Stores patient, consultation, clinical, and prescription information using SQLite.

- **Automated Unit and Integration Testing**  
  Uses pytest to test major components and validate application functionality.

## 📚 References and Technologies

The project uses the following open-source technologies, frameworks, and AI models:

### 🤖 AI and Speech Models

- **OpenAI Whisper**
- **Faster-Whisper**
- **CTranslate2**

### 🌐 Machine Translation

- **Meta NLLB-200**

### 📝 Text Summarization

- **Facebook BART**

### 🧠 NLP and Deep Learning

- **Hugging Face Transformers**
- **spaCy**
- **PyTorch**

### ⚙️ Backend and API

- **FastAPI**
- **Uvicorn**
- **Pydantic**

### 🗄️ Database

- **SQLite**

### 🖥️ Frontend

- **Streamlit**

### 🧪 Testing

- **pytest**

## ⚠️ Disclaimer

CareVoice AI is developed for **academic and research purposes**.

The application is designed to demonstrate the practical use of **Artificial Intelligence (AI)** and **Natural Language Processing (NLP)** techniques for processing clinical conversations.

> **Important:** CareVoice AI is not a medical device and must not be used as a replacement for professional healthcare services.

It should **not** be used as a replacement for:

- Professional medical diagnosis
- Clinical examination
- Emergency medical advice
- Professional healthcare decision-making

All AI-generated summaries, extracted medical information, risk assessments, and clinical reports should be **reviewed and validated by qualified healthcare professionals**.

---

## 🙏 Acknowledgements

CareVoice AI integrates open-source AI models, frameworks, and technologies developed and maintained by the following organizations and communities:

- **OpenAI** — Whisper
- **Faster-Whisper Community** — Faster-Whisper
- **Meta AI** — NLLB-200
- **Hugging Face** — Transformers and model ecosystem
- **Facebook AI Research** — BART
- **spaCy Community** — Natural Language Processing framework
- **FastAPI Community** — Backend API framework
- **Streamlit Community** — Frontend application framework
- **PyTorch Community** — Deep learning framework

The project acknowledges the contributions of these open-source communities and researchers whose tools, models, and frameworks support the development of modern AI and NLP applications.




