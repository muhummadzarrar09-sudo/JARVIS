import subprocess
from typing import Any

from app.core.config import settings


class ShellTool:
    def run(self, command: str) -> dict[str, Any]:
        if not settings.allow_shell_tool:
            return {"ok": False, "error": "Shell tool is disabled in config."}

        try:
            completed = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=settings.shell_timeout_seconds,
            )
            return {
                "ok": completed.returncode == 0,
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": f"Command timed out after {settings.shell_timeout_seconds}s"}
        except Exception as e:  # pragma: no cover
            return {"ok": False, "error": str(e)}


shell_tool = ShellTool()
