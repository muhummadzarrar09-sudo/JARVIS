from typing import Any

from app.services.acceptance_state_service import acceptance_state_service
from app.services.maintenance_service import maintenance_service
from app.services.model_service import model_service
from app.services.runtime_stability_service import runtime_stability_service
from app.services.shell_state_service import shell_state_service
from app.services.validation_service import validation_service


class AcceptanceService:
    def _extract_blockers(self, checks: list[dict[str, Any]], deep_results: dict[str, Any], validation_blockers: list[str]) -> list[str]:
        blockers: list[str] = []
        for check in checks:
            status = check.get("status")
            if status in {"warn", "fail"}:
                blockers.append(f"{check.get('id')}: {check.get('details', {}).get('next_action') or check.get('details', {}).get('plain_english') or status}")
        for name, result in deep_results.items():
            if isinstance(result, dict):
                if not result.get("ok"):
                    blockers.append(f"{name}: {result.get('error') or result.get('next_action') or 'failed'}")
                elif result.get("warning_count"):
                    top = (result.get("warnings") or [None])[0]
                    blockers.append(f"{name}: {top or 'warnings present'}")
        for item in validation_blockers:
            blockers.append(f"validation: {item}")
        deduped = []
        for item in blockers:
            if item and item not in deduped:
                deduped.append(item)
        return deduped[:20]

    def _score(self, counts: dict[str, int]) -> float:
        total = sum(counts.values()) or 1
        weighted = (counts.get("pass", 0) * 1.0) + (counts.get("warn", 0) * 0.5)
        return round((weighted / total) * 100, 1)

    def _compare_with_previous(self, latest: dict[str, Any] | None, current_overall: str, current_blocker_count: int) -> dict[str, Any] | None:
        if not latest:
            return None
        previous_overall = latest.get("overall")
        previous_blockers = latest.get("blocker_count") or 0
        return {
            "previous_overall": previous_overall,
            "previous_blocker_count": previous_blockers,
            "overall_changed": previous_overall != current_overall,
            "blocker_delta": current_blocker_count - previous_blockers,
        }

    def _ready_for_phase_5_12(self, overall: str, blocker_count: int) -> bool:
        return overall == "pass" and blocker_count == 0

    def status(self) -> dict[str, Any]:
        latest = acceptance_state_service.latest()
        doctor = maintenance_service.doctor()
        validation = validation_service.report()
        latest_entry = latest.get("latest") or {}
        blockers = latest_entry.get("blockers") or validation.get("blockers", [])
        ready = self._ready_for_phase_5_12(latest_entry.get("overall", "warn"), len(blockers)) if latest_entry else False
        return {
            "ok": True,
            "latest": latest_entry or None,
            "history_count": latest.get("history_count", 0),
            "doctor_overall": doctor.get("overall"),
            "validation_blockers": validation.get("blockers", []),
            "blocker_count": len(blockers),
            "blockers": blockers,
            "ready_for_phase_5_12": ready,
            "plain_english": "This is the current Phase 5.11.5 acceptance status.",
            "next_action": latest_entry.get("next_action") or doctor.get("next_action") or (validation.get("next_steps") or [None])[0],
        }

    def run(self, deep: bool = False) -> dict[str, Any]:
        previous = acceptance_state_service.latest().get("latest")
        shell_bootstrap = shell_state_service.bootstrap()
        shell_doctor = shell_state_service.doctor()
        runtime_summary = runtime_stability_service.summary()
        maintenance_verify = maintenance_service.verification_summary(limit=5)
        model_fast = model_service.verify_runtime(slot="fast")
        model_main = model_service.verify_runtime(slot="main")
        validation = validation_service.report()

        checks = [
            {
                "id": "shell_bootstrap",
                "status": "pass" if shell_bootstrap.get("ok") else "fail",
                "details": shell_bootstrap,
            },
            {
                "id": "shell_doctor",
                "status": "pass" if shell_doctor.get("ok") and not shell_doctor.get("validation_blockers") else ("warn" if shell_doctor.get("ok") else "fail"),
                "details": shell_doctor,
            },
            {
                "id": "runtime_summary",
                "status": "pass" if runtime_summary.get("overall") == "pass" else "warn",
                "details": runtime_summary,
            },
            {
                "id": "maintenance_verification",
                "status": "pass" if maintenance_verify.get("overall") == "pass" else "warn",
                "details": maintenance_verify,
            },
            {
                "id": "model_fast_verify",
                "status": "pass" if model_fast.get("ok") else "warn",
                "details": model_fast,
            },
            {
                "id": "model_main_verify",
                "status": "pass" if model_main.get("ok") else "warn",
                "details": model_main,
            },
        ]

        deep_results: dict[str, Any] = {}
        if deep:
            preferred = (((runtime_summary.get("browser") or {}).get("context") or {}).get("preferred_browser"))
            deep_results["browser_validation"] = runtime_stability_service.browser_validation_matrix(
                browser_names=[preferred] if preferred else None,
                url="https://example.com",
                headless=False,
            )
            active_title = (((runtime_summary.get("desktop") or {}).get("active") or {}).get("window") or {}).get("title")
            if active_title:
                deep_results["desktop_validation"] = runtime_stability_service.desktop_focus_validation(
                    title=active_title,
                    exact=False,
                    match_index=0,
                    undo=True,
                )

        counts = {"pass": 0, "warn": 0, "fail": 0}
        for check in checks:
            counts[check["status"]] = counts.get(check["status"], 0) + 1
        overall = "pass"
        if counts.get("fail"):
            overall = "fail"
        elif counts.get("warn"):
            overall = "warn"

        blockers = self._extract_blockers(checks, deep_results, validation.get("blockers", []))
        score = self._score(counts)
        comparison = self._compare_with_previous(previous, overall, len(blockers))
        ready = self._ready_for_phase_5_12(overall, len(blockers))

        report = {
            "ok": True,
            "overall": overall,
            "deep": deep,
            "score": score,
            "counts": counts,
            "checks": checks,
            "deep_results": deep_results,
            "validation_blockers": validation.get("blockers", []),
            "blockers": blockers,
            "blocker_count": len(blockers),
            "comparison": comparison,
            "ready_for_phase_5_12": ready,
            "plain_english": "This is the Phase 5.11.5 actual-use acceptance sweep result.",
            "next_action": blockers[0] if blockers else (validation.get("next_steps") or [None])[0],
        }
        acceptance_state_service.record(report)
        return report

    def final_blockers(self) -> dict[str, Any]:
        latest = acceptance_state_service.latest().get("latest") or {}
        history = acceptance_state_service.history(limit=10).get("items", [])
        blockers = latest.get("blockers", []) if latest else []
        recurring: dict[str, int] = {}
        for item in history:
            for blocker in item.get("blockers", []) or []:
                recurring[blocker] = recurring.get(blocker, 0) + 1
        recurring_items = sorted(recurring.items(), key=lambda kv: kv[1], reverse=True)
        return {
            "ok": True,
            "latest_overall": latest.get("overall"),
            "ready_for_phase_5_12": latest.get("ready_for_phase_5_12", False),
            "blocker_count": len(blockers),
            "blockers": blockers,
            "recurring_blockers": [{"text": text, "count": count} for text, count in recurring_items[:10]],
            "plain_english": "This is the final blocker-oriented acceptance summary to feed into Phase 5.12 polish.",
            "next_action": blockers[0] if blockers else None,
        }

    def export_latest(self, output_path: str | None = None) -> dict[str, Any]:
        return acceptance_state_service.export_latest(output_path=output_path)

    def history(self, limit: int = 20) -> dict[str, Any]:
        return acceptance_state_service.history(limit=limit)

    def reset(self) -> dict[str, Any]:
        return acceptance_state_service.reset()


acceptance_service = AcceptanceService()
