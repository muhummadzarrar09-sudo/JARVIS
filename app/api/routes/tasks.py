from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.audit import audit_service
from app.services.task_service import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1)
    session_id: str | None = None
    priority: str = Field(default="normal")
    notes: str | None = None


class TaskStatusRequest(BaseModel):
    task_id: int = Field(..., ge=1)
    status: str = Field(..., min_length=1)


@router.get("")
def list_tasks(status: str | None = Query(default=None), limit: int = Query(default=100, ge=1, le=500)) -> dict:
    items = task_service.list_tasks(status=status, limit=limit)
    return {"items": items, "count": len(items)}


@router.post("")
def create_task(payload: TaskCreateRequest) -> dict:
    result = task_service.create_task(
        title=payload.title,
        session_id=payload.session_id,
        priority=payload.priority,
        notes=payload.notes,
    )
    audit_service.log_event("task_create", {"title": payload.title, "result": result})
    return result


@router.get("/next")
def next_task() -> dict:
    result = task_service.next_task()
    return result


@router.get("/summary")
def task_summary() -> dict:
    return task_service.task_summary()


@router.post("/status")
def update_task_status(payload: TaskStatusRequest) -> dict:
    result = task_service.update_status(payload.task_id, payload.status)
    audit_service.log_event(
        "task_status_update",
        {"task_id": payload.task_id, "status": payload.status, "result_ok": result.get("ok", True)},
    )
    return result
