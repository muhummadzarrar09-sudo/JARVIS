from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.audit import audit_service
from app.services.process_tool import process_tool

router = APIRouter(prefix="/tools/proc", tags=["processes"])


class ProcTargetRequest(BaseModel):
    target: str = Field(..., min_length=1)


class ProcStartRequest(BaseModel):
    command: str = Field(..., min_length=1)


@router.get("/list")
def proc_list(filter_name: str | None = None) -> dict:
    result = process_tool.list_processes(filter_name=filter_name)
    audit_service.log_event("proc_list", {"filter_name": filter_name, "result_ok": result.get("ok")})
    return result


@router.get("/windows")
def proc_windows() -> dict:
    result = process_tool.list_windows()
    audit_service.log_event("proc_windows", {"result_ok": result.get("ok")})
    return result


@router.post("/start")
def proc_start(payload: ProcStartRequest) -> dict:
    result = process_tool.start_process(payload.command)
    audit_service.log_event("proc_start", {"command": payload.command, "result_ok": result.get("ok")})
    return result


@router.post("/kill")
def proc_kill(payload: ProcTargetRequest) -> dict:
    result = process_tool.kill_process(payload.target)
    audit_service.log_event("proc_kill", {"target": payload.target, "result_ok": result.get("ok")})
    return result
