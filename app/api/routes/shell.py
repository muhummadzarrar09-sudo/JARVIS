from fastapi import APIRouter, Query

from app.services.shell_state_service import shell_state_service

router = APIRouter(prefix="/shell", tags=["shell"])


@router.get("/state")
def shell_state(session_id: str | None = Query(default=None)) -> dict:
    return shell_state_service.snapshot(session_id=session_id)
