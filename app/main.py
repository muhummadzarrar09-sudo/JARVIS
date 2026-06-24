from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.routes.apps import router as apps_router
from app.api.routes.audit import router as audit_router
from app.api.routes.browser import router as browser_router
from app.api.routes.chat import router as chat_router
from app.api.routes.checkpoints import router as checkpoints_router
from app.api.routes.database import router as database_router
from app.api.routes.desktop import router as desktop_router
from app.api.routes.files import router as files_router
from app.api.routes.health import router as health_router
from app.api.routes.models import router as models_router
from app.api.routes.maintenance import router as maintenance_router
from app.api.routes.operator import router as operator_router
from app.api.routes.processes import router as processes_router
from app.api.routes.progress import router as progress_router
from app.api.routes.quick_actions import router as quick_actions_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.shell import router as shell_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.tool_registry import router as tool_registry_router
from app.api.routes.tools import router as tools_router
from app.api.routes.ui import router as ui_router
from app.api.routes.validation import router as validation_router
from app.api.routes.voice import router as voice_router
from app.core.config import settings
from app.services.audit import audit_service
from app.services.browser_tool import browser_tool
from app.services.memory import memory_service
from app.services.task_service import task_service

app = FastAPI(title=settings.app_name, version="0.1.0")

allowed_origins = [item.strip() for item in settings.app_allowed_origins.split(",") if item.strip()]
allowed_hosts = [item.strip() for item in settings.app_allowed_hosts.split(",") if item.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts or ["127.0.0.1", "localhost"])


@app.middleware("http")
async def request_size_limit_middleware(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > settings.app_request_max_bytes:
                return JSONResponse(
                    status_code=413,
                    content={
                        "ok": False,
                        "error": f"Request body exceeds APP_REQUEST_MAX_BYTES ({settings.app_request_max_bytes}).",
                    },
                )
        except ValueError:
            pass
    return await call_next(request)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' data: blob:; "
        "img-src 'self' data: blob:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; "
        "connect-src 'self'; "
        "font-src 'self' data:; "
        "frame-ancestors 'self'; base-uri 'self'; form-action 'self'"
    )
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    audit_service.log_event(
        "unhandled_exception",
        {
            "path": str(request.url.path),
            "method": request.method,
            "error": str(exc),
        },
    )
    return JSONResponse(status_code=500, content={"ok": False, "error": "Internal server error."})


app.include_router(health_router)
app.include_router(chat_router)
app.include_router(tools_router)
app.include_router(tool_registry_router)
app.include_router(apps_router)
app.include_router(progress_router)
app.include_router(quick_actions_router)
app.include_router(files_router)
app.include_router(browser_router)
app.include_router(desktop_router)
app.include_router(processes_router)
app.include_router(checkpoints_router)
app.include_router(database_router)
app.include_router(tasks_router)
app.include_router(audit_router)
app.include_router(sessions_router)
app.include_router(shell_router)
app.include_router(ui_router)
app.include_router(validation_router)
app.include_router(voice_router)
app.include_router(operator_router)
app.include_router(models_router)
app.include_router(maintenance_router)


@app.on_event("startup")
def on_startup() -> None:
    memory_service.initialize()
    task_service.initialize()
    audit_service.log_event(
        event_type="startup",
        payload={"app_name": settings.app_name, "message": "JARVIS Local started"},
    )


@app.on_event("shutdown")
def on_shutdown() -> None:
    browser_tool.close()
    audit_service.log_event(
        event_type="shutdown",
        payload={"app_name": settings.app_name, "message": "JARVIS Local stopped"},
    )
