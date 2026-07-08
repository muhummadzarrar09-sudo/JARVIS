from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WindowsAdapter:
    provider: str = "uia-skeleton"

    def status(self) -> dict:
        return {
            "ok": True,
            "provider": self.provider,
            "mode": "skeleton",
            "plain_english": "Windows adapter skeleton is in place for the future UIA-first desktop operator.",
            "next_action": "Wire UIA enumeration and action primitives in the next Windows-control build pass.",
        }

    def inspect(self) -> dict:
        return {
            "ok": True,
            "provider": self.provider,
            "planned_capabilities": [
                "enumerate active windows",
                "inspect UIA element tree",
                "focus/switch apps",
                "click/type/scroll via structured desktop actions",
            ],
            "plain_english": "This is the Week-1 Windows adapter skeleton. It preserves architecture intent while keeping the current rebuild lean.",
        }
