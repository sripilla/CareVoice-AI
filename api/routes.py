import shutil
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Query,
    Request,
    Response,
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
    KEEP_UPLOADS,
    MAX_UPLOAD_BYTES,
    SUPPORTED_AUDIO_EXTENSIONS,
    UPLOAD_DIR,
)
from utils.logger import get_logger
from utils.pdf import build_report_pdf

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

    except HTTPException:

        raise

    except Exception:

        logger.exception(
            "Audio analysis failed."
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to process audio.",
        )

    finally:

        if KEEP_UPLOADS:

            logger.info(
                "Retained uploaded file for evaluation: %s",
                file_path,
            )

        elif file_path.exists():

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
    name: str | None = Query(
        default=None,
        description="Filter by patient name (partial match)",
    ),
    risk_level: str | None = Query(
        default=None,
        description="Filter by risk level: Low, Medium or High",
    ),
):
    """
    Return stored reports, optionally filtered.
    """

    database = request.app.state.engine.database

    if name or risk_level:
        reports = database.search_reports(
            name=name,
            risk_level=risk_level,
        )
    else:
        reports = database.get_all_reports()

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
# Download Report as PDF
# ==========================================================

@router.get(
    "/reports/{report_id}/pdf",
    tags=["Reports"],
    response_class=Response,
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "The clinical report as a PDF.",
        }
    },
)
def download_report_pdf(
    report_id: int,
    request: Request,
):
    """
    Download a stored report as a formatted PDF.
    """

    report = _get_report_or_404(
        request,
        report_id,
    )

    try:

        pdf_bytes = build_report_pdf(dict(report))

    except Exception:

        logger.exception(
            "PDF generation failed for report %d",
            report_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate the PDF report.",
        )

    filename = f"carevoice_report_{report_id}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            )
        },
    )


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

        supported = ", ".join(
            sorted(SUPPORTED_AUDIO_EXTENSIONS)
        )

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported audio format '{extension}'. "
                f"Supported formats: {supported}."
            ),
        )

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Browser recordings all arrive with the same filename, so a
    # unique prefix keeps concurrent uploads from overwriting one
    # another (and stops a crafted name escaping UPLOAD_DIR).
    file_path = (
        UPLOAD_DIR / f"{uuid.uuid4().hex}{extension}"
    )

    with open(
        file_path,
        "wb",
    ) as buffer:

        shutil.copyfileobj(
            audio.file,
            buffer,
        )

    size = file_path.stat().st_size

    if size > MAX_UPLOAD_BYTES:

        file_path.unlink()

        raise HTTPException(
            status_code=400,
            detail=(
                "Audio file is too large "
                f"({size // (1024 * 1024)} MB). "
                f"Limit is {MAX_UPLOAD_BYTES // (1024 * 1024)} MB."
            ),
        )

    logger.info(
        "Uploaded file saved: %s (%d bytes)",
        file_path.name,
        size,
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