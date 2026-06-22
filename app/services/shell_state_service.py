from typing import Any

from app.services.app_wrapper_service import app_wrapper_service
from app.services.audit import audit_service
from app.services.memory import memory_service
from app.services.progress_service import progress_service
from app.services.quick_actions_service import quick_actions_service
from app.services.task_service import task_service
from app.services.validation_service import validation_service


class ShellStateService:
    def snapshot(self, session_id: str | None = None) -> dict[str, Any]:
        resolved_session_id = session_id
        if resolved_session_id and not memory_service.session_overview(resolved_session_id).get("ok"):
            resolved_session_id = memory_service.resolve_session_id(resolved_session_id)

        if resolved_session_id:
            session = memory_service.session_overview(resolved_session_id)
        else:
            sessions = memory_service.list_sessions(limit=1)
            resolved_session_id = sessions[0]["session_id"] if sessions else None
            session = memory_service.session_overview(resolved_session_id) if resolved_session_id else {"ok": False}

        return {
            "ok": True,
            "session_id": resolved_session_id,
            "today": quick_actions_service.today_brief(),
            "progress": quick_actions_service.progress(),
            "setup": quick_actions_service.setup_summary(),
            "focus": quick_actions_service.focus(),
            "project": app_wrapper_service.current_project_context(None),
            "browser": app_wrapper_service.current_browser_context(),
            "wrapper_doctor": app_wrapper_service.wrapper_doctor(),
            "tasks": {
                "summary": task_service.task_summary(),
                "next": task_service.next_task(),
                "current": task_service.current_task(),
                "items": task_service.list_tasks(status=None, limit=12),
            },
            "sessions": {
                "current": session,
                "items": memory_service.list_sessions(limit=10),
            },
            "audit": {
                "timeline": audit_service.timeline(session_id=resolved_session_id, limit=12),
                "replay": audit_service.replay_candidates(session_id=resolved_session_id, limit=10),
                "operator_summary": audit_service.operator_summary(session_id=resolved_session_id),
            },
            "phase4": progress_service.phase4_status(),
            "phase5": progress_service.phase5_status(),
            "validation": validation_service.report(),
        }


shell_state_service = ShellStateService()
