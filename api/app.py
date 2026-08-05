from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes import router
from config import (
    APP_DESCRIPTION,
    APP_NAME,
    APP_VERSION,
)
from utils.logger import get_logger

logger = get_logger(__name__)


def _default_engine():
    """
    Build the real pipeline engine.

    Imported lazily so that injecting a stub engine costs nothing:
    `careinsight.engine` pulls in torch and CTranslate2, and tests
    that never touch the models should not pay for that.
    """

    from careinsight.engine import CareVoiceEngine

    return CareVoiceEngine()


def create_app(engine_factory=_default_engine) -> FastAPI:
    """
    Build the FastAPI application.

    Parameters
    ----------
    engine_factory : callable
        Returns the pipeline engine. Tests pass a stub so the
        routes can be exercised without loading several GB of
        models.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """
        Initialize and shutdown CareVoice AI resources.
        """

        logger.info("Starting %s...", APP_NAME)

        app.state.engine = engine_factory()

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

    return app


# Module-level app for `uvicorn api.app:app`.
app = create_app()
