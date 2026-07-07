from datetime import UTC, datetime
from typing import Any

from app.services.app_wrapper_service import app_wrapper_service
from app.services.memory import memory_service
from app.services.task_service import task_service
from app.services.wrapper_state_service import wrapper_state_service


class ProjectIntelligenceService:
    def _confidence_label(self, score: int) -> str:
        if score >= 92:
            return "very high"
        if score >= 82:
            return "high"
        if score >= 68:
            return "medium"
        return "low"

    def _project_source(self, wrapper_states: dict[str, Any], resolved_path: str | None) -> tuple[str, int, list[str]]:
        matches: list[str] = []
        normalized_resolved = (resolved_path or "").strip().lower()
        for wrapper_name in ("vscode", "terminal", "explorer"):
            state = wrapper_states.get(wrapper_name) or {}
            candidate = (state.get("last_path") or state.get("last_target") or "").strip().lower()
            if candidate and normalized_resolved and candidate == normalized_resolved:
                matches.append(wrapper_name)

        if len(matches) >= 3:
            return "wrapper_consensus", 96, matches
        if len(matches) == 2:
            return "wrapper_majority", 90, matches
        if len(matches) == 1:
            name = matches[0]
            score = 86 if name == "vscode" else 80
            return f"{name}_remembered", score, matches
        if normalized_resolved:
            return "workspace_default", 70, matches
        return "unknown", 48, matches

    def _project_actions(
        self,
        summary: dict[str, Any],
        current_task: dict[str, Any],
        next_task: dict[str, Any],
        browser: dict[str, Any],
    ) -> list[str]:
        actions: list[str | None] = []
        if current_task.get("ok"):
            actions.extend([
                "continue coding",
                "show my tasks",
                "complete current task",
            ])
        elif next_task.get("ok"):
            actions.extend([
                "work on next task",
                "show my tasks",
            ])

        if summary.get("readme"):
            actions.append("open readme")
        actions.extend([
            "review this project",
            "open code here",
            "open terminal here",
            "resume project",
        ])
        if browser.get("remembered_url"):
            actions.append("open browser")

        deduped: list[str] = []
        for item in actions:
            cleaned = (item or "").strip()
            if cleaned and cleaned not in deduped:
                deduped.append(cleaned)
        return deduped[:6]

    def _resume_packet(self, summary: dict[str, Any], browser: dict[str, Any]) -> list[dict[str, Any]]:
        steps: list[dict[str, Any]] = []
        if summary.get("readme"):
            steps.append(
                {
                    "label": "Recover context",
                    "say": "open readme",
                    "why": "Use the README as the fastest low-noise context rebuild.",
                }
            )
        steps.append(
            {
                "label": "Re-open code",
                "say": "open code here",
                "why": "Bring the current project back into the editor immediately.",
            }
        )
        steps.append(
            {
                "label": "Re-open terminal",
                "say": "open terminal here",
                "why": "Restore the execution lane for the project.",
            }
        )
        if browser.get("remembered_url"):
            steps.append(
                {
                    "label": "Re-open browser thread",
                    "say": "open browser",
                    "why": "The project has a remembered browser thread you can continue.",
                }
            )
        return steps[:4]

    def _project_watchouts(self, blockers: list[dict[str, Any]], summary: dict[str, Any]) -> list[str]:
        watchouts = [
            f"{item.get('name')}: {item.get('notes')}"
            for item in blockers
            if item.get("name") and item.get("notes")
        ]
        if not summary.get("readme"):
            watchouts.append("No README was detected, so project recovery may rely more on code and terminal context.")
        return watchouts[:3]

    def _recent_captures(self) -> list[dict[str, Any]]:
        state = wrapper_state_service.get_state("project")
        captures = state.get("captures")
        if not isinstance(captures, list):
            return []
        cleaned: list[dict[str, Any]] = []
        for item in captures[:12]:
            if isinstance(item, dict):
                cleaned.append(item)
        return cleaned[:8]

    def current(self, target: str | None = None) -> dict[str, Any]:
        project = app_wrapper_service.current_project_context(target)
        if not project.get("ok"):
            return project

        summary = project.get("summary") or {}
        wrapper_states = project.get("wrapper_states") or {}
        browser = app_wrapper_service.current_browser_context()
        current_task = task_service.current_task()
        next_task = task_service.next_task()
        task_summary = task_service.task_summary()
        sessions = memory_service.list_sessions(limit=3)
        blockers = [
            {"name": item.get("name"), "notes": item.get("notes")}
            for item in (app_wrapper_service.wrapper_doctor().get("items") or [])
            if not item.get("ready")
        ][:4]

        source, confidence_score, source_matches = self._project_source(wrapper_states, project.get("path"))
        actions = self._project_actions(summary, current_task, next_task, browser)
        resume_packet = self._resume_packet(summary, browser)
        watchouts = self._project_watchouts(blockers, summary)
        recent_captures = self._recent_captures()
        reentry_hint = None
        if summary.get("path"):
            reentry_hint = f"Current project is anchored at {summary.get('path')} via {source.replace('_', ' ')}."

        return {
            "ok": True,
            "path": project.get("path"),
            "summary": summary,
            "source": source,
            "source_matches": source_matches,
            "confidence": confidence_score / 100,
            "confidence_label": self._confidence_label(confidence_score),
            "wrapper_states": wrapper_states,
            "recommended_recipes": project.get("recommended_recipes") or [],
            "current_task": current_task if current_task.get("ok") else None,
            "next_task": next_task if next_task.get("ok") else None,
            "task_summary": task_summary,
            "recent_sessions": sessions,
            "remembered_browser": browser.get("remembered_url"),
            "actions": actions,
            "resume_packet": resume_packet,
            "reentry_hint": reentry_hint,
            "watchouts": watchouts,
            "recent_captures": recent_captures,
            "capture_prompts": [
                "project idea ...",
                "project blocker ...",
                "project follow up ...",
            ],
            "plain_english": "This is the current-project intelligence packet for resuming and steering work with less drift.",
            "next_action": actions[0] if actions else None,
        }

    def capture(self, kind: str, text: str, target: str | None = None) -> dict[str, Any]:
        clean_kind = (kind or "note").strip().lower().replace("-", "_").replace(" ", "_")
        clean_text = (text or "").strip()
        if not clean_text:
            return {"ok": False, "error": "Capture text is required."}

        project = self.current(target)
        if not project.get("ok"):
            return project

        existing = self._recent_captures()
        item = {
            "kind": clean_kind,
            "text": clean_text[:1000],
            "project_path": project.get("path"),
            "created_at": datetime.now(UTC).isoformat(),
        }
        updated = [item, *existing][:12]
        wrapper_state_service.update_state(
            "project",
            last_path=project.get("path"),
            last_capture_kind=clean_kind,
            last_capture_text=clean_text[:1000],
            captures=updated,
        )
        return {
            "ok": True,
            "kind": clean_kind,
            "text": clean_text[:1000],
            "project_path": project.get("path"),
            "recent_captures": updated[:6],
            "plain_english": f"Saved this {clean_kind.replace('_', ' ')} against the current project context.",
            "next_action": project.get("next_action") or "review this project",
        }

    def resume_work_packet(self, target: str | None = None) -> dict[str, Any]:
        project = self.current(target)
        if not project.get("ok"):
            return project
        return {
            "ok": True,
            "path": project.get("path"),
            "headline": "Resume work",
            "resume_packet": project.get("resume_packet") or [],
            "actions": project.get("actions") or [],
            "reentry_hint": project.get("reentry_hint"),
            "watchouts": project.get("watchouts") or [],
            "recent_captures": project.get("recent_captures") or [],
            "plain_english": "This is the current project resume pack so you can get back into the operating thread fast.",
            "next_action": (project.get("actions") or [None])[0],
        }


project_intelligence_service = ProjectIntelligenceService()
