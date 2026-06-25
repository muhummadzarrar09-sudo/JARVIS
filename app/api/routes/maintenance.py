from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.services.audit import audit_service
from app.services.maintenance_service import maintenance_service
from app.services.maintenance_settings_service import maintenance_settings_service
from app.services.recovery_service import recovery_service

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


class RecoveryExportRequest(BaseModel):
    label: str | None = Field(default=None, max_length=40)
    include_backups: bool = True
    include_archives: bool = True


class RecoveryImportRequest(BaseModel):
    pack_path: str = Field(..., min_length=1, max_length=400)
    restore_database: bool = True
    restore_audit: bool = True
    restore_wrapper_state: bool = True
    extract_only: bool = False
    create_safety_backup: bool = True


class RecoveryPackDeleteRequest(BaseModel):
    pack_path: str = Field(..., min_length=1, max_length=400)


class MaintenanceSettingsRequest(BaseModel):
    audit_keep: int = Field(default=10, ge=0, le=200)
    cleanup_keep_recent: int = Field(default=25, ge=0, le=1000)
    cleanup_empty_days: int = Field(default=7, ge=0, le=3650)
    cleanup_inactive_days: int = Field(default=90, ge=0, le=3650)


@router.get("/doctor")
def maintenance_doctor() -> dict:
    result = maintenance_service.doctor()
    audit_service.log_event("maintenance_doctor", {"result_ok": result.get("ok"), "overall": result.get("overall")})
    return result


@router.get("/verify")
def maintenance_verify(limit: int = Query(default=5, ge=1, le=50)) -> dict:
    result = maintenance_service.verification_summary(limit=limit)
    audit_service.log_event("maintenance_verify", {"result_ok": result.get("ok"), "overall": result.get("overall"), "limit": limit})
    return result


@router.get("/history")
def maintenance_history(
    limit: int = Query(default=50, ge=1, le=500),
    event_type: str | None = Query(default=None),
    search: str | None = Query(default=None, max_length=200),
) -> dict:
    result = maintenance_service.history(limit=limit, event_type=event_type, search=search)
    audit_service.log_event("maintenance_history", {"result_ok": result.get("ok"), "event_type": event_type, "search": search, "count": result.get("count")})
    return result


@router.get("/settings")
def maintenance_settings() -> dict:
    return maintenance_settings_service.get_settings()


@router.post("/settings")
def save_maintenance_settings(payload: MaintenanceSettingsRequest) -> dict:
    result = maintenance_settings_service.save_settings(
        audit_keep=payload.audit_keep,
        cleanup_keep_recent=payload.cleanup_keep_recent,
        cleanup_empty_days=payload.cleanup_empty_days,
        cleanup_inactive_days=payload.cleanup_inactive_days,
    )
    audit_service.log_event("maintenance_settings", {"result_ok": result.get("ok"), **payload.model_dump()})
    return result


@router.get("/packs")
def maintenance_packs(limit: int = Query(default=20, ge=1, le=200)) -> dict:
    result = recovery_service.list_packs(limit=limit)
    audit_service.log_event("maintenance_packs", {"result_ok": result.get("ok"), "count": result.get("count")})
    return result


@router.get("/pack-preview")
def maintenance_pack_preview(path: str = Query(..., min_length=1, max_length=400)) -> dict:
    result = recovery_service.preview_pack(path)
    audit_service.log_event("maintenance_pack_preview", {"result_ok": result.get("ok"), "path": path})
    return result


@router.get("/pack-file")
def maintenance_pack_file(path: str = Query(..., min_length=1, max_length=400)) -> FileResponse:
    resolved = recovery_service.resolve_pack_path(path)
    return FileResponse(path=resolved, filename=resolved.name, media_type="application/zip")


@router.post("/pack-delete")
def maintenance_pack_delete(payload: RecoveryPackDeleteRequest) -> dict:
    result = recovery_service.delete_pack(payload.pack_path)
    audit_service.log_event("maintenance_pack_delete", {"pack_path": payload.pack_path, "result_ok": result.get("ok")})
    return result


@router.post("/export-pack")
def maintenance_export_pack(payload: RecoveryExportRequest) -> dict:
    result = recovery_service.export_pack(
        label=payload.label,
        include_backups=payload.include_backups,
        include_archives=payload.include_archives,
    )
    audit_service.log_event(
        "maintenance_export_pack",
        {
            "label": payload.label,
            "include_backups": payload.include_backups,
            "include_archives": payload.include_archives,
            "result_ok": result.get("ok"),
            "path": result.get("path"),
        },
    )
    return result


@router.post("/import-pack")
def maintenance_import_pack(payload: RecoveryImportRequest) -> dict:
    result = recovery_service.import_pack(
        pack_path=payload.pack_path,
        restore_database=payload.restore_database,
        restore_audit=payload.restore_audit,
        restore_wrapper_state=payload.restore_wrapper_state,
        extract_only=payload.extract_only,
        create_safety_backup=payload.create_safety_backup,
    )
    audit_service.log_event(
        "maintenance_import_pack",
        {
            "pack_path": payload.pack_path,
            "restore_database": payload.restore_database,
            "restore_audit": payload.restore_audit,
            "restore_wrapper_state": payload.restore_wrapper_state,
            "extract_only": payload.extract_only,
            "create_safety_backup": payload.create_safety_backup,
            "result_ok": result.get("ok"),
        },
    )
    return result
