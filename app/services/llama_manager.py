import os
from pathlib import Path
from typing import Any

from app.core.config import settings


class LlamaManager:
    def __init__(self) -> None:
        self._models: dict[str, Any] = {}

    def _threads(self) -> int | None:
        if settings.llama_n_threads and settings.llama_n_threads > 0:
            return settings.llama_n_threads
        cpu = os.cpu_count() or 4
        return max(1, cpu - 1)

    def _cache_key(self, model_path: Path) -> str:
        resolved = str(model_path.resolve())
        return f"{resolved}::ctx={settings.llama_n_ctx}::gpu={settings.llama_n_gpu_layers}::threads={self._threads()}"

    def get_or_load(self, model_path: Path):
        key = self._cache_key(model_path)
        if key in self._models:
            return self._models[key]

        from llama_cpp import Llama  # type: ignore

        kwargs: dict[str, Any] = {
            "model_path": str(model_path.resolve()),
            "n_ctx": settings.llama_n_ctx,
            "verbose": False,
        }
        threads = self._threads()
        if threads:
            kwargs["n_threads"] = threads
        if settings.llama_n_gpu_layers:
            kwargs["n_gpu_layers"] = settings.llama_n_gpu_layers

        llm = Llama(**kwargs)
        self._models[key] = llm
        return llm

    def preload(self, model_path: Path) -> dict[str, Any]:
        llm = self.get_or_load(model_path)
        return {
            "ok": True,
            "model_path": str(model_path.resolve()),
            "cache_key": self._cache_key(model_path),
            "loaded": llm is not None,
            "plain_english": "JARVIS warmed the local GGUF model into memory for faster first replies.",
        }

    def unload_all(self) -> dict[str, Any]:
        count = len(self._models)
        self._models = {}
        return {
            "ok": True,
            "unloaded_count": count,
            "plain_english": "JARVIS cleared the in-process local model cache.",
        }

    def loaded_models(self) -> dict[str, Any]:
        return {
            "ok": True,
            "count": len(self._models),
            "items": sorted(self._models.keys()),
        }

    def generate(
        self,
        model_path: Path,
        system_prompt: str,
        context_messages: list[dict[str, str]],
        user_message: str,
        max_tokens: int | None = None,
    ) -> str:
        llm = self.get_or_load(model_path)
        convo_lines = [system_prompt.strip(), ""]
        for item in context_messages[-8:]:
            role = item.get("role", "user").capitalize()
            content = item.get("content", "")
            convo_lines.append(f"{role}: {content}")
        convo_lines.append(f"User: {user_message}")
        convo_lines.append("Assistant:")
        prompt = "\n".join(convo_lines)

        output = llm(prompt, max_tokens=max_tokens or settings.llama_max_tokens, stop=["User:"])
        return output["choices"][0]["text"].strip()


llama_manager = LlamaManager()
