from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import Request, urlopen

from bravo1.models.router import ModelRoute


@dataclass(slots=True)
class ModelClient:
    timeout_seconds: int = 8

    def generate(self, route: ModelRoute, system_prompt: str, user_prompt: str) -> dict:
        payload = {
            "model": route.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }
        req = Request(
            route.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(req, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
            data = json.loads(raw)
            content = (((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip()
            return {
                "ok": True,
                "content": content,
                "endpoint": route.endpoint,
                "model": route.model_name,
            }
        except (URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
            return {
                "ok": False,
                "endpoint": route.endpoint,
                "model": route.model_name,
                "error": str(exc),
            }
