from fastapi import APIRouter, Query

from app.services.quick_actions_service import quick_actions_service

router = APIRouter(prefix="/quick-actions", tags=["quick-actions"])


@router.get("/guide")
def guide() -> dict:
    return quick_actions_service.guide()


@router.get("/next")
def next_steps() -> dict:
    return quick_actions_service.next_steps()


@router.get("/search")
def search(query: str = Query(..., min_length=1)) -> dict:
    return quick_actions_service.search(query)
