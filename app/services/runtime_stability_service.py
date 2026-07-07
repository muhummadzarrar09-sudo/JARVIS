from typing import Any

from app.services.app_wrapper_service import app_wrapper_service
from app.services.browser_tool import browser_tool
from app.services.desktop_tool import desktop_tool


class RuntimeStabilityService:
    def browser_summary(self) -> dict[str, Any]:
        available = browser_tool.available_browsers()
        context = app_wrapper_service.current_browser_context()
        doctor = app_wrapper_service.wrapper_doctor("browser")

        warnings: list[str] = []
        item = doctor.get("item") or {}
        if not item.get("external_ready") and not item.get("managed_ready"):
            warnings.append("Neither external browser launch nor controlled browser mode is ready.")
        if not (available.get("count") or 0):
            warnings.append("No browser candidates were detected.")
        if context.get("preferred_browser") == "playwright_chromium" and not item.get("managed_ready"):
            warnings.append("Browser preference points at Playwright Chromium, but controlled mode is not ready.")

        candidate_count = available.get("count") or 0
        installed_count = len([x for x in available.get("items", []) if x.get("executable_path")])
        overall = "pass" if not warnings else "warn"
        return {
            "ok": True,
            "overall": overall,
            "candidate_count": candidate_count,
            "installed_count": installed_count,
            "available": available,
            "context": context,
            "doctor": doctor,
            "warnings": warnings,
            "plain_english": "This is the live browser-runtime stability summary with external-browser-first behavior.",
            "next_action": context.get("next_action") or (warnings[0] if warnings else None),
        }

    def browser_validation_matrix(
        self,
        browser_names: list[str] | None = None,
        url: str | None = None,
        headless: bool | None = None,
        mode: str | None = None,
    ) -> dict[str, Any]:
        selected_mode = (mode or "external").strip().lower()
        if selected_mode in {"managed", "controlled", "playwright", "playwright_managed"}:
            return browser_tool.validate_candidates(browser_names=browser_names, url=url, headless=headless)
        return browser_tool.validate_external_candidates(browser_names=browser_names, url=url)

    def desktop_summary(self) -> dict[str, Any]:
        active = desktop_tool.active_window()
        windows = desktop_tool.list_windows()
        safety = desktop_tool.safety_status()

        warnings: list[str] = []
        if not active.get("ok"):
            warnings.append("Active-window lookup is failing.")
        if not windows.get("ok"):
            warnings.append("Desktop window listing is failing.")
        if not safety.get("undo_focus_supported"):
            warnings.append("Undo focus is not available.")
        if windows.get("ok") and (windows.get("count") or 0) == 0:
            warnings.append("No titled desktop windows were detected.")

        overall = "pass" if not warnings else "warn"
        return {
            "ok": True,
            "overall": overall,
            "active": active,
            "windows": windows,
            "safety": safety,
            "warnings": warnings,
            "plain_english": "This is the live desktop-runtime stability summary.",
            "next_action": warnings[0] if warnings else None,
        }

    def desktop_focus_validation(
        self,
        title: str,
        exact: bool = False,
        match_index: int = 0,
        undo: bool = True,
    ) -> dict[str, Any]:
        return desktop_tool.validate_focus_flow(title=title, exact=exact, match_index=match_index, undo=undo)

    def summary(self) -> dict[str, Any]:
        browser = self.browser_summary()
        desktop = self.desktop_summary()
        warnings = [*browser.get("warnings", []), *desktop.get("warnings", [])]
        overall = "pass" if not warnings else "warn"
        return {
            "ok": True,
            "overall": overall,
            "browser": browser,
            "desktop": desktop,
            "warning_count": len(warnings),
            "warnings": warnings,
            "plain_english": "This is the combined browser + desktop runtime stability summary.",
            "next_action": warnings[0] if warnings else None,
        }


runtime_stability_service = RuntimeStabilityService()
