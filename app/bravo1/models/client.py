from __future__ import annotations

import json
from dataclasses import dataclass
from time import perf_counter
from urllib.error import URLError
from urllib.request import Request, urlopen

from bravo1.models.router import ModelRoute


@dataclass(slots=True)
class ModelClient:
    timeout_seconds: int = 8
    retry_count: int = 2

    def _extract_content(self, data: dict) -> str:
        choices = data.get("choices") or []
        if choices:
            message = (choices[0].get("message") or {}).get("content")
            if isinstance(message, str) and message.strip():
                return message.strip()
            text = choices[0].get("text")
            if isinstance(text, str) and text.strip():
                return text.strip()
        for key in ("response", "generated_text", "content"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

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
        last_error = "unreachable"
        for attempt in range(1, self.retry_count + 1):
            started = perf_counter()
            try:
                with urlopen(req, timeout=self.timeout_seconds) as response:
                    raw = response.read().decode("utf-8")
                data = json.loads(raw)
                content = self._extract_content(data)
                if content:
                    return {
                        "ok": True,
                        "content": content,
                        "endpoint": route.endpoint,
                        "model": route.model_name,
                        "attempt": attempt,
                        "latency_ms": round((perf_counter() - started) * 1000, 1),
                    }
                last_error = "Model returned an empty response payload."
            except (URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
                last_error = str(exc)
        return {
            "ok": False,
            "endpoint": route.endpoint,
            "model": route.model_name,
            "error": last_error,
            "attempt": self.retry_count,
        }
