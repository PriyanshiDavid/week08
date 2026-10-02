import logging
import os
import random
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.exc import OperationalError

from app.db import Base, engine
from app.routers import courses


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def initialise_database() -> None:
    maximum_attempts = 10
    retry_delay_seconds = 5

    for attempt in range(1, maximum_attempts + 1):
        try:
            Base.metadata.create_all(bind=engine)

            logger.info(
                "Database connection established successfully."
            )

            return

        except OperationalError:
            logger.warning(
                "Database connection failed. Attempt %s of %s.",
                attempt,
                maximum_attempts,
            )

            if attempt == maximum_attempts:
                logger.exception(
                    "Unable to connect to the database."
                )
                raise

            time.sleep(retry_delay_seconds)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialise_database()
    yield


app = FastAPI(
    title="KoalaTech University Course Service",
    description=(
        "Manages courses and lecturer assignments "
        "for KoalaTech University."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# Demo fault injection: a "faulty" image is built with FAULT_RATE > 0 so the
# canary analysis has a bad release to catch. Production images use 0.
FAULT_RATE = float(os.getenv("FAULT_RATE", "0"))


@app.middleware("http")
async def inject_faults(request: Request, call_next):
    if (
        FAULT_RATE > 0
        and request.url.path.startswith("/courses")
        and random.random() < FAULT_RATE
    ):
        return JSONResponse(
            {"detail": "Injected fault"}, status_code=500
        )
    return await call_next(request)


# Exposes request count and latency histograms at /metrics for Prometheus
Instrumentator().instrument(app).expose(app, include_in_schema=False)


app.include_router(courses.router)


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    return {
        "message": (
            "KoalaTech University Course Service is running."
        )
    }


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "course-service",
    }