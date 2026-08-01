from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes import router
from careinsight.engine import CareVoiceEngine
from config import (
    APP_DESCRIPTION,
    APP_NAME,
    APP_VERSION,
)
from utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize and shutdown CareVoice AI resources.
    """

    logger.info("Starting %s...", APP_NAME)

    app.state.engine = CareVoiceEngine()

    try:
        yield

    finally:

        logger.info("Shutting down %s...", APP_NAME)

        app.state.engine.database.close()

        logger.info("Application shutdown completed.")


app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
)

app.include_router(router)