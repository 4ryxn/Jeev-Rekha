from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.routes import router as api_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Synthetic core-operations API for Jeev Rekha Phase 2.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/api/v1/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Return the API process health without depending on future services."""
    return {"status": "ok", "service": "jeev-rekha-api", "environment": settings.app_env}
