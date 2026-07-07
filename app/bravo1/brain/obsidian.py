from __future__ import annotations

from pathlib import Path

from bravo1.core.session import SessionState


class ObsidianBrain:
    def __init__(self, brain_dir: Path) -> None:
        self.brain_dir = brain_dir
        self.brain_dir.mkdir(parents=True, exist_ok=True)
        self.active_path = self.brain_dir / "active.md"

    def bootstrap(self) -> None:
        if self.active_path.exists():
            return
        self.active_path.write_text(
            "# BRAVO-1 Active Context\n\n"
            "## What matters now\n- Define the next operator loop.\n\n"
            "## Current project\n- BRAVO-1 rebuild\n\n"
            "## Current goal\n- Stand up the new operator spine.\n\n"
            "## Last primary action\n- Start the rebuild scaffold.\n",
            encoding="utf-8",
        )

    def read_active(self) -> str:
        self.bootstrap()
        return self.active_path.read_text(encoding="utf-8")

    def sync_from_session(self, state: SessionState, primary_action: str) -> None:
        self.bootstrap()
        goal = state.current_goal or "Stand up the new operator spine."
        project = state.current_project or "BRAVO-1 rebuild"
        self.active_path.write_text(
            "# BRAVO-1 Active Context\n\n"
            f"## What matters now\n- {primary_action}\n\n"
            f"## Current project\n- {project}\n\n"
            f"## Current goal\n- {goal}\n\n"
            f"## Last primary action\n- {primary_action}\n",
            encoding="utf-8",
        )
