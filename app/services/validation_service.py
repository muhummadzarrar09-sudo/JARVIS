import importlib.util
import os
import platform
import shutil
import sys
from typing import Any

from app.core.config import settings
from app.services.app_wrapper_service import app_wrapper_service
from app.services.audit import audit_service
from app.services.browser_tool import browser_tool
from app.services.database_service import database_service
from app.services.desktop_tool import desktop_tool
from app.services.progress_service import progress_service
from app.services.model_service import model_service
from app.services.recovery_service import recovery_service


class ValidationService:
    def report(self) -> dict[str, Any]:
        browser = browser_tool.available_browsers()
        browser_context = app_wrapper_service.current_browser_context()
        browser_doctor = app_wrapper_service.wrapper_doctor("browser")
        desktop_safety = desktop_tool.safety_status()
        desktop_active = desktop_tool.active_window()
        desktop_windows = desktop_tool.list_windows()
        model_status = model_service.status()
        database_status = database_service.status()
        audit_status = audit_service.status()
        recovery_packs = recovery_service.list_packs(limit=12)
        phase4 = progress_service.phase4_status()
        phase5 = progress_service.phase5_status()

        binaries = {
            "python": shutil.which("python") or shutil.which("python3"),
            "powershell": shutil.which("powershell") or shutil.which("pwsh"),
            "code": shutil.which("code"),
        }

        pywebview_installed = importlib.util.find_spec("webview") is not None
        app_security = {
            "allowed_origins": [item.strip() for item in settings.app_allowed_origins.split(",") if item.strip()],
            "allowed_hosts": [item.strip() for item in settings.app_allowed_hosts.split(",") if item.strip()],
            "request_max_bytes": settings.app_request_max_bytes,
        }
        shell_launcher = {
            "ready": pywebview_installed,
            "pywebview_installed": pywebview_installed,
            "entrypoint": "desktop_shell/app.py",
            "start_script": "scripts/start-shell.ps1",
            "url": f"http://{settings.app_host}:{settings.app_port}/ui/app-shell",
        }

        blockers = []
        if not browser_doctor.get("item", {}).get("ready"):
            blockers.append("Browser automation is not fully ready on this machine.")
        if not binaries.get("code"):
            blockers.append("VS Code CLI launcher (`code`) is not available on PATH.")
        if not binaries.get("powershell") and os.name == "nt":
            blockers.append("PowerShell executable was not found on PATH.")
        provider = model_status.get("provider", {})
        if provider.get("configured_provider") == "llama_cpp" and not provider.get("llama_cpp_installed"):
            blockers.append("DEFAULT_MODEL_PROVIDER is set to llama_cpp but llama-cpp-python is not installed.")
        if provider.get("configured_provider") == "llama_cpp" and not provider.get("selected_model_exists"):
            blockers.append("DEFAULT_MODEL_PROVIDER is set to llama_cpp but no configured GGUF model could be found.")
        if database_status.get("exists") and database_status.get("integrity_check") not in {None, "ok"}:
            blockers.append("SQLite integrity_check did not return ok.")
        if audit_status.get("exists") and (audit_status.get("size_bytes") or 0) > 5_000_000:
            blockers.append("Audit log is getting large and should be rotated soon.")
        if (database_status.get("session_count") or 0) > 300:
            blockers.append("Session history is getting large and may benefit from a cleanup pass.")

        next_steps = []
        if blockers:
            next_steps.append("Run the browser/desktop install scripts and re-check setup.")
            next_steps.append("Open /browser and /doctor in the console to inspect readiness.")
        else:
            next_steps.append("Try launching your preferred browser and a desktop wrapper flow.")

        if not shell_launcher.get("ready"):
            next_steps.append("Install shell support with .\\scripts\\install-shell.ps1 if you want the packaged desktop shell window.")
        else:
            next_steps.append("Launch the packaged shell with .\\scripts\\start-shell.ps1 and validate the live command-center flow.")

        if provider.get("effective_provider") == "mock" and model_status.get("discovered", {}).get("count"):
            next_steps.append("Switch to downloaded local GGUF models with .\\scripts\\use-local-models.ps1 or the /models/use-local API.")
        if audit_status.get("exists") and (audit_status.get("size_bytes") or 0) > 2_000_000:
            next_steps.append("Rotate the audit log with .\\scripts\\rotate-audit.ps1 if you want to keep maintenance logs tidy.")
        if (database_status.get("session_count") or 0) > 100:
            next_steps.append("Run a session cleanup pass if you want to trim older inactive chat history.")
        if (recovery_packs.get("count") or 0) == 0:
            next_steps.append("Create a recovery pack so you have a fuller export checkpoint before bigger experiments.")

        return {
            "ok": True,
            "platform": platform.platform(),
            "python_version": sys.version.split()[0],
            "binaries": binaries,
            "browser_available": browser,
            "browser_context": browser_context,
            "browser_doctor": browser_doctor,
            "desktop_safety": desktop_safety,
            "desktop_active": desktop_active,
            "desktop_windows": desktop_windows,
            "model_status": model_status,
            "database_status": database_status,
            "audit_status": audit_status,
            "recovery_packs": recovery_packs,
            "app_security": app_security,
            "shell_launcher": shell_launcher,
            "phase4": phase4,
            "phase5": phase5,
            "blockers": blockers,
            "plain_english": "This report shows what JARVIS can detect about your local machine right now.",
            "next_steps": next_steps,
        }


validation_service = ValidationService()
