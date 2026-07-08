from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from bravo1.core.session import SessionState


@dataclass(slots=True)
class SessionSummaryWriter:
    summary_dir: Path

    def __post_init__(self) -> None:
        self.summary_dir.mkdir(parents=True, exist_ok=True)

    def write(
        self,
        state: SessionState,
        trigger: str = "manual",
        active_context: str | None = None,
        project_snapshot: dict | None = None,
    ) -> Path:
        ts = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        path = self.summary_dir / f"session-{ts}.md"
        messages = state.recent_messages[-8:]
        project_snapshot = project_snapshot or {}
        captures = project_snapshot.get("recent_captures") or []
        lines = [
            "# BRAVO-1 Session Summary",
            "",
            f"- session_id: {state.session_id}",
            f"- created_at: {state.created_at}",
            f"- updated_at: {state.updated_at}",
            f"- trigger: {trigger}",
            f"- current_goal: {state.current_goal or 'not set'}",
            f"- current_project: {state.current_project or 'not set'}",
            f"- last_primary_action: {state.last_primary_action or 'not set'}",
            f"- last_summary_path: {state.last_summary_path or 'not set'}",
            "",
            "## Active context",
            "",
            (active_context or "No active context provided.").strip(),
            "",
            "## Project continuity",
            "",
            f"- current_project: {project_snapshot.get('current_project') or state.current_project or 'not set'}",
            f"- current_goal: {project_snapshot.get('current_goal') or state.current_goal or 'not set'}",
            f"- recent_captures: {len(captures)}",
            "",
            "## Recent messages",
            "",
        ]
        if not messages:
            lines.append("- no messages yet")
        else:
            for item in messages:
                role = item.get("role", "unknown")
                content = (item.get("content", "") or "").strip()
                lines.append(f"### {role}")
                lines.append(content or "(empty)")
                lines.append("")
        lines.extend(["## Recent captures", ""])
        if not captures:
            lines.append("- no captures yet")
        else:
            for item in captures[:6]:
                lines.append(f"- {item.get('kind')}: {item.get('text')}")
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        return path
