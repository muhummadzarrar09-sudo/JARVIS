from pathlib import Path
from typing import Any


class LlamaManager:
    def __init__(self) -> None:
        self._models: dict[str, Any] = {}

    def get_or_load(self, model_path: Path):
        key = str(model_path.resolve())
        if key in self._models:
            return self._models[key]

        from llama_cpp import Llama  # type: ignore

        llm = Llama(
            model_path=key,
            n_ctx=4096,
            verbose=False,
        )
        self._models[key] = llm
        return llm

    def generate(
        self,
        model_path: Path,
        system_prompt: str,
        context_messages: list[dict[str, str]],
        user_message: str,
        max_tokens: int = 384,
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

        output = llm(prompt, max_tokens=max_tokens, stop=["User:"])
        return output["choices"][0]["text"].strip()


llama_manager = LlamaManager()
