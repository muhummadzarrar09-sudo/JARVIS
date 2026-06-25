from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.audit import audit_service
from app.services.runtime_stability_service import runtime_stability_service

router = APIRouter(prefix="/runtime", tags=["runtime"])


class BrowserValidationRequest(BaseModel):
    browsers: list[str] | None = None
    url: str | None = None
    headless: bool | None = None


class DesktopValidationRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    exact: bool = False
    match_index: int = Field(default=0, ge=0, le=20)
    undo: bool = True


@router.get("/browser")
def runtime_browser() -> dict:
    result = runtime_stability_service.browser_summary()
    audit_service.log_event("runtime_browser_summary", {"result_ok": result.get("ok"), "overall": result.get("overall")})
    return result


@router.post("/browser/validate")
def runtime_browser_validate(payload: BrowserValidationRequest) -> dict:
    result = runtime_stability_service.browser_validation_matrix(
        browser_names=payload.browsers,
        url=payload.url,
        headless=payload.headless,
    )
    audit_service.log_event(
        "runtime_browser_validate",
        {
            "result_ok": result.get("ok"),
            "warning_count": result.get("warning_count"),
            "url": payload.url,
            "browsers": payload.browsers,
        },
    )
    return result


@router.get("/desktop")
def runtime_desktop() -> dict:
    result = runtime_stability_service.desktop_summary()
    audit_service.log_event("runtime_desktop_summary", {"result_ok": result.get("ok"), "overall": result.get("overall")})
    return result


@router.post("/desktop/validate")
def runtime_desktop_validate(payload: DesktopValidationRequest) -> dict:
    result = runtime_stability_service.desktop_focus_validation(
        title=payload.title,
        exact=payload.exact,
        match_index=payload.match_index,
        undo=payload.undo,
    )
    audit_service.log_event(
        "runtime_desktop_validate",
        {
            "result_ok": result.get("ok"),
            "warning_count": result.get("warning_count"),
            "title": payload.title,
            "exact": payload.exact,
            "match_index": payload.match_index,
            "undo": payload.undo,
        },
    )
    return result


@router.get("/summary")
def runtime_summary() -> dict:
    result = runtime_stability_service.summary()
    audit_service.log_event("runtime_summary", {"result_ok": result.get("ok"), "overall": result.get("overall")})
    return result
