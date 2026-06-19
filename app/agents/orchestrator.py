import json

from app.services.audit import audit_service
from app.services.browser_tool import browser_tool
from app.services.file_tool import file_tool
from app.services.llm_router import llm_router
from app.services.memory import memory_service
from app.services.shell_tool import shell_tool


class Orchestrator:
    def _handle_prefixed_tool(self, message: str) -> tuple[str | None, str | None, dict | None]:
        normalized = message.strip()
        lowered = normalized.lower()

        if lowered.startswith("shell:"):
            command = normalized.split(":", 1)[1].strip()
            result = shell_tool.run(command)
            return "shell_command", command, result

        if lowered.startswith("fs list:"):
            raw_path = normalized.split(":", 1)[1].strip()
            result = file_tool.list_dir(raw_path)
            return "fs_list", raw_path, result

        if lowered.startswith("fs read:"):
            raw_path = normalized.split(":", 1)[1].strip()
            result = file_tool.read_text(raw_path)
            return "fs_read", raw_path, result

        if lowered.startswith("fs mkdir:"):
            raw_path = normalized.split(":", 1)[1].strip()
            result = file_tool.make_dir(raw_path)
            return "fs_mkdir", raw_path, result

        if lowered.startswith("fs write:") or lowered.startswith("fs append:"):
            append = lowered.startswith("fs append:")
            raw = normalized.split(":", 1)[1].strip()
            if ":::" not in raw:
                return (
                    "tool_usage_error",
                    raw,
                    {"ok": False, "error": "Use format: fs write: relative/path.txt ::: your content"},
                )
            raw_path, content = raw.split(":::", 1)
            result = file_tool.write_text(raw_path.strip(), content.lstrip(), append=append)
            return "fs_append" if append else "fs_write", raw_path.strip(), result

        if lowered == "browser start":
            result = browser_tool.start()
            return "browser_start", "browser", result

        if lowered.startswith("browser open:") or lowered.startswith("browser visit:"):
            raw_url = normalized.split(":", 1)[1].strip()
            result = browser_tool.open_url(raw_url)
            return "browser_open", raw_url, result

        if lowered == "browser state":
            result = browser_tool.state()
            return "browser_state", "browser", result

        if lowered == "browser title":
            result = browser_tool.title()
            return "browser_title", "browser", result

        if lowered == "browser text":
            result = browser_tool.text_snapshot()
            return "browser_text", "browser", result

        if lowered.startswith("browser click:"):
            selector = normalized.split(":", 1)[1].strip()
            result = browser_tool.click(selector)
            return "browser_click", selector, result

        if lowered.startswith("browser fill:"):
            raw = normalized.split(":", 1)[1].strip()
            if ":::" not in raw:
                return (
                    "tool_usage_error",
                    raw,
                    {"ok": False, "error": "Use format: browser fill: <selector> ::: <text>"},
                )
            selector, text = raw.split(":::", 1)
            result = browser_tool.fill(selector.strip(), text.lstrip())
            return "browser_fill", selector.strip(), result

        if lowered.startswith("browser press:"):
            raw = normalized.split(":", 1)[1].strip()
            if ":::" not in raw:
                return (
                    "tool_usage_error",
                    raw,
                    {"ok": False, "error": "Use format: browser press: <selector> ::: <key>"},
                )
            selector, key = raw.split(":::", 1)
            result = browser_tool.press(selector.strip(), key.strip())
            return "browser_press", selector.strip(), result

        if lowered == "browser back":
            result = browser_tool.back()
            return "browser_back", "browser", result

        if lowered == "browser forward":
            result = browser_tool.forward()
            return "browser_forward", "browser", result

        if lowered.startswith("browser screenshot:"):
            raw_path = normalized.split(":", 1)[1].strip()
            result = browser_tool.screenshot(raw_path or None)
            return "browser_screenshot", raw_path or "auto", result

        if lowered == "browser close":
            result = browser_tool.close()
            return "browser_close", "browser", result

        return None, None, None

    def _format_tool_reply(self, tool_name: str, target: str | None, result: dict | None) -> str:
        pretty = json.dumps(result or {}, indent=2, ensure_ascii=False)
        return f"Tool `{tool_name}` executed on `{target}`.\nResult:\n{pretty}"

    def handle_chat(self, message: str, session_id: str | None, use_tools: bool = True) -> dict:
        sid = memory_service.ensure_session(session_id)
        memory_service.add_message(sid, "user", message)

        steps: list[str] = []
        context = memory_service.recent_messages(sid, limit=8)
        steps.append("loaded_recent_memory")

        tool_name = None
        target = None
        tool_result = None

        if use_tools:
            tool_name, target, tool_result = self._handle_prefixed_tool(message)
            if tool_name:
                audit_service.log_event(
                    tool_name,
                    {"session_id": sid, "target": target, "result": tool_result},
                )
                steps.append(f"executed_{tool_name}")

        if tool_name:
            reply = self._format_tool_reply(tool_name, target, tool_result)
            model_name = "tool_only"
        else:
            reply, model_name = llm_router.generate_reply(message, context)
            steps.append(f"generated_reply_with_{model_name}")

        memory_service.add_message(sid, "assistant", reply)
        audit_service.log_event(
            "chat_turn",
            {
                "session_id": sid,
                "message": message,
                "reply_preview": reply[:300],
                "steps": steps,
                "model": model_name,
            },
        )

        return {
            "session_id": sid,
            "reply": reply,
            "steps": steps,
        }


orchestrator = Orchestrator()
