from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.audit import audit_service
from app.services.memory import memory_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


class SessionCleanupRequest(BaseModel):
    keep_recent: int = Field(default=25, ge=0, le=1000)
    drop_empty_older_than_days: int = Field(default=7, ge=0, le=3650)
    drop_inactive_older_than_days: int = Field(default=90, ge=0, le=3650)
    dry_run: bool = False


@router.get("/list")
def list_sessions(limit: int = Query(default=20, ge=1, le=200)) -> dict:
    items = memory_service.list_sessions(limit=limit)
    return {"items": items, "count": len(items)}


@router.get("/overview")
def session_overview(session_id: str = Query(..., min_length=1, max_length=120)) -> dict:
    return memory_service.session_overview(session_id)


@router.get("/recent-messages")
def recent_messages(session_id: str = Query(..., min_length=1, max_length=120), limit: int = Query(default=10, ge=1, le=100)) -> dict:
    return {"session_id": session_id, "messages": memory_service.recent_messages(session_id, limit=limit)}


@router.post("/cleanup")
def cleanup_sessions(payload: SessionCleanupRequest) -> dict:
    result = memory_service.cleanup_sessions(
        keep_recent=payload.keep_recent,
        drop_empty_older_than_days=payload.drop_empty_older_than_days,
        drop_inactive_older_than_days=payload.drop_inactive_older_than_days,
        dry_run=payload.dry_run,
    )
    audit_service.log_event(
        "session_cleanup",
        {
            "keep_recent": payload.keep_recent,
            "drop_empty_older_than_days": payload.drop_empty_older_than_days,
            "drop_inactive_older_than_days": payload.drop_inactive_older_than_days,
            "dry_run": payload.dry_run,
            "result_ok": result.get("ok"),
            "deleted_count": result.get("deleted_count"),
            "candidate_count": result.get("candidate_count"),
        },
    )
    return result
