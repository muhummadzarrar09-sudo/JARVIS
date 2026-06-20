from pathlib import Path

from app.core.config import settings
from app.services.llama_manager import llama_manager


class LLMRouter:
    """
    Phase-1 router.

    Supports:
    - mock provider for bootstrapping
    - llama_cpp provider for real local GGUF inference
    """

    def _pick_model_name(self, prompt: str) -> str:
        prompt_l = prompt.lower()
        if any(word in prompt_l for word in ["plan", "architect", "design", "strategy", "analyze"]):
            return settings.default_main_model
        return settings.default_fast_model

    def _model_path(self, model_name: str) -> Path:
        return settings.model_dir / model_name

    def _system_prompt(self) -> str:
        return (
            "You are JARVIS, a precise local AI assistant running on the user's laptop. "
            "Be concise, useful, and operational. When tool output is provided in context, "
            "use it directly and do not invent results."
        )

    def _normalized_provider(self) -> str:
        raw = (settings.default_model_provider or "mock").strip().lower()
        normalized = raw.replace("-", "_").replace(".", "_")
        aliases = {
            "mock": "mock",
            "none": "mock",
            "llama_cpp": "llama_cpp",
            "llamacpp": "llama_cpp",
        }
        return aliases.get(normalized, normalized)

    def generate_reply(self, prompt: str, context: list[dict]) -> tuple[str, str]:
        model_name = self._pick_model_name(prompt)
        model_path = self._model_path(model_name)
        provider = self._normalized_provider()

        if provider == "mock":
            summary = " | ".join([f"{m['role']}: {m['content'][:80]}" for m in context[-4:]]) or "no prior context"
            reply = (
                f"[MOCK JARVIS REPLY via {model_name}]\n"
                f"You said: {prompt}\n"
                f"Context seen: {summary}\n"
                f"Next step: switch DEFAULT_MODEL_PROVIDER=llama_cpp once models are ready."
            )
            return reply, model_name

        if provider == "llama_cpp":
            if not model_path.exists():
                return (
                    f"Model file not found: {model_path}. Update .env or run bootstrap/model download first.",
                    model_name,
                )
            try:
                text = llama_manager.generate(
                    model_path=model_path,
                    system_prompt=self._system_prompt(),
                    context_messages=context,
                    user_message=prompt,
                    max_tokens=384,
                )
                return text or "The model returned an empty reply.", model_name
            except ImportError:
                return (
                    "llama-cpp-python is not installed correctly yet. Rebuild with Python 3.11 or use mock mode first.",
                    model_name,
                )
            except Exception as e:
                return (f"llama.cpp inference error: {e}", model_name)

        expected = "mock or llama_cpp"
        actual = settings.default_model_provider
        return (f"Unknown model provider configured: `{actual}`. Expected one of: {expected}.", model_name)


llm_router = LLMRouter()
