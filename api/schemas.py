from typing import List, Optional

from pydantic import BaseModel, Field


# ==========================================================
# Health Check Response
# ==========================================================

class HealthResponse(BaseModel):
    message: str
    status: str


# ==========================================================
# Patient Information
# ==========================================================

class PatientResponse(BaseModel):

    patient_name: Optional[str] = Field(
        default=None,
        description="Patient name",
    )

    age: Optional[int] = Field(
        default=None,
        description="Patient age",
    )

    symptoms: List[str] = Field(
        default_factory=list,
        description="Detected symptoms",
    )

    conditions: List[str] = Field(
        default_factory=list,
        description="Detected medical conditions",
    )

    medications: List[str] = Field(
        default_factory=list,
        description="Detected medications",
    )

    duration: Optional[str] = Field(
        default=None,
        description="Duration of symptoms",
    )


# ==========================================================
# Risk Assessment
# ==========================================================

class RiskResponse(BaseModel):

    risk_score: int = Field(
        description="Calculated clinical risk score",
    )

    risk_level: str = Field(
        description="Low / Medium / High",
    )


# ==========================================================
# Analyze Response
# ==========================================================

class AnalyzeResponse(BaseModel):

    report_id: int = Field(
        description="ID of the stored report",
    )

    detected_language: str

    language_probability: float = Field(
        description="Whisper language detection confidence",
    )

    original_transcript: str

    english_transcript: str

    summary: str

    patient: PatientResponse

    risk: RiskResponse

    clinical_report: str

    warnings: List[str] = Field(
        default_factory=list,
        description=(
            "Non-fatal problems encountered while processing, "
            "such as an unsupported source language"
        ),
    )


# ==========================================================
# Report List Item
# ==========================================================

class ReportListItem(BaseModel):

    id: int

    timestamp: str

    patient_name: Optional[str]

    age: Optional[int]

    risk_level: str


# ==========================================================
# Report Details
# ==========================================================

class ReportDetail(BaseModel):

    id: int

    timestamp: str

    patient_name: Optional[str]

    age: Optional[int]

    symptoms: str

    conditions: str

    medications: str

    duration: Optional[str]

    summary: str

    risk_score: int

    risk_level: str

    clinical_report: str

    detected_language: Optional[str] = None

    original_transcript: Optional[str] = None

    english_transcript: Optional[str] = None


# ==========================================================
# Delete Response
# ==========================================================

class DeleteResponse(BaseModel):

    message: str