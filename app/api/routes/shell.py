from fastapi import APIRouter, Query

from app.services.shell_state_service import shell_state_service

router = APIRouter(prefix="/shell", tags=["shell"])


@router.get("/bootstrap")
def shell_bootstrap() -> dict:
    return shell_state_service.bootstrap()


@router.get("/doctor")
def shell_doctor() -> dict:
    return shell_state_service.doctor()


@router.get("/state")
def shell_state(session_id: str | None = Query(default=None)) -> dict:
    return shell_state_service.snapshot(session_id=session_id)
