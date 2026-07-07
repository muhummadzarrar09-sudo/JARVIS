from fastapi import APIRouter, Query

from app.services.quick_actions_service import quick_actions_service

router = APIRouter(prefix="/quick-actions", tags=["quick-actions"])


@router.get("/guide")
def guide() -> dict:
    return quick_actions_service.guide()


@router.get("/next")
def next_steps() -> dict:
    return quick_actions_service.next_steps()


@router.get("/brief")
def brief() -> dict:
    return quick_actions_service.executive_brief()


@router.get("/today")
def today() -> dict:
    return quick_actions_service.today_brief()


@router.get("/focus")
def focus() -> dict:
    return quick_actions_service.focus()


@router.get("/recent-work")
def recent_work() -> dict:
    return quick_actions_service.recent_work_summary()


@router.get("/project")
def project() -> dict:
    return quick_actions_service.project_intelligence()


@router.get("/resume-work")
def resume_work() -> dict:
    return quick_actions_service.resume_work_packet()


@router.get("/progress")
def progress() -> dict:
    return quick_actions_service.progress()


@router.get("/setup")
def setup() -> dict:
    return quick_actions_service.setup_summary()


@router.get("/search")
def search(query: str = Query(..., min_length=1)) -> dict:
    return quick_actions_service.search(query)
