from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.app_wrapper_service import app_wrapper_service
from app.services.audit import audit_service

router = APIRouter(prefix="/tools/apps", tags=["app-wrappers"])


class AppActionRequest(BaseModel):
    action: str = Field(..., min_length=1)
    name: str | None = None
    target: str | None = None
    text: str | None = None
    exact: bool = False


@router.get("/wrappers")
def list_wrappers() -> dict:
    result = app_wrapper_service.list_wrappers()
    audit_service.log_event("app_wrappers_list", {"result_ok": result.get("ok")})
    return result


@router.get("/recipes")
def list_recipes() -> dict:
    result = app_wrapper_service.list_recipes()
    audit_service.log_event("app_recipes_list", {"result_ok": result.get("ok")})
    return result


@router.get("/status")
def wrapper_status(name: str | None = Query(default=None)) -> dict:
    result = app_wrapper_service.wrapper_status(name)
    audit_service.log_event("app_wrapper_status", {"name": name, "result_ok": result.get("ok")})
    return result


@router.get("/project-context")
def project_context(target: str | None = Query(default=None)) -> dict:
    result = app_wrapper_service.current_project_context(target)
    audit_service.log_event("app_project_context", {"target": target, "result_ok": result.get("ok")})
    return result


@router.get("/doctor")
def wrapper_doctor(name: str | None = Query(default=None)) -> dict:
    result = app_wrapper_service.wrapper_doctor(name)
    audit_service.log_event("app_wrapper_doctor", {"name": name, "result_ok": result.get("ok")})
    return result


@router.post("/action")
def app_action(payload: AppActionRequest) -> dict:
    action = payload.action.strip().lower()

    if action == "list":
        result = app_wrapper_service.list_wrappers()
    elif action == "recipes":
        result = app_wrapper_service.list_recipes()
    elif action in {"status", "state"}:
        result = app_wrapper_service.wrapper_status(payload.name)
    elif action in {"doctor", "diagnose"}:
        result = app_wrapper_service.wrapper_doctor(payload.name)
    elif action in {"project", "context", "project_context"}:
        result = app_wrapper_service.current_project_context(payload.target)
    elif action == "reset":
        result = app_wrapper_service.reset_wrapper_state(payload.name)
    elif action == "recipe":
        result = app_wrapper_service.run_recipe(payload.name or "", target=payload.target, text=payload.text)
    elif action == "open":
        result = app_wrapper_service.open_app(payload.name or "", target=payload.target)
    elif action == "ensure":
        result = app_wrapper_service.ensure_app(payload.name or "", target=payload.target, exact=payload.exact)
    elif action == "focus":
        result = app_wrapper_service.focus_app(payload.name or "", exact=payload.exact)
    elif action == "note":
        result = app_wrapper_service.quick_note(payload.text or "")
    elif action == "explore":
        result = app_wrapper_service.open_path_in_explorer(payload.target or "")
    elif action == "code":
        result = app_wrapper_service.open_path_in_vscode(payload.target or "")
    elif action == "browse":
        result = app_wrapper_service.open_url_in_browser(payload.target or "")
    else:
        result = {"ok": False, "error": f"Unknown app wrapper action: {payload.action}"}

    audit_service.log_event(
        "app_wrapper_action",
        {
            "action": action,
            "name": payload.name,
            "target": payload.target,
            "text_present": bool(payload.text),
            "exact": payload.exact,
            "result_ok": result.get("ok"),
        },
    )
    return result
