from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.audit import audit_service
from app.services.file_tool import file_tool

router = APIRouter(prefix="/tools/fs", tags=["filesystem"])


class FileListRequest(BaseModel):
    path: str = Field(default=".")


class FileReadRequest(BaseModel):
    path: str = Field(..., min_length=1)


class FileWriteRequest(BaseModel):
    path: str = Field(..., min_length=1)
    content: str = Field(default="")
    append: bool = False


@router.post("/list")
def fs_list(payload: FileListRequest) -> dict:
    result = file_tool.list_dir(payload.path)
    audit_service.log_event("fs_list", {"path": payload.path, "result_ok": result.get("ok")})
    return result


@router.post("/read")
def fs_read(payload: FileReadRequest) -> dict:
    result = file_tool.read_text(payload.path)
    audit_service.log_event("fs_read", {"path": payload.path, "result_ok": result.get("ok")})
    return result


@router.post("/write")
def fs_write(payload: FileWriteRequest) -> dict:
    result = file_tool.write_text(payload.path, payload.content, append=payload.append)
    audit_service.log_event(
        "fs_write",
        {"path": payload.path, "append": payload.append, "result_ok": result.get("ok")},
    )
    return result


@router.post("/mkdir")
def fs_mkdir(payload: FileListRequest) -> dict:
    result = file_tool.make_dir(payload.path)
    audit_service.log_event("fs_mkdir", {"path": payload.path, "result_ok": result.get("ok")})
    return result
