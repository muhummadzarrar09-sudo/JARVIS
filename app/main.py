from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.audit import router as audit_router
from app.api.routes.browser import router as browser_router
from app.api.routes.chat import router as chat_router
from app.api.routes.files import router as files_router
from app.api.routes.health import router as health_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.tools import router as tools_router
from app.core.config import settings
from app.services.audit import audit_service
from app.services.browser_tool import browser_tool
from app.services.memory import memory_service

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
app.include_router(files_router)
app.include_router(browser_router)
app.include_router(audit_router)
app.include_router(sessions_router)


@app.on_event("startup")
def on_startup() -> None:
    memory_service.initialize()
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
