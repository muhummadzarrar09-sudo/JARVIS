from fastapi import APIRouter

from app.core.config import settings
from app.services.database_service import database_service
from app.services.model_service import model_service

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    model_status = model_service.status()
    provider = model_status.get("provider", {})
    selected = provider.get("selected_model") or {}
    db = database_service.status()
    return {
        "status": "ok",
        "app": settings.app_name,
        "configured_provider": provider.get("configured_provider"),
        "effective_provider": provider.get("effective_provider"),
        "selected_model": selected.get("name"),
        "llama_cpp_installed": provider.get("llama_cpp_installed"),
        "database_exists": db.get("exists"),
        "database_integrity": db.get("integrity_check"),
    }
