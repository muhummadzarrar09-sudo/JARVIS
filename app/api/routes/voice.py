from fastapi import APIRouter

from app.services.voice_service import voice_service

router = APIRouter(prefix="/voice", tags=["voice"])


@router.get("/status")
def voice_status() -> dict:
    return voice_service.status()
