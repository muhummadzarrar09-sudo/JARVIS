from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class BrowserAdapter:
    provider: str = "playwright-dom"

    def status(self) -> dict:
        return {
            "ok": True,
            "provider": self.provider,
            "mode": "skeleton",
            "plain_english": "Browser adapter skeleton is in place for the future DOM-first browser operator.",
            "next_action": "Wire Playwright session management and DOM extraction in the next browser build pass.",
        }

    def inspect(self) -> dict:
        return {
            "ok": True,
            "provider": self.provider,
            "planned_capabilities": [
                "launch real browser session",
                "persist browser profile/session",
                "extract DOM/actionable element context",
                "navigate/click/type via element references",
            ],
            "plain_english": "This is the Week-1 browser adapter skeleton. It documents the target shape without locking us into a heavy implementation too early.",
        }
