from typing import Any

from app.services.app_wrapper_service import app_wrapper_service
from app.services.memory import memory_service
from app.services.project_intelligence_service import project_intelligence_service
from app.services.task_service import task_service


class ExecutiveBriefService:
    def _dedupe(self, items: list[str | None], limit: int | None = None) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for item in items:
            cleaned = (item or "").strip()
            if not cleaned or cleaned in seen:
                continue
            seen.add(cleaned)
            result.append(cleaned)
            if limit is not None and len(result) >= limit:
                break
        return result

    def _blockers(self) -> list[dict[str, Any]]:
        doctor = app_wrapper_service.wrapper_doctor()
        blockers: list[dict[str, Any]] = []
        for item in doctor.get("items", []):
            if item.get("ready"):
                continue
            blockers.append(
                {
                    "name": item.get("name"),
                    "notes": item.get("notes"),
                }
            )
        return blockers[:4]

    def _signals(
        self,
        task_summary: dict[str, Any],
        project: dict[str, Any],
        browser: dict[str, Any],
        blockers: list[dict[str, Any]],
        sessions: list[dict[str, Any]],
    ) -> list[str]:
        signals: list[str] = []
        if task_summary.get("in_progress"):
            signals.append(f"{task_summary.get('in_progress')} active")
        elif task_summary.get("open"):
            signals.append(f"{task_summary.get('open')} queued")
        if project.get("ok") and project.get("path"):
            signals.append("project ready")
        if browser.get("remembered_url"):
            signals.append("browser thread remembered")
        if blockers:
            count = len(blockers)
            signals.append(f"{count} blocker{'s' if count != 1 else ''}")
        if sessions:
            signals.append("recent history available")
        return signals

    def _confidence_label(self, score: int) -> str:
        if score >= 92:
            return "very high"
        if score >= 82:
            return "high"
        if score >= 70:
            return "medium"
        return "low"

    def _project_reentry_hint(self, project: dict[str, Any]) -> str | None:
        if not project.get("ok"):
            return None
        summary = project.get("summary") or {}
        path = project.get("path") or summary.get("path")
        project_types = summary.get("project_type") or []
        label = ", ".join(project_types[:2]) if isinstance(project_types, list) and project_types else "project"
        if path:
            return f"Project context is ready at {path} ({label})."
        return None

    def _browser_reentry_hint(self, browser: dict[str, Any]) -> str | None:
        remembered = browser.get("remembered_url")
        if remembered:
            return f"JARVIS remembers this browser thread: {remembered}"
        return None

    def _session_reentry_hint(self, sessions: list[dict[str, Any]]) -> str | None:
        if not sessions:
            return None
        title = sessions[0].get("title") or "recent session"
        return f"Recent thread: {title}"

    def _action_candidates(
        self,
        project: dict[str, Any],
        browser: dict[str, Any],
        current_task: dict[str, Any],
        next_task: dict[str, Any],
        blockers: list[dict[str, Any]],
        sessions: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        summary = project.get("summary") or {}
        candidates: list[dict[str, Any]] = []

        def add(action: str | None, score: int, why: str, mode: str, source: str) -> None:
            cleaned = (action or "").strip()
            if not cleaned:
                return
            candidates.append(
                {
                    "action": cleaned,
                    "score": score,
                    "why": why,
                    "mode": mode,
                    "source": source,
                }
            )

        if current_task.get("ok"):
            add(
                "continue coding" if project.get("ok") else "what am i doing now",
                98,
                "You already have active work in motion, so the best move is to continue the live thread.",
                "continue",
                "current_task",
            )
            add(
                "show my tasks",
                88,
                "Your task board can keep the active thread visible without changing focus.",
                "continue",
                "current_task",
            )
            add(
                "complete current task",
                80,
                "If the current task is basically done, wrap it cleanly and move on.",
                "close_loop",
                "current_task",
            )
        elif next_task.get("ok"):
            add(
                "work on next task",
                93,
                "A concrete next task already exists, so the fastest win is to start moving on it.",
                "execute",
                "next_task",
            )
            add(
                "show my tasks",
                84,
                "Your task board is the cleanest place to confirm the queue before acting.",
                "plan",
                "next_task",
            )
            add(
                "continue coding" if project.get("ok") else None,
                81,
                "The task queue exists and your project context is ready, so you can drop back into execution fast.",
                "execute",
                "next_task_project",
            )
        elif project.get("ok"):
            add(
                "review this project" if summary.get("readme") else "show my project",
                86,
                "A real project context is available, so re-entering it cleanly is better than starting from scratch.",
                "resume_project",
                "project",
            )
            add(
                "open readme" if summary.get("readme") else None,
                82,
                "A README is available, which is the fastest low-noise way to recover context.",
                "resume_project",
                "project_readme",
            )
            add(
                "open code here",
                78,
                "The project is ready, so opening code is a direct path back into execution.",
                "execute",
                "project_code",
            )
            add(
                "open terminal here",
                76,
                "Terminal context is often the quickest bridge back into the working thread.",
                "execute",
                "project_terminal",
            )
        elif browser.get("remembered_url"):
            add(
                "open browser",
                78,
                "A remembered browser thread exists, so reopening it is the fastest context recovery path.",
                "resume_browser",
                "browser",
            )
            add(
                "show me the current page",
                72,
                "If you want context before action, review the remembered page in controlled mode.",
                "review",
                "browser",
            )
            add(
                "research this",
                67,
                "If the browser thread needs deeper review, move into controlled research mode.",
                "review",
                "browser",
            )

        if blockers:
            add(
                "show my setup blockers",
                74 if not (current_task.get("ok") or next_task.get("ok") or project.get("ok")) else 58,
                "A few blockers exist, so keeping them visible may save you from hidden friction later.",
                "unstick",
                "blockers",
            )

        if sessions:
            add(
                "show me recent work",
                68 if not (current_task.get("ok") or next_task.get("ok") or project.get("ok")) else 54,
                "Recent sessions can rebuild momentum when there is no stronger active thread.",
                "resume_session",
                "sessions",
            )
            add(
                "resume project" if project.get("ok") else None,
                60,
                "If you want to use remembered project continuity directly, resume the broader project thread.",
                "resume_session",
                "sessions",
            )

        if not candidates:
            add(
                "start my workday",
                60,
                "No strong active thread was found, so a clean startup flow is the best reset move.",
                "reset",
                "fallback",
            )
            add(
                "show me today",
                58,
                "If you want a calm snapshot first, the day brief is the cleanest overview.",
                "reset",
                "fallback",
            )

        add(
            "open browser" if browser.get("preferred_browser") or browser.get("remembered_url") else None,
            50,
            "The browser can be reopened quickly if you want to pivot into the web thread.",
            "support",
            "browser_support",
        )
        add(
            "show my progress",
            46,
            "A progress snapshot is useful if you want orientation without committing yet.",
            "support",
            "progress",
        )

        candidates.sort(key=lambda item: item.get("score", 0), reverse=True)
        deduped: list[dict[str, Any]] = []
        seen: set[str] = set()
        for item in candidates:
            action = item.get("action")
            if action in seen:
                continue
            seen.add(action)
            deduped.append(item)
        return deduped

    def next_steps(self) -> dict[str, Any]:
        project = project_intelligence_service.current(None)
        current_task = task_service.current_task()
        next_task = task_service.next_task()
        browser = app_wrapper_service.current_browser_context()
        sessions = memory_service.list_sessions(limit=2)
        blockers = self._blockers()
        candidates = self._action_candidates(project, browser, current_task, next_task, blockers, sessions)
        items = [item.get("action") for item in candidates[:6] if item.get("action")]
        return {
            "ok": True,
            "items": items,
            "candidates": candidates[:6],
            "plain_english": "These are the most grounded next actions based on your current local context.",
            "next_action": items[0] if items else None,
        }

    def build(self) -> dict[str, Any]:
        project = project_intelligence_service.current(None)
        browser = app_wrapper_service.current_browser_context()
        current_task = task_service.current_task()
        next_task = task_service.next_task()
        task_summary = task_service.task_summary()
        sessions = memory_service.list_sessions(limit=3)
        blockers = self._blockers()
        candidates = self._action_candidates(project, browser, current_task, next_task, blockers, sessions)

        primary = candidates[0] if candidates else {
            "action": "start my workday",
            "score": 60,
            "why": "No strong active thread was found, so a clean startup flow is the best reset move.",
            "mode": "reset",
            "source": "fallback",
        }
        primary_action = primary.get("action") or "start my workday"
        signals = self._signals(task_summary, project, browser, blockers, sessions)
        startup_subtitle = " • ".join(signals[:3]) if signals else "Chat first. Low noise. Context when needed."

        headline = "Do this now"
        if current_task.get("ok"):
            headline = f"Stay on: {current_task.get('title')}"
        elif next_task.get("ok"):
            headline = f"Queue up: {next_task.get('title')}"
        elif primary.get("mode") == "resume_project":
            headline = "Re-enter the project cleanly"
        elif primary.get("mode") == "resume_browser":
            headline = "Pick up the browser thread"
        elif primary.get("mode") == "unstick":
            headline = "Clear the friction first"
        elif primary.get("mode") == "resume_session":
            headline = "Resume your last operating thread"

        project_reentry = project.get("reentry_hint") or self._project_reentry_hint(project)
        browser_reentry = self._browser_reentry_hint(browser)
        session_reentry = self._session_reentry_hint(sessions)
        reentry_hint = project_reentry or browser_reentry or session_reentry

        watchouts = list(project.get("watchouts") or []) or [
            f"{item.get('name')}: {item.get('notes')}"
            for item in blockers
            if item.get("name") and item.get("notes")
        ][:3]

        secondary_candidates = candidates[1:4]
        secondary_actions = [item.get("action") for item in secondary_candidates if item.get("action")]

        return {
            "ok": True,
            "headline": headline,
            "primary_action": primary_action,
            "why": primary.get("why"),
            "startup_subtitle": startup_subtitle,
            "secondary_actions": secondary_actions,
            "secondary_candidates": secondary_candidates,
            "operating_mode": primary.get("mode") or "reset",
            "confidence": min(0.99, max(0.4, (primary.get("score", 60) / 100))),
            "confidence_label": self._confidence_label(primary.get("score", 60)),
            "lane_hint": "mixed personal + business",
            "signals": signals,
            "reentry_hint": reentry_hint,
            "watchouts": watchouts,
            "decision_log": candidates[:5],
            "task_summary": task_summary,
            "current_task": current_task if current_task.get("ok") else None,
            "next_task": next_task if next_task.get("ok") else None,
            "project_path": project.get("path") if project.get("ok") else None,
            "project_type": (project.get("summary") or {}).get("project_type") if project.get("ok") else None,
            "remembered_browser": browser.get("remembered_url"),
            "recent_sessions": sessions,
            "blockers": blockers,
            "plain_english": "This is the short executive brief for what matters next without adding noise.",
            "next_action": primary_action,
        }


executive_brief_service = ExecutiveBriefService()
