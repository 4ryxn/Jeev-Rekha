from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.api.routes import router as api_router
from app.db.session import engine

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Jeev Rekha operational advisory API. Synthetic and pilot data remain clearly separated.",
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_host_list)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/api/v1/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Return the API process health without depending on future services."""
    return {"status": "ok", "service": "jeev-rekha-api", "environment": settings.app_env}


@app.get("/api/v1/readiness", tags=["system"])
def readiness_check() -> dict[str, str]:
    """Check database reachability without disclosing connection details."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "database": "unavailable"},
        ) from exc
    return {"status": "ready", "database": "connected"}
