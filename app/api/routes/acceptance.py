from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.acceptance_service import acceptance_service
from app.services.audit import audit_service

router = APIRouter(prefix="/acceptance", tags=["acceptance"])


class AcceptanceRunRequest(BaseModel):
    deep: bool = False


class AcceptanceExportRequest(BaseModel):
    output_path: str | None = Field(default=None, max_length=400)


@router.get("/status")
def acceptance_status() -> dict:
    return acceptance_service.status()


@router.get("/history")
def acceptance_history(limit: int = Query(default=20, ge=1, le=100)) -> dict:
    return acceptance_service.history(limit=limit)


@router.get("/final-blockers")
def acceptance_final_blockers() -> dict:
    return acceptance_service.final_blockers()


@router.post("/run")
def acceptance_run(payload: AcceptanceRunRequest) -> dict:
    result = acceptance_service.run(deep=payload.deep)
    audit_service.log_event("acceptance_run", {"result_ok": result.get("ok"), "overall": result.get("overall"), "deep": payload.deep})
    return result


@router.post("/export")
def acceptance_export(payload: AcceptanceExportRequest) -> dict:
    result = acceptance_service.export_latest(output_path=payload.output_path)
    audit_service.log_event("acceptance_export", {"result_ok": result.get("ok"), "path": result.get("path")})
    return result


@router.post("/reset")
def acceptance_reset() -> dict:
    result = acceptance_service.reset()
    audit_service.log_event("acceptance_reset", {"result_ok": result.get("ok")})
    return result
