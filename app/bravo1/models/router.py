from __future__ import annotations

from dataclasses import dataclass

from bravo1.config import Settings


@dataclass(slots=True)
class ModelRoute:
    lane: str
    model_name: str
    endpoint: str


class ModelRouter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def route(self, task_type: str) -> ModelRoute:
        if task_type in {"quick", "brief", "tool"}:
            return ModelRoute(
                lane="fast",
                model_name=self.settings.fast_model,
                endpoint=f"http://{self.settings.runtime_host}:{self.settings.runtime_fast_port}/v1/chat/completions",
            )
        return ModelRoute(
            lane="main",
            model_name=self.settings.main_model,
            endpoint=f"http://{self.settings.runtime_host}:{self.settings.runtime_main_port}/v1/chat/completions",
        )
