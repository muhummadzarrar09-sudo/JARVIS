from pathlib import Path

from app.core.config import settings
from app.services.llama_manager import llama_manager
from app.services.model_service import model_service


class LLMRouter:
    """
    Phase-1 router.

    Supports:
    - mock provider for bootstrapping
    - llama_cpp provider for real local GGUF inference
    - auto provider that uses local GGUFs when ready and falls back to mock
    """

    def _system_prompt(self) -> str:
        return (
            "You are JARVIS, a precise local AI assistant running on the user's laptop. "
            "Be concise, useful, and operational. When tool output is provided in context, "
            "use it directly and do not invent results."
        )

    def _mock_reply(self, prompt: str, context: list[dict], model_name: str, note: str | None = None) -> tuple[str, str]:
        summary = " | ".join([f"{m['role']}: {m['content'][:80]}" for m in context[-4:]]) or "no prior context"
        extra = f"\nMode note: {note}" if note else ""
        reply = (
            f"[MOCK JARVIS REPLY via {model_name}]\n"
            f"You said: {prompt}\n"
            f"Context seen: {summary}{extra}"
        )
        return reply, model_name

    def generate_reply(self, prompt: str, context: list[dict]) -> tuple[str, str]:
        provider_state = model_service.effective_provider()
        configured_provider = provider_state.get("configured_provider")
        effective_provider = provider_state.get("effective_provider")
        selection = model_service.resolve_model_choice(prompt)
        selected = selection.get("selected") or {}
        model_name = selected.get("name") or selection.get("configured_name") or settings.default_fast_model
        model_path = Path(selected.get("path")) if selected.get("path") else None

        if effective_provider == "mock":
            note = None
            if configured_provider == "auto":
                note = provider_state.get("reason")
            return self._mock_reply(prompt, context, model_name, note=note)

        if effective_provider == "llama_cpp":
            if not model_path or not model_path.exists():
                return (
                    f"Model file not found: {model_path}. Update .env, configure local models, or run model download first.",
                    model_name,
                )
            try:
                text = llama_manager.generate(
                    model_path=model_path,
                    system_prompt=self._system_prompt(),
                    context_messages=context,
                    user_message=prompt,
                    max_tokens=settings.llama_max_tokens,
                )
                return text or "The model returned an empty reply.", model_name
            except ImportError:
                return (
                    "llama-cpp-python is not installed correctly yet. Rebuild with Python 3.11 or switch to mock mode first.",
                    model_name,
                )
            except Exception as e:
                return (f"llama.cpp inference error: {e}", model_name)

        expected = "mock, auto, or llama_cpp"
        actual = settings.default_model_provider
        return (f"Unknown model provider configured: `{actual}`. Expected one of: {expected}.", model_name)


llm_router = LLMRouter()
