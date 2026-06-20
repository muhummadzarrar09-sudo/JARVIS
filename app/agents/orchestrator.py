import json

from app.services.app_wrapper_service import app_wrapper_service
from app.services.audit import audit_service
from app.services.browser_tool import browser_tool
from app.services.checkpoint_service import checkpoint_service
from app.services.desktop_tool import desktop_tool
from app.services.file_tool import file_tool
from app.services.llm_router import llm_router
from app.services.memory import memory_service
from app.services.process_tool import process_tool
from app.services.shell_tool import shell_tool
from app.services.task_service import task_service


class Orchestrator:
    def _tail_after_prefixes(self, normalized: str, lowered: str, prefixes: list[str]) -> str | None:
        for prefix in prefixes:
            if lowered.startswith(prefix):
                return normalized[len(prefix):].strip()
        return None

    def _coerce_browser_selector(self, raw: str) -> str:
        selector = raw.strip()
        if not selector:
            return selector

        known_prefixes = (
            "text=",
            "css=",
            "xpath=",
            "id=",
            "role=",
            "label=",
            "placeholder=",
        )
        if selector.startswith(known_prefixes):
            return selector
        if selector.startswith(("//", "#", ".", "[")):
            return selector
        return f"text={selector}"

    def _parse_click_payload(self, raw: str) -> tuple[int | None, int | None, str | None, str | None]:
        button = "left"
        coords_part = raw.strip()
        if ":::" in coords_part:
            coords_part, button_part = coords_part.split(":::", 1)
            button = button_part.strip() or "left"
        parts = [p.strip() for p in coords_part.split(",")]
        if len(parts) != 2:
            return None, None, None, "Use format: desktop click: x,y or desktop click: x,y ::: right"
        try:
            x = int(parts[0])
            y = int(parts[1])
            return x, y, button, None
        except ValueError:
            return None, None, None, "Desktop click coordinates must be integers."

    def _parse_hotkey_payload(self, raw: str) -> list[str]:
        if "+" in raw:
            return [part.strip() for part in raw.split("+") if part.strip()]
        return [part.strip() for part in raw.split() if part.strip()]

    def _handle_prefixed_tool(self, message: str, session_id: str) -> tuple[str | None, str | None, dict | None]:
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

        if lowered == "browser state":
            result = browser_tool.state()
            return "browser_state", "browser", result

        if lowered == "browser title":
            result = browser_tool.title()
            return "browser_title", "browser", result

        if lowered == "browser text":
            result = browser_tool.text_snapshot()
            return "browser_text", "browser", result

        raw_url = self._tail_after_prefixes(normalized, lowered, ["browser open:", "browser open ", "browser visit:", "browser visit "])
        if raw_url is not None:
            result = browser_tool.open_url(raw_url)
            return "browser_open", raw_url, result

        raw_inspect = self._tail_after_prefixes(normalized, lowered, ["browser inspect:", "browser inspect "])
        if raw_inspect is not None:
            selector = self._coerce_browser_selector(raw_inspect)
            result = browser_tool.inspect(selector)
            return "browser_inspect", selector, result

        raw_click = self._tail_after_prefixes(normalized, lowered, ["browser click:", "browser click "])
        if raw_click is not None:
            selector = self._coerce_browser_selector(raw_click)
            result = browser_tool.click(selector, force=False)
            return "browser_click", selector, result

        raw_forceclick = self._tail_after_prefixes(normalized, lowered, ["browser forceclick:", "browser forceclick "])
        if raw_forceclick is not None:
            selector = self._coerce_browser_selector(raw_forceclick)
            result = browser_tool.click(selector, force=True)
            return "browser_forceclick", selector, result

        raw_fill = self._tail_after_prefixes(normalized, lowered, ["browser fill:", "browser fill "])
        if raw_fill is not None:
            if ":::" not in raw_fill:
                return (
                    "tool_usage_error",
                    raw_fill,
                    {"ok": False, "error": "Use format: browser fill: <selector> ::: <text>"},
                )
            selector, text = raw_fill.split(":::", 1)
            final_selector = self._coerce_browser_selector(selector)
            result = browser_tool.fill(final_selector, text.lstrip())
            return "browser_fill", final_selector, result

        raw_press = self._tail_after_prefixes(normalized, lowered, ["browser press:", "browser press "])
        if raw_press is not None:
            if ":::" not in raw_press:
                return (
                    "tool_usage_error",
                    raw_press,
                    {"ok": False, "error": "Use format: browser press: <selector> ::: <key>"},
                )
            selector, key = raw_press.split(":::", 1)
            final_selector = self._coerce_browser_selector(selector)
            result = browser_tool.press(final_selector, key.strip())
            return "browser_press", final_selector, result

        if lowered == "browser back":
            result = browser_tool.back()
            return "browser_back", "browser", result

        if lowered == "browser forward":
            result = browser_tool.forward()
            return "browser_forward", "browser", result

        raw_screenshot = self._tail_after_prefixes(normalized, lowered, ["browser screenshot:", "browser screenshot "])
        if raw_screenshot is not None:
            result = browser_tool.screenshot(raw_screenshot or None)
            return "browser_screenshot", raw_screenshot or "auto", result

        if lowered == "browser close":
            result = browser_tool.close()
            return "browser_close", "browser", result

        if lowered == "app wrappers":
            result = app_wrapper_service.list_wrappers()
            return "app_wrappers", "apps", result

        if lowered == "app recipes":
            result = app_wrapper_service.list_recipes()
            return "app_recipes", "apps", result

        if lowered in {"app status", "app state"}:
            result = app_wrapper_service.wrapper_status(None)
            return "app_status", "apps", result

        raw_app_status = self._tail_after_prefixes(normalized, lowered, ["app status:", "app status ", "app state:", "app state "])
        if raw_app_status is not None:
            result = app_wrapper_service.wrapper_status(raw_app_status.strip())
            return "app_status", raw_app_status.strip(), result

        if lowered == "app reset":
            result = app_wrapper_service.reset_wrapper_state(None)
            return "app_reset", "all", result

        raw_app_reset = self._tail_after_prefixes(normalized, lowered, ["app reset:", "app reset "])
        if raw_app_reset is not None:
            result = app_wrapper_service.reset_wrapper_state(raw_app_reset.strip())
            return "app_reset", raw_app_reset.strip(), result

        raw_app_recipe = self._tail_after_prefixes(normalized, lowered, ["app recipe:", "app recipe "])
        if raw_app_recipe is not None:
            if ":::" in raw_app_recipe:
                recipe_name, payload = raw_app_recipe.split(":::", 1)
                result = app_wrapper_service.run_recipe(recipe_name.strip(), target=payload.strip(), text=payload.strip())
                return "app_recipe", recipe_name.strip(), result
            result = app_wrapper_service.run_recipe(raw_app_recipe.strip())
            return "app_recipe", raw_app_recipe.strip(), result

        raw_app_open = self._tail_after_prefixes(normalized, lowered, ["app open:", "app open "])
        if raw_app_open is not None:
            if ":::" in raw_app_open:
                name, target = raw_app_open.split(":::", 1)
                result = app_wrapper_service.open_app(name.strip(), target=target.strip())
                return "app_open", name.strip(), result
            result = app_wrapper_service.open_app(raw_app_open.strip(), target=None)
            return "app_open", raw_app_open.strip(), result

        raw_app_focus = self._tail_after_prefixes(normalized, lowered, ["app focus:", "app focus "])
        if raw_app_focus is not None:
            result = app_wrapper_service.focus_app(raw_app_focus.strip(), exact=False)
            return "app_focus", raw_app_focus.strip(), result

        raw_app_focus_exact = self._tail_after_prefixes(normalized, lowered, ["app focusexact:", "app focusexact "])
        if raw_app_focus_exact is not None:
            result = app_wrapper_service.focus_app(raw_app_focus_exact.strip(), exact=True)
            return "app_focus_exact", raw_app_focus_exact.strip(), result

        raw_app_ensure = self._tail_after_prefixes(normalized, lowered, ["app ensure:", "app ensure "])
        if raw_app_ensure is not None:
            if ":::" in raw_app_ensure:
                name, target = raw_app_ensure.split(":::", 1)
                result = app_wrapper_service.ensure_app(name.strip(), target=target.strip(), exact=False)
                return "app_ensure", name.strip(), result
            result = app_wrapper_service.ensure_app(raw_app_ensure.strip(), target=None, exact=False)
            return "app_ensure", raw_app_ensure.strip(), result

        raw_app_note = self._tail_after_prefixes(normalized, lowered, ["app note:", "app note "])
        if raw_app_note is not None:
            result = app_wrapper_service.quick_note(raw_app_note)
            return "app_note", "notepad", result

        raw_app_explore = self._tail_after_prefixes(normalized, lowered, ["app explore:", "app explore "])
        if raw_app_explore is not None:
            result = app_wrapper_service.open_path_in_explorer(raw_app_explore)
            return "app_explore", raw_app_explore, result

        raw_app_code = self._tail_after_prefixes(normalized, lowered, ["app code:", "app code "])
        if raw_app_code is not None:
            result = app_wrapper_service.open_path_in_vscode(raw_app_code)
            return "app_code", raw_app_code, result

        raw_app_browse = self._tail_after_prefixes(normalized, lowered, ["app browse:", "app browse "])
        if raw_app_browse is not None:
            result = app_wrapper_service.open_url_in_browser(raw_app_browse)
            return "app_browse", raw_app_browse, result

        if lowered == "desktop windows":
            result = desktop_tool.list_windows()
            return "desktop_windows", "desktop", result

        if lowered == "desktop active":
            result = desktop_tool.active_window()
            return "desktop_active", "desktop", result

        if lowered == "desktop screen":
            result = desktop_tool.screen_info()
            return "desktop_screen", "desktop", result

        raw_desktop_focus = self._tail_after_prefixes(normalized, lowered, ["desktop focus:", "desktop focus "])
        if raw_desktop_focus is not None:
            result = desktop_tool.focus_window(raw_desktop_focus, exact=False)
            return "desktop_focus", raw_desktop_focus, result

        raw_desktop_focus_exact = self._tail_after_prefixes(normalized, lowered, ["desktop focusexact:", "desktop focusexact "])
        if raw_desktop_focus_exact is not None:
            result = desktop_tool.focus_window(raw_desktop_focus_exact, exact=True)
            return "desktop_focus_exact", raw_desktop_focus_exact, result

        raw_desktop_type = self._tail_after_prefixes(normalized, lowered, ["desktop type:", "desktop type ", "desktop write:", "desktop write "])
        if raw_desktop_type is not None:
            result = desktop_tool.type_text(raw_desktop_type)
            return "desktop_type", "focused_window", result

        raw_desktop_press = self._tail_after_prefixes(normalized, lowered, ["desktop press:", "desktop press "])
        if raw_desktop_press is not None:
            result = desktop_tool.press_key(raw_desktop_press.strip())
            return "desktop_press", raw_desktop_press.strip(), result

        raw_desktop_hotkey = self._tail_after_prefixes(normalized, lowered, ["desktop hotkey:", "desktop hotkey "])
        if raw_desktop_hotkey is not None:
            keys = self._parse_hotkey_payload(raw_desktop_hotkey)
            result = desktop_tool.hotkey(keys)
            return "desktop_hotkey", "+".join(keys), result

        raw_desktop_click = self._tail_after_prefixes(normalized, lowered, ["desktop click:", "desktop click "])
        if raw_desktop_click is not None:
            x, y, button, error = self._parse_click_payload(raw_desktop_click)
            if error:
                return ("tool_usage_error", raw_desktop_click, {"ok": False, "error": error})
            result = desktop_tool.click(x, y, button=button or "left")
            return "desktop_click", f"{x},{y}", result

        if lowered == "desktop screenshot":
            result = desktop_tool.screenshot(None)
            return "desktop_screenshot", "auto", result

        raw_desktop_screenshot = self._tail_after_prefixes(normalized, lowered, ["desktop screenshot:", "desktop screenshot "])
        if raw_desktop_screenshot is not None:
            result = desktop_tool.screenshot(raw_desktop_screenshot or None)
            return "desktop_screenshot", raw_desktop_screenshot or "auto", result

        if lowered == "proc list":
            result = process_tool.list_processes()
            return "proc_list", "all", result

        raw_proc_list = self._tail_after_prefixes(normalized, lowered, ["proc list:", "proc list "])
        if raw_proc_list is not None:
            result = process_tool.list_processes(filter_name=raw_proc_list)
            return "proc_list", raw_proc_list, result

        if lowered == "proc windows":
            result = process_tool.list_windows()
            return "proc_windows", "windows", result

        raw_proc_start = self._tail_after_prefixes(normalized, lowered, ["proc start:", "proc start "])
        if raw_proc_start is not None:
            result = process_tool.start_process(raw_proc_start)
            return "proc_start", raw_proc_start, result

        raw_proc_kill = self._tail_after_prefixes(normalized, lowered, ["proc kill:", "proc kill "])
        if raw_proc_kill is not None:
            result = process_tool.kill_process(raw_proc_kill)
            return "proc_kill", raw_proc_kill, result

        if lowered == "checkpoint create":
            result = checkpoint_service.create(session_id)
            return "checkpoint_create", session_id, result

        raw_checkpoint = self._tail_after_prefixes(normalized, lowered, ["checkpoint create:", "checkpoint create "])
        if raw_checkpoint is not None:
            result = checkpoint_service.create(session_id, note=raw_checkpoint)
            return "checkpoint_create", session_id, result

        if lowered == "checkpoint get":
            result = checkpoint_service.load(session_id)
            return "checkpoint_get", session_id, result

        raw_task_create = self._tail_after_prefixes(normalized, lowered, ["task create:", "task create "])
        if raw_task_create is not None:
            result = task_service.create_task(title=raw_task_create, session_id=session_id)
            return "task_create", raw_task_create, result

        if lowered == "task list":
            result = {"ok": True, "items": task_service.list_tasks(status=None, limit=50)}
            return "task_list", "all", result

        if lowered == "task open":
            result = {"ok": True, "items": task_service.list_tasks(status="open", limit=50)}
            return "task_list_open", "open", result

        if lowered == "task done":
            return (
                "tool_usage_error",
                "task done",
                {"ok": False, "error": "Use format: task done: <id>"},
            )

        raw_task_done = self._tail_after_prefixes(normalized, lowered, ["task done:", "task done "])
        if raw_task_done is not None:
            if not raw_task_done.isdigit():
                return (
                    "tool_usage_error",
                    raw_task_done,
                    {"ok": False, "error": "Task id must be a number."},
                )
            result = task_service.update_status(int(raw_task_done), "done")
            return "task_done", raw_task_done, result

        raw_task_reopen = self._tail_after_prefixes(normalized, lowered, ["task reopen:", "task reopen "])
        if raw_task_reopen is not None:
            if not raw_task_reopen.isdigit():
                return (
                    "tool_usage_error",
                    raw_task_reopen,
                    {"ok": False, "error": "Task id must be a number."},
                )
            result = task_service.update_status(int(raw_task_reopen), "open")
            return "task_reopen", raw_task_reopen, result

        if lowered == "session list":
            result = {"ok": True, "items": memory_service.list_sessions(limit=20)}
            return "session_list", "recent", result

        if lowered == "session overview":
            result = memory_service.session_overview(session_id)
            return "session_overview", session_id, result

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
            tool_name, target, tool_result = self._handle_prefixed_tool(message, sid)
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
