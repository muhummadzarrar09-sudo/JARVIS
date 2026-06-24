from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.services.audit import audit_service

router = APIRouter(prefix="/audit", tags=["audit"])


class AuditRotateRequest(BaseModel):
    label: str | None = Field(default=None, max_length=40)
    keep_archives: int = Field(default=10, ge=0, le=200)


class AuditPruneRequest(BaseModel):
    keep_archives: int = Field(default=10, ge=0, le=200)


class AuditArchiveDeleteRequest(BaseModel):
    archive_path: str = Field(..., min_length=1, max_length=400)


@router.get("/status")
def audit_status() -> dict:
    return audit_service.status()


@router.get("/archives")
def audit_archives(limit: int = Query(default=20, ge=1, le=200)) -> dict:
    return audit_service.list_archives(limit=limit)


@router.get("/archive-preview")
def audit_archive_preview(path: str = Query(..., min_length=1, max_length=400), limit: int = Query(default=20, ge=1, le=200)) -> dict:
    return audit_service.preview_archive(archive_path=path, limit=limit)


@router.get("/archive-file")
def audit_archive_file(path: str = Query(..., min_length=1, max_length=400)) -> FileResponse:
    resolved = audit_service.resolve_archive_path(path)
    return FileResponse(path=resolved, filename=resolved.name, media_type="application/x-ndjson")


@router.post("/archive-delete")
def audit_archive_delete(payload: AuditArchiveDeleteRequest) -> dict:
    result = audit_service.delete_archive(payload.archive_path)
    audit_service.log_event("audit_archive_delete", {"archive_path": payload.archive_path, "result_ok": result.get("ok")})
    return result


@router.post("/rotate")
def rotate_audit(payload: AuditRotateRequest) -> dict:
    result = audit_service.rotate(label=payload.label, keep_archives=payload.keep_archives)
    audit_service.log_event("audit_rotate", {"label": payload.label, "keep_archives": payload.keep_archives, "result_ok": result.get("ok")})
    return result


@router.post("/prune")
def prune_audit(payload: AuditPruneRequest) -> dict:
    result = audit_service.prune_archives(keep=payload.keep_archives)
    audit_service.log_event("audit_prune", {"keep_archives": payload.keep_archives, "result_ok": result.get("ok"), "removed_count": result.get("removed_count")})
    return result


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
