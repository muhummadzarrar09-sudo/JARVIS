from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.audit import audit_service
from app.services.desktop_tool import desktop_tool

router = APIRouter(prefix="/tools/desktop", tags=["desktop"])


class DesktopActionRequest(BaseModel):
    action: str = Field(..., min_length=1)
    title: str | None = None
    text: str | None = None
    key: str | None = None
    keys: list[str] | None = None
    path: str | None = None
    x: int | None = None
    y: int | None = None
    handle: int | None = None
    match_index: int = 0
    preview: bool = False
    button: str = "left"
    exact: bool = False


@router.get("/windows")
def desktop_windows() -> dict:
    result = desktop_tool.list_windows()
    audit_service.log_event("desktop_windows", {"result_ok": result.get("ok")})
    return result


@router.get("/find")
def desktop_find(title: str, exact: bool = False) -> dict:
    result = desktop_tool.find_windows(title=title, exact=exact)
    audit_service.log_event("desktop_find", {"title": title, "exact": exact, "result_ok": result.get("ok")})
    return result


@router.get("/safety")
def desktop_safety() -> dict:
    result = desktop_tool.safety_status()
    audit_service.log_event("desktop_safety", {"result_ok": result.get("ok")})
    return result


@router.get("/active")
def desktop_active() -> dict:
    result = desktop_tool.active_window()
    audit_service.log_event("desktop_active", {"result_ok": result.get("ok")})
    return result


@router.get("/screen")
def desktop_screen() -> dict:
    result = desktop_tool.screen_info()
    audit_service.log_event("desktop_screen", {"result_ok": result.get("ok")})
    return result


@router.post("/action")
def desktop_action(payload: DesktopActionRequest) -> dict:
    action = payload.action.strip().lower()

    if payload.preview:
        preview_payload = {
            "title": payload.title,
            "text": payload.text,
            "key": payload.key,
            "keys": payload.keys,
            "path": payload.path,
            "x": payload.x,
            "y": payload.y,
            "handle": payload.handle,
            "match_index": payload.match_index,
            "button": payload.button,
            "exact": payload.exact,
        }
        result = desktop_tool.preview_action(action, preview_payload)
    elif action == "windows":
        result = desktop_tool.list_windows()
    elif action == "find":
        result = desktop_tool.find_windows(payload.title or "", exact=payload.exact)
    elif action == "active":
        result = desktop_tool.active_window()
    elif action == "screen":
        result = desktop_tool.screen_info()
    elif action == "focus":
        result = desktop_tool.focus_window(payload.title or "", exact=payload.exact, match_index=payload.match_index)
    elif action == "focus_handle":
        result = desktop_tool.focus_handle(payload.handle or 0)
    elif action == "undo_focus":
        result = desktop_tool.undo_last_focus()
    elif action == "safety":
        result = desktop_tool.safety_status()
    elif action == "type":
        result = desktop_tool.type_text(payload.text or "")
    elif action == "press":
        result = desktop_tool.press_key(payload.key or "")
    elif action == "hotkey":
        result = desktop_tool.hotkey(payload.keys or [])
    elif action == "click":
        result = desktop_tool.click(payload.x, payload.y, button=payload.button)
    elif action == "screenshot":
        result = desktop_tool.screenshot(payload.path)
    else:
        result = {"ok": False, "error": f"Unknown desktop action: {payload.action}"}

    audit_payload = {
        "action": action,
        "title": payload.title,
        "key": payload.key,
        "keys": payload.keys,
        "path": payload.path,
        "coords": [payload.x, payload.y],
        "result_ok": result.get("ok"),
        "guard": result.get("guard"),
    }
    if result.get("path"):
        audit_payload["artifact_path"] = result.get("path")
    if result.get("active_window"):
        audit_payload["active_window"] = result.get("active_window")
    audit_service.log_event("desktop_action", audit_payload)
    return result
