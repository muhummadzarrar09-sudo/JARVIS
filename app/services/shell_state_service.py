from datetime import UTC, datetime
from time import perf_counter
from typing import Any

from app.services.app_wrapper_service import app_wrapper_service
from app.services.audit import audit_service
from app.services.database_service import database_service
from app.services.memory import memory_service
from app.services.model_service import model_service
from app.services.progress_service import progress_service
from app.services.recovery_service import recovery_service
from app.services.runtime_stability_service import runtime_stability_service
from app.services.maintenance_service import maintenance_service
from app.services.maintenance_settings_service import maintenance_settings_service
from app.services.project_intelligence_service import project_intelligence_service
from app.services.quick_actions_service import quick_actions_service
from app.services.task_service import task_service
from app.services.trusted_root_service import trusted_root_service
from app.services.validation_service import validation_service
from app.services.wrapper_state_service import wrapper_state_service


class ShellStateService:
    def bootstrap(self) -> dict[str, Any]:
        hygiene = wrapper_state_service.sanitize_all()
        models = model_service.status()
        doctor = maintenance_service.doctor()
        return {
            "ok": True,
            "app_name": "JARVIS Shell",
            "state_hygiene": hygiene,
            "models": {
                "provider": (models.get("provider") or {}).get("effective_provider"),
                "selected_model": ((models.get("provider") or {}).get("selected_model") or {}).get("name"),
                "loaded_count": (models.get("loaded_models") or {}).get("count", 0),
            },
            "maintenance_doctor": {
                "overall": doctor.get("overall"),
                "counts": doctor.get("counts"),
                "next_action": doctor.get("next_action"),
            },
            "plain_english": "This is the shell bootstrap payload used to verify state hygiene and runtime readiness before the full shell snapshot loads.",
            "next_action": doctor.get("next_action") or models.get("next_action"),
        }

    def doctor(self) -> dict[str, Any]:
        hygiene = wrapper_state_service.hygiene_report()
        validation = validation_service.report()
        models = model_service.status()
        database = database_service.status()
        return {
            "ok": True,
            "state_hygiene": hygiene,
            "validation_blockers": validation.get("blockers", []),
            "model_provider": (models.get("provider") or {}).get("effective_provider"),
            "selected_model": ((models.get("provider") or {}).get("selected_model") or {}).get("name"),
            "database_integrity": database.get("integrity_check"),
            "plain_english": "This is the shell doctor report for shell boot reliability and state correctness.",
            "next_action": validation.get("next_steps", [None])[0],
        }

    def snapshot(self, session_id: str | None = None) -> dict[str, Any]:
        started_at = perf_counter()
        generated_at = datetime.now(UTC).isoformat()
        wrapper_state_service.sanitize_all()
        resolved_session_id = session_id
        if resolved_session_id and not memory_service.session_overview(resolved_session_id).get("ok"):
            resolved_session_id = memory_service.resolve_session_id(resolved_session_id)

        if resolved_session_id:
            session = memory_service.session_overview(resolved_session_id)
        else:
            sessions = memory_service.list_sessions(limit=1)
            resolved_session_id = sessions[0]["session_id"] if sessions else None
            session = memory_service.session_overview(resolved_session_id) if resolved_session_id else {"ok": False}

        models_status = model_service.status()
        database_status = database_service.status()
        audit_status = audit_service.status()
        audit_archives = audit_service.list_archives(limit=12)
        database_backups = database_service.list_backups(limit=12)
        database_history = audit_service.recent_by_types(["database_backup", "database_restore", "database_vacuum"], limit=12)
        audit_history = audit_service.recent_by_types(["audit_rotate", "audit_prune", "audit_archive_delete"], limit=12)
        session_history = audit_service.recent_by_types(["session_cleanup"], limit=12)
        recovery_history = audit_service.recent_by_types(["maintenance_export_pack", "maintenance_import_pack", "maintenance_pack_preview", "maintenance_pack_delete"], limit=12)
        maintenance_history_preview = maintenance_service.history(limit=30)

        duration_ms = round((perf_counter() - started_at) * 1000, 1)
        return {
            "ok": True,
            "generated_at": generated_at,
            "duration_ms": duration_ms,
            "session_id": resolved_session_id,
            "brief": quick_actions_service.executive_brief(),
            "today": quick_actions_service.today_brief(),
            "progress": quick_actions_service.progress(),
            "setup": quick_actions_service.setup_summary(),
            "focus": quick_actions_service.focus(),
            "project": app_wrapper_service.current_project_context(None),
            "project_intelligence": project_intelligence_service.current(None),
            "browser": app_wrapper_service.current_browser_context(),
            "trusted_roots": trusted_root_service.summary(),
            "runtime": runtime_stability_service.summary(),
            "models": models_status,
            "database": database_status,
            "shell": {
                "bootstrap": self.bootstrap(),
                "doctor": self.doctor(),
            },
            "maintenance": {
                "database_backups": database_backups,
                "doctor": maintenance_service.doctor(),
                "verification": maintenance_service.verification_summary(limit=5),
                "settings": maintenance_settings_service.get_settings(),
                "history_preview": maintenance_history_preview,
                "database_history": database_history,
                "recovery_packs": recovery_service.list_packs(limit=12),
                "recovery_history": recovery_history,
                "audit_status": audit_status,
                "audit_archives": audit_archives,
                "audit_history": audit_history,
                "session_history": session_history,
                "summary": {
                    "database_backup_count": database_status.get("backup_count"),
                    "audit_archive_count": audit_status.get("archive_count"),
                    "latest_database_event": database_history[-1] if database_history else None,
                    "latest_audit_event": audit_history[-1] if audit_history else None,
                    "latest_session_event": session_history[-1] if session_history else None,
                    "latest_recovery_event": recovery_history[-1] if recovery_history else None,
                },
            },
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
