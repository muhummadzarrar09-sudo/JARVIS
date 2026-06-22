from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.apps import router as apps_router
from app.api.routes.audit import router as audit_router
from app.api.routes.browser import router as browser_router
from app.api.routes.chat import router as chat_router
from app.api.routes.checkpoints import router as checkpoints_router
from app.api.routes.desktop import router as desktop_router
from app.api.routes.files import router as files_router
from app.api.routes.health import router as health_router
from app.api.routes.processes import router as processes_router
from app.api.routes.progress import router as progress_router
from app.api.routes.quick_actions import router as quick_actions_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.tool_registry import router as tool_registry_router
from app.api.routes.tools import router as tools_router
from app.api.routes.ui import router as ui_router
from app.api.routes.validation import router as validation_router
from app.core.config import settings
from app.services.audit import audit_service
from app.services.browser_tool import browser_tool
from app.services.memory import memory_service
from app.services.task_service import task_service

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(tasks_router)
app.include_router(audit_router)
app.include_router(sessions_router)
app.include_router(ui_router)
app.include_router(validation_router)


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
