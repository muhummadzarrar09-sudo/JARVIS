from fastapi import APIRouter, Query

from app.services.operator_mode import operator_mode_service

router = APIRouter(prefix="/operator", tags=["operator"])


@router.get("/classify")
def classify(command: str = Query(..., min_length=1)) -> dict:
    return operator_mode_service.classify_command(command)


@router.get("/palette")
def palette() -> dict:
    return {"items": operator_mode_service.palette()}
