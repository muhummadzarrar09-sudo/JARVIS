from __future__ import annotations

import importlib.util
import json
import os
import platform
import subprocess
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class WindowsAdapter:
    provider: str = "uia-bootstrap"

    def _powershell(self, script: str) -> dict[str, Any]:
        try:
            completed = subprocess.run(
                ["powershell", "-NoProfile", "-Command", script],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if completed.returncode != 0:
                return {"ok": False, "error": completed.stderr.strip() or completed.stdout.strip()}
            return {"ok": True, "stdout": completed.stdout.strip()}
        except OSError as exc:
            return {"ok": False, "error": str(exc)}

    def status(self) -> dict:
        pywinauto_installed = importlib.util.find_spec("pywinauto") is not None
        pyautogui_installed = importlib.util.find_spec("pyautogui") is not None
        is_windows = os.name == "nt"
        return {
            "ok": True,
            "provider": self.provider,
            "platform": platform.platform(),
            "is_windows": is_windows,
            "pywinauto_installed": pywinauto_installed,
            "pyautogui_installed": pyautogui_installed,
            "plain_english": "This is the current Windows-control adapter status for BRAVO-1.",
            "next_action": "Install pywinauto later to begin the real UIA-first Windows control pass." if not pywinauto_installed else "Windows adapter prerequisites look good for the next control pass.",
        }

    def list_windows(self) -> dict:
        if os.name != "nt":
            return {
                "ok": False,
                "error": "Window enumeration currently targets Windows only.",
                "platform": platform.platform(),
            }
        result = self._powershell(
            "Get-Process | Where-Object {$_.MainWindowTitle} | Select-Object Id,ProcessName,MainWindowTitle | ConvertTo-Json -Depth 2"
        )
        if not result.get("ok"):
            return result
        raw = result.get("stdout") or ""
        if not raw:
            return {"ok": True, "count": 0, "items": []}
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            parsed = [parsed]
        return {
            "ok": True,
            "count": len(parsed),
            "items": parsed[:50],
            "plain_english": "This is the current titled-window list from the Windows adapter bootstrap.",
        }

    def inspect(self) -> dict:
        status = self.status()
        windows = self.list_windows() if status.get("is_windows") else {"ok": False, "items": []}
        status["window_count"] = windows.get("count", 0)
        status["sample_windows"] = windows.get("items", [])[:5]
        status["planned_capabilities"] = [
            "enumerate active windows",
            "inspect UIA element tree",
            "focus and switch apps",
            "click/type/scroll via structured desktop actions",
        ]
        status["plain_english"] = "This is the current Windows adapter implementation + future control shape."
        return status
