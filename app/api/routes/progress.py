from fastapi import APIRouter

from app.services.progress_service import progress_service

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/phase4")
def phase4() -> dict:
    return progress_service.phase4_status()
