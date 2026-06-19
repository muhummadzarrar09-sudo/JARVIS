from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.audit import audit_service
from app.services.shell_tool import shell_tool

router = APIRouter(prefix="/tools", tags=["tools"])


class ShellRequest(BaseModel):
    command: str = Field(..., min_length=1)


@router.post("/shell")
def run_shell(payload: ShellRequest) -> dict:
    result = shell_tool.run(payload.command)
    audit_service.log_event("shell_command_direct", {"command": payload.command, "result": result})
    return result
