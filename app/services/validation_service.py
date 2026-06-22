import os
import platform
import shutil
import sys
from typing import Any

from app.services.app_wrapper_service import app_wrapper_service
from app.services.browser_tool import browser_tool
from app.services.desktop_tool import desktop_tool
from app.services.progress_service import progress_service


class ValidationService:
    def report(self) -> dict[str, Any]:
        browser = browser_tool.available_browsers()
        browser_doctor = app_wrapper_service.wrapper_doctor("browser")
        desktop_safety = desktop_tool.safety_status()
        phase4 = progress_service.phase4_status()

        binaries = {
            "python": shutil.which("python") or shutil.which("python3"),
            "powershell": shutil.which("powershell") or shutil.which("pwsh"),
            "code": shutil.which("code"),
        }

        blockers = []
        if not browser_doctor.get("item", {}).get("ready"):
            blockers.append("Browser automation is not fully ready on this machine.")
        if not binaries.get("code"):
            blockers.append("VS Code CLI launcher (`code`) is not available on PATH.")
        if not binaries.get("powershell") and os.name == "nt":
            blockers.append("PowerShell executable was not found on PATH.")

        next_steps = []
        if blockers:
            next_steps.append("Run the browser/desktop install scripts and re-check setup.")
            next_steps.append("Open /browser and /doctor in the console to inspect readiness.")
        else:
            next_steps.append("Try launching your preferred browser and a desktop wrapper flow.")

        return {
            "ok": True,
            "platform": platform.platform(),
            "python_version": sys.version.split()[0],
            "binaries": binaries,
            "browser_available": browser,
            "browser_doctor": browser_doctor,
            "desktop_safety": desktop_safety,
            "phase4": phase4,
            "blockers": blockers,
            "plain_english": "This report shows what JARVIS can detect about your local machine right now.",
            "next_steps": next_steps,
        }


validation_service = ValidationService()
