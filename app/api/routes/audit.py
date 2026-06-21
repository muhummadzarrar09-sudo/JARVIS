from fastapi import APIRouter, Query

from app.services.audit import audit_service

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/recent")
def recent_audit(
    limit: int = Query(default=20, ge=1, le=200),
    event_type: str | None = Query(default=None),
    session_id: str | None = Query(default=None),
) -> dict:
    return {"items": audit_service.recent(limit=limit, event_type=event_type, session_id=session_id)}


@router.get("/timeline")
def audit_timeline(
    limit: int = Query(default=30, ge=1, le=300),
    session_id: str | None = Query(default=None),
) -> dict:
    return {"items": audit_service.timeline(session_id=session_id, limit=limit)}


@router.get("/summary")
def audit_summary(session_id: str | None = Query(default=None)) -> dict:
    return audit_service.summary(session_id=session_id)


@router.get("/operator-summary")
def audit_operator_summary(session_id: str | None = Query(default=None)) -> dict:
    return audit_service.operator_summary(session_id=session_id)


@router.get("/replay")
def audit_replay(session_id: str | None = Query(default=None), limit: int = Query(default=12, ge=1, le=100)) -> dict:
    return {"items": audit_service.replay_candidates(session_id=session_id, limit=limit)}
