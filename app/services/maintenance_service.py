from typing import Any

from app.services.app_wrapper_service import app_wrapper_service
from app.services.audit import audit_service
from app.services.database_service import database_service
from app.services.model_service import model_service
from app.services.recovery_service import recovery_service


class MaintenanceService:
    def doctor(self) -> dict[str, Any]:
        from app.services.validation_service import validation_service

        validation = validation_service.report()
        database = database_service.status()
        audit = audit_service.status()
        models = model_service.status()
        browser = app_wrapper_service.wrapper_doctor("browser")
        packs = recovery_service.list_packs(limit=12)

        items = []

        db_ok = database.get("integrity_check") in {None, "ok"}
        items.append(
            {
                "id": "database_integrity",
                "label": "Database integrity",
                "status": "pass" if db_ok else "fail",
                "details": f"integrity_check={database.get('integrity_check')}",
                "evidence": {
                    "integrity_check": database.get("integrity_check"),
                    "journal_mode": database.get("journal_mode"),
                    "session_count": database.get("session_count"),
                    "message_count": database.get("message_count"),
                    "task_count": database.get("task_count"),
                },
                "next_action": None if db_ok else "Restore from a healthy backup or recovery pack.",
            }
        )

        audit_size = audit.get("size_bytes") or 0
        audit_ok = audit_size <= 5_000_000
        items.append(
            {
                "id": "audit_size",
                "label": "Audit log size",
                "status": "pass" if audit_ok else "warn",
                "details": f"size_bytes={audit_size} archive_count={audit.get('archive_count')}",
                "evidence": {
                    "size_bytes": audit_size,
                    "archive_count": audit.get("archive_count"),
                    "line_count": audit.get("line_count"),
                },
                "next_action": None if audit_ok else "Rotate or prune the audit log if it keeps growing.",
            }
        )

        provider_info = models.get("provider") or {}
        model_provider = provider_info.get("effective_provider")
        model_ok = model_provider in {"mock", "llama_cpp"}
        items.append(
            {
                "id": "model_runtime",
                "label": "Model runtime",
                "status": "pass" if model_ok else "warn",
                "details": f"effective_provider={model_provider}",
                "evidence": {
                    "effective_provider": model_provider,
                    "configured_provider": provider_info.get("configured_provider"),
                    "selected_model": provider_info.get("selected_model"),
                    "loaded_model_count": (models.get("loaded_models") or {}).get("count"),
                },
                "next_action": models.get("next_action"),
            }
        )

        browser_item = browser.get("item") or {}
        browser_ready = browser_item.get("ready", False)
        items.append(
            {
                "id": "browser_readiness",
                "label": "Browser readiness",
                "status": "pass" if browser_ready else "warn",
                "details": f"ready={browser_ready}",
                "evidence": {
                    "ready": browser_ready,
                    "playwright_installed": browser_item.get("playwright_installed"),
                    "available_browsers": browser_item.get("available_browsers"),
                },
                "next_action": "Install browser support or re-run browser validation." if not browser_ready else None,
            }
        )

        recovery_count = packs.get("count") or 0
        items.append(
            {
                "id": "recovery_packs",
                "label": "Recovery packs",
                "status": "pass" if recovery_count > 0 else "warn",
                "details": f"count={recovery_count}",
                "evidence": {"count": recovery_count, "items": packs.get("items", [])[:5]},
                "next_action": None if recovery_count > 0 else "Create a recovery pack before risky maintenance or migration work.",
            }
        )

        blockers = validation.get("blockers", [])
        items.append(
            {
                "id": "validation_blockers",
                "label": "Validation blockers",
                "status": "pass" if not blockers else "warn",
                "details": f"blocker_count={len(blockers)}",
                "evidence": {"blockers": blockers, "next_steps": validation.get("next_steps", [])[:5]},
                "next_action": None if not blockers else (validation.get("next_steps") or [None])[0],
            }
        )

        counts = {"pass": 0, "warn": 0, "fail": 0}
        for item in items:
            counts[item["status"]] = counts.get(item["status"], 0) + 1

        overall = "pass"
        if counts.get("fail"):
            overall = "fail"
        elif counts.get("warn"):
            overall = "warn"

        suggested_actions = [item.get("next_action") for item in items if item.get("next_action")]
        return {
            "ok": True,
            "overall": overall,
            "counts": counts,
            "items": items,
            "suggested_actions": suggested_actions[:8],
            "plain_english": "This is the maintenance doctor summary for the current local runtime.",
            "next_action": suggested_actions[0] if suggested_actions else None,
        }

    def history(self, limit: int = 50, event_type: str | None = None, search: str | None = None) -> dict[str, Any]:
        all_types = [
            "database_backup",
            "database_restore",
            "database_vacuum",
            "audit_rotate",
            "audit_prune",
            "session_cleanup",
            "maintenance_export_pack",
            "maintenance_import_pack",
            "maintenance_pack_preview",
            "maintenance_doctor",
        ]
        items = audit_service.recent_by_types(all_types, limit=max(limit * 4, 100))
        if event_type:
            items = [item for item in items if item.get("event_type") == event_type]
        if search:
            needle = search.lower().strip()
            filtered = []
            for item in items:
                hay = f"{item.get('event_type')} {item.get('ts')} {item.get('payload')}".lower()
                if needle in hay:
                    filtered.append(item)
            items = filtered
        items = items[-limit:]
        counts: dict[str, int] = {}
        for item in items:
            event = item.get("event_type", "unknown")
            counts[event] = counts.get(event, 0) + 1
        return {
            "ok": True,
            "count": len(items),
            "items": items,
            "event_counts": counts,
            "plain_english": "This is the filtered maintenance operation history.",
        }


maintenance_service = MaintenanceService()
