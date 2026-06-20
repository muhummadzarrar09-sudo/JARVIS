from fastapi import APIRouter, Query

from app.services.memory import memory_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/list")
def list_sessions(limit: int = Query(default=20, ge=1, le=200)) -> dict:
    items = memory_service.list_sessions(limit=limit)
    return {"items": items, "count": len(items)}


@router.get("/overview")
def session_overview(session_id: str = Query(...)) -> dict:
    return memory_service.session_overview(session_id)


@router.get("/recent-messages")
def recent_messages(session_id: str = Query(...), limit: int = Query(default=10, ge=1, le=100)) -> dict:
    return {"session_id": session_id, "messages": memory_service.recent_messages(session_id, limit=limit)}
