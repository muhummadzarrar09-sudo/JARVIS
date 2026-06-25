import importlib.util
import re
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services.llama_manager import llama_manager


class ModelService:
    def _workspace_root(self) -> Path:
        return Path(settings.workspace_root).resolve()

    def _model_dir(self) -> Path:
        raw = Path(settings.model_dir)
        if raw.is_absolute():
            return raw.resolve()
        return (self._workspace_root() / raw).resolve()

    def _env_path(self) -> Path:
        return self._workspace_root() / ".env"

    def _normalize_provider(self, raw: str | None = None) -> str:
        value = (raw or settings.default_model_provider or "mock").strip().lower()
        value = value.replace("-", "_").replace(".", "_")
        aliases = {
            "": "auto",
            "none": "mock",
            "mock": "mock",
            "auto": "auto",
            "local": "auto",
            "gguf": "auto",
            "llama_cpp": "llama_cpp",
            "llamacpp": "llama_cpp",
        }
        return aliases.get(value, value)

    def _gguf_items(self) -> list[dict[str, Any]]:
        model_dir = self._model_dir()
        if not model_dir.exists():
            return []

        items: list[dict[str, Any]] = []
        for path in sorted(model_dir.rglob("*.gguf")):
            if not path.is_file():
                continue
            try:
                relative = str(path.resolve().relative_to(self._workspace_root()))
            except Exception:
                relative = str(path)
            size_bytes = path.stat().st_size
            lower = path.name.lower()
            param_match = re.search(r"(\d+(?:\.\d+)?)b", lower)
            quant_match = re.search(r"q\d[^._\s-]*", lower)
            items.append(
                {
                    "name": path.name,
                    "path": str(path.resolve()),
                    "relative_path": relative,
                    "size_bytes": size_bytes,
                    "size_gb": round(size_bytes / (1024 ** 3), 3),
                    "family": self._family_from_name(path.name),
                    "param_b": float(param_match.group(1)) if param_match else None,
                    "quant": quant_match.group(0).upper() if quant_match else None,
                    "instruct": "instruct" in lower or "chat" in lower,
                }
            )
        return items

    def _family_from_name(self, name: str) -> str:
        lower = name.lower()
        for family in ("qwen", "llama", "mistral", "phi", "gemma", "deepseek", "yi"):
            if family in lower:
                return family
        return "unknown"

    def _score_fast(self, item: dict[str, Any]) -> tuple:
        param = item.get("param_b")
        size = item.get("size_bytes") or 0
        quant = item.get("quant") or ""
        instruct = 1 if item.get("instruct") else 0
        has_param = 0 if param is None else 1
        return (
            instruct,
            has_param,
            -(param or 999.0),
            1 if "Q4" in quant else 0,
            -size,
        )

    def _score_main(self, item: dict[str, Any]) -> tuple:
        param = item.get("param_b")
        size = item.get("size_bytes") or 0
        quant = item.get("quant") or ""
        instruct = 1 if item.get("instruct") else 0
        has_param = 0 if param is None else 1
        return (
            instruct,
            has_param,
            (param or 0.0),
            1 if "Q4" in quant else 0,
            size,
        )

    def discover_models(self) -> dict[str, Any]:
        items = self._gguf_items()
        fast = None
        main = None
        if items:
            fast = max(items, key=self._score_fast)
            main = max(items, key=self._score_main)
        return {
            "ok": True,
            "model_dir": str(self._model_dir()),
            "count": len(items),
            "items": items,
            "recommended_fast": fast,
            "recommended_main": main,
        }

    def _find_by_name(self, name: str | None, items: list[dict[str, Any]]) -> dict[str, Any] | None:
        raw = (name or "").strip()
        if not raw:
            return None
        for item in items:
            if item.get("name") == raw:
                return item
        normalized = raw.lower()
        for item in items:
            if str(item.get("name", "")).lower() == normalized:
                return item
        for item in items:
            if normalized in str(item.get("name", "")).lower():
                return item
        return None

    def resolve_model_choice(self, prompt: str | None = None) -> dict[str, Any]:
        discovered = self.discover_models()
        items = discovered.get("items", [])
        use_main = False
        prompt_l = (prompt or "").lower()
        if any(word in prompt_l for word in ["plan", "architect", "design", "strategy", "analyze"]):
            use_main = True

        configured_name = settings.default_main_model if use_main else settings.default_fast_model
        configured_item = self._find_by_name(configured_name, items)
        fallback_item = discovered.get("recommended_main") if use_main else discovered.get("recommended_fast")
        selected_item = configured_item or fallback_item

        return {
            "ok": selected_item is not None,
            "slot": "main" if use_main else "fast",
            "configured_name": configured_name,
            "selected": selected_item,
            "selection_source": "configured" if configured_item else ("discovered" if fallback_item else None),
        }

    def effective_provider(self) -> dict[str, Any]:
        discovered = self.discover_models()
        selection = self.resolve_model_choice(prompt=None)
        provider = self._normalize_provider()
        llama_cpp_installed = importlib.util.find_spec("llama_cpp") is not None
        selected = selection.get("selected") or {}
        selected_path = Path(selected.get("path")) if selected.get("path") else None
        selected_exists = bool(selected_path and selected_path.exists())

        effective = provider
        reason = None
        if provider == "auto":
            if llama_cpp_installed and selected_exists:
                effective = "llama_cpp"
                reason = "Auto mode found llama.cpp support and a local GGUF model."
            else:
                effective = "mock"
                reason = "Auto mode fell back to mock because llama.cpp support or a usable GGUF model is missing."
        elif provider == "llama_cpp":
            if not llama_cpp_installed:
                reason = "llama.cpp Python bindings are not installed."
            elif not selected_exists:
                reason = "No usable GGUF model was found for the configured slot."
            else:
                reason = "llama.cpp is configured and a GGUF model is available."
        else:
            reason = "Mock mode is explicitly configured."

        return {
            "ok": True,
            "configured_provider": provider,
            "effective_provider": effective,
            "llama_cpp_installed": llama_cpp_installed,
            "has_any_gguf": discovered.get("count", 0) > 0,
            "selected_model": selected,
            "selected_model_slot": selection.get("slot"),
            "selected_model_exists": selected_exists,
            "reason": reason,
        }

    def consistency_summary(self) -> dict[str, Any]:
        provider = self.effective_provider()
        discovered = self.discover_models()
        loaded = llama_manager.loaded_models()
        warnings: list[str] = []

        if provider.get("effective_provider") == "llama_cpp" and not provider.get("selected_model_exists"):
            warnings.append("Local GGUF runtime is selected, but the chosen model file is missing.")
        if provider.get("configured_provider") == "llama_cpp" and not provider.get("llama_cpp_installed"):
            warnings.append("llama.cpp is configured but the Python bindings are not installed.")
        if provider.get("effective_provider") == "mock" and discovered.get("count"):
            warnings.append("Local GGUF models exist, but runtime is not currently using them.")

        overall = "pass" if not warnings else "warn"
        return {
            "ok": True,
            "overall": overall,
            "provider": provider,
            "discovered_count": discovered.get("count", 0),
            "loaded_models": loaded,
            "warnings": warnings,
            "plain_english": "This is the model/runtime consistency summary.",
            "next_action": warnings[0] if warnings else None,
        }

    def status(self) -> dict[str, Any]:
        discovered = self.discover_models()
        provider = self.effective_provider()
        fast = self.resolve_model_choice(prompt="quick reply")
        main = self.resolve_model_choice(prompt="plan and analyze this")
        consistency = self.consistency_summary()
        plain = "JARVIS is using mock mode right now."
        next_action = "Switch to local models or keep using mock mode."
        if provider.get("effective_provider") == "llama_cpp":
            name = (provider.get("selected_model") or {}).get("name")
            plain = f"JARVIS is ready to use your local GGUF model: {name}."
            next_action = "Start chatting in the shell or API and JARVIS will use your local model for non-tool replies."
        elif provider.get("configured_provider") == "auto":
            plain = provider.get("reason") or plain
            next_action = "Install llama-cpp-python or put GGUF models in data/models if you want local inference."

        return {
            "ok": True,
            "provider": provider,
            "consistency": consistency,
            "discovered": discovered,
            "fast_selection": fast,
            "main_selection": main,
            "loaded_models": llama_manager.loaded_models(),
            "plain_english": plain,
            "next_action": next_action,
        }

    def _upsert_env_key(self, content: str, key: str, value: str) -> str:
        pattern = re.compile(rf"(?m)^{re.escape(key)}=.*$")
        line = f"{key}={value}"
        if pattern.search(content):
            return pattern.sub(line, content)
        if content and not content.endswith("\n"):
            content += "\n"
        return content + line + "\n"

    def configure_provider(self, provider: str, fast_model: str | None = None, main_model: str | None = None) -> dict[str, Any]:
        normalized = self._normalize_provider(provider)
        if normalized not in {"mock", "auto", "llama_cpp"}:
            return {"ok": False, "error": f"Unsupported provider: {provider}"}

        env_path = self._env_path()
        env_path.parent.mkdir(parents=True, exist_ok=True)
        content = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
        content = self._upsert_env_key(content, "DEFAULT_MODEL_PROVIDER", normalized)

        if fast_model:
            content = self._upsert_env_key(content, "DEFAULT_FAST_MODEL", fast_model)
        if main_model:
            content = self._upsert_env_key(content, "DEFAULT_MAIN_MODEL", main_model)

        env_path.write_text(content, encoding="utf-8")

        settings.default_model_provider = normalized
        if fast_model:
            settings.default_fast_model = fast_model
        if main_model:
            settings.default_main_model = main_model

        unload_result = llama_manager.unload_all()
        return {
            "ok": True,
            "configured_provider": normalized,
            "fast_model": settings.default_fast_model,
            "main_model": settings.default_main_model,
            "env_path": str(env_path),
            "runtime_cache_reset": unload_result,
            "restart_recommended": True,
            "plain_english": f"JARVIS switched provider config to {normalized}.",
            "next_action": "Restart the API or shell if you want every process to pick up the new model settings cleanly.",
        }

    def configure_local_models(self) -> dict[str, Any]:
        discovered = self.discover_models()
        if not discovered.get("count"):
            return {
                "ok": False,
                "error": "No GGUF models were found in the local model directory.",
                "model_dir": str(self._model_dir()),
            }
        fast = discovered.get("recommended_fast") or {}
        main = discovered.get("recommended_main") or {}
        result = self.configure_provider(
            provider="auto",
            fast_model=fast.get("name"),
            main_model=main.get("name"),
        )
        result["selected_fast"] = fast
        result["selected_main"] = main
        result["plain_english"] = "JARVIS is now configured to prefer your downloaded local GGUF models and fall back safely when needed."
        return result

    def configure_mock_mode(self) -> dict[str, Any]:
        result = self.configure_provider(provider="mock")
        result["plain_english"] = "JARVIS is now configured to use mock mode for non-tool replies."
        return result

    def preload_selected_model(self, slot: str = "fast") -> dict[str, Any]:
        normalized_slot = (slot or "fast").strip().lower()
        prompt = "plan and analyze this" if normalized_slot == "main" else "quick reply"
        provider = self.effective_provider()
        if provider.get("effective_provider") != "llama_cpp":
            return {
                "ok": False,
                "error": "Local llama.cpp runtime is not currently active, so there is no GGUF model to preload.",
                "provider": provider,
            }
        choice = self.resolve_model_choice(prompt=prompt)
        selected = choice.get("selected") or {}
        selected_path = Path(selected.get("path")) if selected.get("path") else None
        if not selected_path or not selected_path.exists():
            return {
                "ok": False,
                "error": "No selected GGUF model path was found for preload.",
                "slot": normalized_slot,
                "choice": choice,
            }
        result = llama_manager.preload(selected_path)
        result["slot"] = normalized_slot
        result["model_name"] = selected.get("name")
        return result

    def unload_runtime_cache(self) -> dict[str, Any]:
        return llama_manager.unload_all()

    def verify_runtime(self, slot: str = "fast", prompt: str | None = None, expected: str | None = None) -> dict[str, Any]:
        normalized_slot = (slot or "fast").strip().lower()
        probe_prompt = prompt or f"Reply with exactly: MODEL VERIFY {normalized_slot.upper()}"
        expected_text = expected or f"MODEL VERIFY {normalized_slot.upper()}"
        provider = self.effective_provider()
        if provider.get("effective_provider") != "llama_cpp":
            return {
                "ok": False,
                "error": "Local llama.cpp runtime is not active, so runtime verification cannot run a GGUF inference test.",
                "provider": provider,
            }

        choice_prompt = "plan and analyze this" if normalized_slot == "main" else "quick reply"
        choice = self.resolve_model_choice(prompt=choice_prompt)
        selected = choice.get("selected") or {}
        model_path = Path(selected.get("path")) if selected.get("path") else None
        if not model_path or not model_path.exists():
            return {
                "ok": False,
                "error": "No selected GGUF model is available for runtime verification.",
                "slot": normalized_slot,
                "choice": choice,
            }

        reply = llama_manager.generate(
            model_path=model_path,
            system_prompt="You are JARVIS. Follow the user instruction exactly and return only the requested text when asked.",
            context_messages=[],
            user_message=probe_prompt,
            max_tokens=settings.llama_max_tokens,
        )
        model_name = selected.get("name") or model_path.name
        passed = expected_text.strip() in (reply or "")
        return {
            "ok": passed,
            "slot": normalized_slot,
            "provider": provider,
            "model_name": model_name,
            "selected_model": selected,
            "prompt": probe_prompt,
            "expected_contains": expected_text,
            "reply": reply,
            "loaded_models": llama_manager.loaded_models(),
            "plain_english": "This is the local GGUF runtime verification result.",
            "next_action": None if passed else "Inspect the reply and runtime state because the local verification output did not match the expected probe.",
        }


model_service = ModelService()
