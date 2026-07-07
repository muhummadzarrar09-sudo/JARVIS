from __future__ import annotations

from pathlib import Path


class ObsidianBrain:
    def __init__(self, brain_dir: Path) -> None:
        self.brain_dir = brain_dir
        self.brain_dir.mkdir(parents=True, exist_ok=True)
        self.active_path = self.brain_dir / "active.md"

    def bootstrap(self) -> None:
        if self.active_path.exists():
            return
        self.active_path.write_text(
            "# BRAVO-1 Active Context\n\n## What matters now\n- Define the next operator loop.\n\n## Current project\n- BRAVO-1 rebuild\n",
            encoding="utf-8",
        )

    def read_active(self) -> str:
        self.bootstrap()
        return self.active_path.read_text(encoding="utf-8")
