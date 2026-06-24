from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.services.audit import audit_service
from app.services.database_service import database_service

router = APIRouter(prefix="/database", tags=["database"])


class DatabaseBackupRequest(BaseModel):
    label: str | None = Field(default=None, max_length=40)


class DatabaseRestoreRequest(BaseModel):
    backup_path: str = Field(..., min_length=1, max_length=400)
    create_backup_first: bool = True


class DatabaseBackupDeleteRequest(BaseModel):
    backup_path: str = Field(..., min_length=1, max_length=400)


@router.get("/status")
def database_status() -> dict:
    result = database_service.status()
    audit_service.log_event("database_status", {"result_ok": result.get("ok")})
    return result


@router.get("/backups")
def database_backups(limit: int = Query(default=20, ge=1, le=200)) -> dict:
    result = database_service.list_backups(limit=limit)
    audit_service.log_event("database_backups", {"result_ok": result.get("ok"), "count": result.get("count")})
    return result


@router.get("/backup-file")
def database_backup_file(path: str = Query(..., min_length=1, max_length=400)) -> FileResponse:
    resolved = database_service.resolve_backup_path(path)
    return FileResponse(path=resolved, filename=resolved.name, media_type="application/octet-stream")


@router.post("/backup")
def database_backup(payload: DatabaseBackupRequest) -> dict:
    result = database_service.backup(label=payload.label)
    audit_service.log_event("database_backup", {"label": payload.label, "result_ok": result.get("ok"), "path": result.get("path")})
    return result


@router.post("/backup-delete")
def database_backup_delete(payload: DatabaseBackupDeleteRequest) -> dict:
    result = database_service.delete_backup(payload.backup_path)
    audit_service.log_event("database_backup_delete", {"backup_path": payload.backup_path, "result_ok": result.get("ok")})
    return result


@router.post("/restore")
def database_restore(payload: DatabaseRestoreRequest) -> dict:
    result = database_service.restore(backup_path=payload.backup_path, create_backup_first=payload.create_backup_first)
    audit_service.log_event(
        "database_restore",
        {
            "backup_path": payload.backup_path,
            "create_backup_first": payload.create_backup_first,
            "result_ok": result.get("ok"),
        },
    )
    return result


@router.post("/vacuum")
def database_vacuum() -> dict:
    result = database_service.vacuum()
    audit_service.log_event("database_vacuum", {"result_ok": result.get("ok"), "delta_bytes": result.get("delta_bytes")})
    return result
