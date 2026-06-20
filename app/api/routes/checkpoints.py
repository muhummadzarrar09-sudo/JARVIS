from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.audit import audit_service
from app.services.checkpoint_service import checkpoint_service

router = APIRouter(prefix="/checkpoints", tags=["checkpoints"])


class CheckpointCreateRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    note: str | None = None


@router.post("/create")
def create_checkpoint(payload: CheckpointCreateRequest) -> dict:
    result = checkpoint_service.create(payload.session_id, note=payload.note)
    audit_service.log_event(
        "checkpoint_create",
        {"session_id": payload.session_id, "note": payload.note, "result_ok": result.get("ok")},
    )
    return result


@router.get("/get")
def get_checkpoint(session_id: str) -> dict:
    result = checkpoint_service.load(session_id)
    audit_service.log_event("checkpoint_get", {"session_id": session_id, "result_ok": result.get("ok")})
    return result
