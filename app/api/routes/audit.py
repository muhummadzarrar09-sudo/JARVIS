from fastapi import APIRouter, Query

from app.services.audit import audit_service

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/recent")
def recent_audit(limit: int = Query(default=20, ge=1, le=200)) -> dict:
    return {"items": audit_service.recent(limit=limit)}
