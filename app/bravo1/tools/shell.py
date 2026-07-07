from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ShellTool:
    timeout_seconds: int
    default_cwd: Path

    def run(self, command: str, cwd: str | None = None) -> dict:
        clean = (command or "").strip()
        if not clean:
            return {"ok": False, "error": "Shell command is required."}

        working_dir = Path(cwd).resolve() if cwd else self.default_cwd.resolve()
        if not working_dir.exists() or not working_dir.is_dir():
            return {"ok": False, "error": f"Invalid working directory: {working_dir}"}

        try:
            completed = subprocess.run(
                clean,
                shell=True,
                cwd=str(working_dir),
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            return {
                "ok": completed.returncode == 0,
                "command": clean,
                "cwd": str(working_dir),
                "returncode": completed.returncode,
                "stdout": completed.stdout.strip(),
                "stderr": completed.stderr.strip(),
                "plain_english": "Shell command executed." if completed.returncode == 0 else "Shell command returned a non-zero exit code.",
            }
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "command": clean,
                "cwd": str(working_dir),
                "error": f"Shell command timed out after {self.timeout_seconds} seconds.",
            }
