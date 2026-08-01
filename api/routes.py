from pathlib import Path
import shutil

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Request,
    UploadFile,
)

from api.schemas import (
    AnalyzeResponse,
    DeleteResponse,
    HealthResponse,
    ReportDetail,
    ReportListItem,
)
from config import (
    SUPPORTED_AUDIO_EXTENSIONS,
    UPLOAD_DIR,
)
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ==========================================================
# Health Check
# ==========================================================

@router.get(
    "/",
    response_model=HealthResponse,
    tags=["Health"],
)
def home():
    """
    Health check endpoint.
    """

    return {
        "message": "Welcome to CareVoice AI API",
        "status": "Running",
    }


# ==========================================================
# Analyze Audio
# ==========================================================

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    tags=["Analysis"],
)
async def analyze_audio(
    request: Request,
    audio: UploadFile = File(...),
):
    """
    Analyze an uploaded audio file.
    """

    file_path = _save_uploaded_file(audio)

    try:

        logger.info(
            "Processing uploaded file: %s",
            file_path.name,
        )

        engine = request.app.state.engine

        return engine.process_audio(
            str(file_path)
        )

    except Exception:

        logger.exception(
            "Audio analysis failed."
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to process audio.",
        )

    finally:

        if file_path.exists():

            file_path.unlink()

            logger.info(
                "Removed uploaded file: %s",
                file_path.name,
            )


# ==========================================================
# Get All Reports
# ==========================================================

@router.get(
    "/reports",
    response_model=list[ReportListItem],
    tags=["Reports"],
)
def get_reports(
    request: Request,
):
    """
    Return all stored reports.
    """

    reports = request.app.state.engine.database.get_all_reports()

    return [
        {
            "id": report["id"],
            "timestamp": report["timestamp"],
            "patient_name": report["patient_name"],
            "age": report["age"],
            "risk_level": report["risk_level"],
        }
        for report in reports
    ]


# ==========================================================
# Get Report
# ==========================================================

@router.get(
    "/reports/{report_id}",
    response_model=ReportDetail,
    tags=["Reports"],
)
def get_report(
    report_id: int,
    request: Request,
):
    """
    Return a report by ID.
    """

    report = _get_report_or_404(
        request,
        report_id,
    )

    return dict(report)


# ==========================================================
# Delete Report
# ==========================================================

@router.delete(
    "/reports/{report_id}",
    response_model=DeleteResponse,
    tags=["Reports"],
)
def delete_report(
    report_id: int,
    request: Request,
):
    """
    Delete a report.
    """

    db = request.app.state.engine.database

    _get_report_or_404(
        request,
        report_id,
    )

    db.delete_report(report_id)

    logger.info(
        "Deleted report %d",
        report_id,
    )

    return {
        "message": (
            f"Report {report_id} deleted successfully."
        )
    }


# ==========================================================
# Helper Functions
# ==========================================================

def _save_uploaded_file(
    audio: UploadFile,
) -> Path:
    """
    Validate and save the uploaded audio.
    """

    if not audio.filename:

        raise HTTPException(
            status_code=400,
            detail="No file uploaded.",
        )

    extension = Path(
        audio.filename
    ).suffix.lower()

    if extension not in SUPPORTED_AUDIO_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported audio format."
            ),
        )

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = UPLOAD_DIR / audio.filename

    with open(
        file_path,
        "wb",
    ) as buffer:

        shutil.copyfileobj(
            audio.file,
            buffer,
        )

    logger.info(
        "Uploaded file saved: %s",
        file_path.name,
    )

    return file_path


def _get_report_or_404(
    request: Request,
    report_id: int,
):
    """
    Return a report or raise 404.
    """

    db = request.app.state.engine.database

    report = db.get_report_by_id(
        report_id,
    )

    if report is None:

        raise HTTPException(
            status_code=404,
            detail="Report not found.",
        )

    return report