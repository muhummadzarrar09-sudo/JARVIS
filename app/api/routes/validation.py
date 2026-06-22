from fastapi import APIRouter

from app.services.validation_service import validation_service

router = APIRouter(prefix="/validation", tags=["validation"])


@router.get("/report")
def validation_report() -> dict:
    return validation_service.report()
