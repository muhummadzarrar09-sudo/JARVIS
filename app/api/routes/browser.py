from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.audit import audit_service
from app.services.browser_tool import browser_tool

router = APIRouter(prefix="/tools/browser", tags=["browser"])


class BrowserActionRequest(BaseModel):
    action: str = Field(..., min_length=1)
    url: str | None = None
    selector: str | None = None
    text: str | None = None
    key: str | None = None
    path: str | None = None
    headless: bool | None = None
    max_chars: int = Field(default=4000, ge=100, le=20000)


@router.get("/state")
def browser_state() -> dict:
    result = browser_tool.state()
    audit_service.log_event("browser_state", {"result_ok": result.get("ok")})
    return result


@router.post("/action")
def browser_action(payload: BrowserActionRequest) -> dict:
    action = payload.action.strip().lower()

    if action == "start":
        result = browser_tool.start(headless=payload.headless)
    elif action in {"open", "visit", "goto"}:
        result = browser_tool.open_url(payload.url or "", headless=payload.headless)
    elif action == "back":
        result = browser_tool.back()
    elif action == "forward":
        result = browser_tool.forward()
    elif action == "title":
        result = browser_tool.title()
    elif action == "text":
        result = browser_tool.text_snapshot(max_chars=payload.max_chars)
    elif action == "inspect":
        result = browser_tool.inspect(payload.selector or "")
    elif action == "click":
        result = browser_tool.click(payload.selector or "", force=False)
    elif action == "forceclick":
        result = browser_tool.click(payload.selector or "", force=True)
    elif action == "fill":
        result = browser_tool.fill(payload.selector or "", payload.text or "")
    elif action == "press":
        result = browser_tool.press(payload.selector or "", payload.key or "Enter")
    elif action == "screenshot":
        result = browser_tool.screenshot(payload.path)
    elif action == "close":
        result = browser_tool.close()
    else:
        result = {"ok": False, "error": f"Unknown browser action: {payload.action}"}

    audit_service.log_event(
        "browser_action",
        {
            "action": action,
            "url": payload.url,
            "selector": payload.selector,
            "path": payload.path,
            "result_ok": result.get("ok"),
        },
    )
    return result
