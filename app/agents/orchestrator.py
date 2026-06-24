import json

from app.services.app_wrapper_service import app_wrapper_service
from app.services.audit import audit_service
from app.services.browser_tool import browser_tool
from app.services.checkpoint_service import checkpoint_service
from app.services.desktop_tool import desktop_tool
from app.services.file_tool import file_tool
from app.services.llm_router import llm_router
from app.services.memory import memory_service
from app.services.model_service import model_service
from app.services.operator_mode import operator_mode_service
from app.services.process_tool import process_tool
from app.services.progress_service import progress_service
from app.services.quick_actions_service import quick_actions_service
from app.services.shell_tool import shell_tool
from app.services.task_service import task_service
from app.services.validation_service import validation_service


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

    def _handle_easy_command(self, normalized: str, lowered: str) -> tuple[str | None, str | None, dict | None]:
        if lowered in {"what can you do", "show examples", "starter commands", "help me start", "help me", "show starter guide"}:
            return "quick_guide", "guide", quick_actions_service.guide()

        if lowered in {"what should i do next", "what next", "show next steps", "show me what to do next", "show me where to start", "where should i start", "get me started"}:
            return "quick_next_steps", "guide", quick_actions_service.next_steps()

        if lowered in {"show me today", "today", "give me my day", "show me my day", "how does my day look"}:
            return "quick_today", "guide", quick_actions_service.today_brief()

        if lowered in {"show my progress", "how am i doing", "where am i at", "show progress", "how's my progress"}:
            return "quick_progress", "guide", quick_actions_service.progress()

        if lowered in {"validate my machine", "validate my setup", "show validation report", "run validation"}:
            return "validation_report", "validation", validation_service.report()

        if lowered in {"show model status", "model status", "which model are you using", "what model are you using", "show local models", "show gguf models"}:
            return "model_status", "models", model_service.status()

        if lowered in {"use local models", "use downloaded models", "use gguf models", "switch to local models", "switch to gguf models"}:
            return "model_configure", "auto", model_service.configure_local_models()

        if lowered in {"use mock mode", "use mock models", "switch to mock mode", "switch to mock models"}:
            return "model_configure", "mock", model_service.configure_mock_mode()

        if lowered in {"how much is phase 4 done", "phase 4 status", "phase 4 progress", "what's left in phase 4", "whats left in phase 4"}:
            return "phase4_status", "phase4", progress_service.phase4_status()

        if lowered in {"show me today's focus", "what should i focus on", "focus me", "show my focus", "what should i work on right now", "show me my focus"}:
            return "quick_focus", "guide", quick_actions_service.focus()

        if lowered in {"help me continue where i left off", "continue where i left off", "continue my work", "take me back to my last work", "open my last project"}:
            return "app_recipe", "project.resume", app_wrapper_service.run_recipe("project.resume")

        if lowered in {"show me recent work", "what was i doing", "where did i leave off"}:
            return "quick_recent_work", "recent", quick_actions_service.recent_work_summary()

        if lowered in {"resume last session"}:
            return "session_list", "recent", {"ok": True, "items": memory_service.list_sessions(limit=10)}

        if lowered in {"set me up to work on this project", "set up my project", "open my project tools", "start my project tools", "start my workday", "get me ready to work"}:
            return "app_recipe", "project.starter", app_wrapper_service.run_recipe("project.starter", target=".")

        if lowered in {"start coding", "set me up to code", "get me ready to code"}:
            return "app_recipe", "coding.start", app_wrapper_service.run_recipe("coding.start", target=".")

        if lowered in {"continue coding", "resume coding", "get me back to coding"}:
            return "app_recipe", "coding.resume", app_wrapper_service.run_recipe("coding.resume", target=".")

        if lowered in {"review this project", "give me the project overview", "show project overview", "help me review this project", "summarize this project"}:
            return "app_recipe", "project.review", app_wrapper_service.run_recipe("project.review", target=".")

        if lowered in {"show my project files", "show project files", "open my project files", "open my workspace"}:
            return "app_recipe", "project.files", app_wrapper_service.run_recipe("project.files", target=".")

        if lowered in {"show my setup blockers", "what is blocking me", "show blockers"}:
            return "quick_setup", "setup", quick_actions_service.setup_summary()

        if lowered in {"show my tasks", "show tasks", "what are my tasks", "what am i working on", "open my tasks"}:
            return "task_list_open", "open", {"ok": True, "items": task_service.list_tasks(status="open", limit=20)}

        if lowered in {"show my sessions", "recent sessions", "show recent sessions"}:
            return "session_list", "recent", {"ok": True, "items": memory_service.list_sessions(limit=10)}

        if lowered in {"what task should i do next", "next task", "focus me on the next task"}:
            return "task_next", "next", task_service.next_task()

        if lowered in {"what am i doing now", "current task", "what is my current task"}:
            current = task_service.current_task()
            return ("task_current", "current", current if current.get("ok") else task_service.next_task())

        if lowered in {"wrap up current task", "finish what i'm doing", "complete current task"}:
            current = task_service.current_task()
            if current.get("ok") and current.get("id"):
                return "task_done", str(current.get("id")), task_service.update_status(int(current.get("id")), "done")
            fallback = task_service.next_task()
            if fallback.get("ok") and fallback.get("id"):
                return "task_done", str(fallback.get("id")), task_service.update_status(int(fallback.get("id")), "done")
            return "task_next", "next", fallback

        if lowered.startswith("add task ") or lowered.startswith("create task "):
            prefix = "add task " if lowered.startswith("add task ") else "create task "
            title = normalized[len(prefix):].strip()
            return "task_create", title, task_service.create_task(title=title, session_id=None)

        if lowered.startswith("done with task "):
            raw_id = normalized[len("done with task "):].strip()
            if raw_id.isdigit():
                return "task_done", raw_id, task_service.update_status(int(raw_id), "done")

        if lowered in {"work on next task", "start next task", "begin next task"}:
            next_task = task_service.next_task()
            if next_task.get("ok") and next_task.get("id"):
                return "task_in_progress", str(next_task.get("id")), task_service.update_status(int(next_task.get("id")), "in_progress")
            return "task_next", "next", next_task

        if lowered in {"complete next task", "mark next task done", "finish next task"}:
            next_task = task_service.next_task()
            if next_task.get("ok") and next_task.get("id"):
                return "task_done", str(next_task.get("id")), task_service.update_status(int(next_task.get("id")), "done")
            return "task_next", "next", next_task

        if lowered.startswith("focus on task ") or lowered.startswith("start task "):
            prefix = "focus on task " if lowered.startswith("focus on task ") else "start task "
            raw_id = normalized[len(prefix):].strip()
            if raw_id.isdigit():
                return "task_in_progress", raw_id, task_service.update_status(int(raw_id), "in_progress")

        if lowered.startswith("pause task "):
            raw_id = normalized[len("pause task "):].strip()
            if raw_id.isdigit():
                return "task_reopen", raw_id, task_service.update_status(int(raw_id), "open")

        if lowered.startswith("reopen task "):
            raw_id = normalized[len("reopen task "):].strip()
            if raw_id.isdigit():
                return "task_reopen", raw_id, task_service.update_status(int(raw_id), "open")

        if lowered in {"show wrapper status", "show wrappers", "wrapper status"}:
            return "app_status", "apps", app_wrapper_service.wrapper_status(None)

        if lowered in {"show setup", "check my setup", "check setup", "are my tools ready", "check if my tools are ready", "what is blocking me"}:
            return "quick_setup", "setup", quick_actions_service.setup_summary()

        if lowered in {"run doctor", "show doctor"}:
            return "app_doctor", "apps", app_wrapper_service.wrapper_doctor(None)

        if lowered in {"show my project", "project info", "what project is this", "inspect project"}:
            return "app_project_context", "project", app_wrapper_service.current_project_context(None)

        if lowered in {"open browser", "start browser"}:
            return "app_ensure", "browser", app_wrapper_service.ensure_app("browser", target="https://example.com")

        if lowered in {"use default browser", "reset browser preference", "browser auto"}:
            return "browser_preference", "auto", app_wrapper_service.set_browser_preference(None)

        for browser_name in ("chrome", "msedge", "edge", "brave", "firefox"):
            if lowered in {f"use {browser_name}", f"prefer {browser_name}", f"use {browser_name} browser", f"prefer {browser_name} browser"}:
                requested = "msedge" if browser_name == "edge" else browser_name
                return "browser_preference", requested, app_wrapper_service.set_browser_preference(requested)
            if lowered in {f"use {browser_name} for browser", f"prefer {browser_name} for browser"}:
                requested = "msedge" if browser_name == "edge" else browser_name
                return "browser_preference", requested, app_wrapper_service.set_browser_preference(requested)
            
             
            if lowered == f"open {browser_name}":
                requested = "msedge" if browser_name == "edge" else browser_name
                return "app_ensure", requested, app_wrapper_service.ensure_app("browser", target="https://example.com", browser_name=requested)
            if lowered.startswith(f"open {browser_name} to "):
                requested = "msedge" if browser_name == "edge" else browser_name
                target = normalized[len(f"open {browser_name} to "):].strip()
                return "app_ensure", requested, app_wrapper_service.ensure_app("browser", target=target, browser_name=requested)

        if lowered in {"show browser options", "what browsers can you use", "which browser will you use", "browser options"}:
            return "browser_available", "browser", browser_tool.available_browsers()

        if lowered in {"show me browser status", "show browser status", "browser status", "what is my browser doing"}:
            return "app_browser_context", "browser", app_wrapper_service.current_browser_context()

        if lowered.startswith("open browser to "):
            target = normalized[len("open browser to "):].strip()
            return "app_ensure", "browser", app_wrapper_service.ensure_app("browser", target=target)

        if lowered.startswith("browse to "):
            target = normalized[len("browse to "):].strip()
            return "app_ensure", "browser", app_wrapper_service.ensure_app("browser", target=target)

        if lowered.startswith("search for "):
            query = normalized[len("search for "):].strip()
            return "app_recipe", "browser.search", app_wrapper_service.run_recipe("browser.search", text=query)

        if lowered.startswith("search this site for "):
            query = normalized[len("search this site for "):].strip()
            return "app_recipe", "browser.site_search", app_wrapper_service.run_recipe("browser.site_search", text=query)

        if lowered.startswith("find on this site "):
            query = normalized[len("find on this site "):].strip()
            return "app_recipe", "browser.site_search", app_wrapper_service.run_recipe("browser.site_search", text=query)

        if lowered.startswith("research "):
            query = normalized[len("research "):].strip()
            return "app_recipe", "browser.research", app_wrapper_service.run_recipe("browser.research", text=query)

        if lowered.startswith("start research on "):
            query = normalized[len("start research on "):].strip()
            return "app_recipe", "browser.research", app_wrapper_service.run_recipe("browser.research", text=query)

        if lowered.startswith("research this "):
            query = normalized[len("research this "):].strip()
            return "app_recipe", "browser.research", app_wrapper_service.run_recipe("browser.research", text=query)

        if lowered.startswith("look up "):
            query = normalized[len("look up "):].strip()
            return "app_recipe", "browser.search", app_wrapper_service.run_recipe("browser.search", text=query)

        if lowered in {"show me the current page", "show current page", "what page am i on", "resume browser", "continue browsing", "read the current page"}:
            return "app_recipe", "browser.resume", app_wrapper_service.run_recipe("browser.resume")

        if lowered in {"open code", "open vscode", "open code here", "open this folder in code", "open my code"}:
            return "app_code", ".", app_wrapper_service.open_path_in_vscode(".")

        if lowered.startswith("open code in "):
            target = normalized[len("open code in "):].strip()
            return "app_code", target, app_wrapper_service.open_path_in_vscode(target)

        if lowered in {"open files", "open file explorer", "open files here", "open explorer", "open my files"}:
            return "app_explore", ".", app_wrapper_service.open_path_in_explorer(".")

        if lowered.startswith("open files in "):
            target = normalized[len("open files in "):].strip()
            return "app_explore", target, app_wrapper_service.open_path_in_explorer(target)

        if lowered in {"open terminal", "open terminal here", "start terminal"}:
            return "app_ensure", "terminal", app_wrapper_service.ensure_app("terminal", target=".")

        if lowered.startswith("open terminal in "):
            target = normalized[len("open terminal in "):].strip()
            return "app_ensure", "terminal", app_wrapper_service.ensure_app("terminal", target=target)

        if lowered in {"resume project", "resume my project"}:
            return "app_recipe", "project.resume", app_wrapper_service.run_recipe("project.resume")

        if lowered in {"open readme", "show readme", "open readme in code", "show me the readme"}:
            return "app_recipe", "vscode.readme", app_wrapper_service.run_recipe("vscode.readme", target=".")

        if lowered in {"resume code", "resume vscode"}:
            return "app_recipe", "vscode.resume", app_wrapper_service.run_recipe("vscode.resume")

        if lowered in {"resume browser", "show me the current page", "continue browsing"}:
            return "app_recipe", "browser.resume", app_wrapper_service.run_recipe("browser.resume")

        if lowered in {"take screenshot", "screenshot", "capture screenshot"}:
            return "desktop_screenshot", "auto", desktop_tool.screenshot(None)

        if lowered.startswith("write note "):
            text = normalized[len("write note "):].strip()
            return "app_note", "notepad", app_wrapper_service.quick_note(text)

        if lowered.startswith("remember this "):
            text = normalized[len("remember this "):].strip()
            return "app_note", "notepad", app_wrapper_service.quick_note(text)

        return None, None, None

    def _handle_prefixed_tool(self, message: str, session_id: str) -> tuple[str | None, str | None, dict | None]:
        normalized = message.strip()
        lowered = normalized.lower()

        easy_tool_name, easy_target, easy_result = self._handle_easy_command(normalized, lowered)
        if easy_tool_name:
            return easy_tool_name, easy_target, easy_result

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

        if lowered == "model status":
            result = model_service.status()
            return "model_status", "models", result

        if lowered == "model use local":
            result = model_service.configure_local_models()
            return "model_configure", "auto", result

        if lowered == "model use mock":
            result = model_service.configure_mock_mode()
            return "model_configure", "mock", result

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

        if lowered in {"app doctor", "app diagnose"}:
            result = app_wrapper_service.wrapper_doctor(None)
            return "app_doctor", "apps", result

        if lowered in {"app project", "app context"}:
            result = app_wrapper_service.current_project_context(None)
            return "app_project_context", "project", result

        raw_app_status = self._tail_after_prefixes(normalized, lowered, ["app status:", "app status ", "app state:", "app state "])
        if raw_app_status is not None:
            result = app_wrapper_service.wrapper_status(raw_app_status.strip())
            return "app_status", raw_app_status.strip(), result

        raw_app_doctor = self._tail_after_prefixes(normalized, lowered, ["app doctor:", "app doctor ", "app diagnose:", "app diagnose "])
        if raw_app_doctor is not None:
            result = app_wrapper_service.wrapper_doctor(raw_app_doctor.strip())
            return "app_doctor", raw_app_doctor.strip(), result

        raw_app_project = self._tail_after_prefixes(normalized, lowered, ["app project:", "app project ", "app context:", "app context "])
        if raw_app_project is not None:
            result = app_wrapper_service.current_project_context(raw_app_project.strip())
            return "app_project_context", raw_app_project.strip(), result

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

        raw_desktop_find = self._tail_after_prefixes(normalized, lowered, ["desktop find:", "desktop find "])
        if raw_desktop_find is not None:
            result = desktop_tool.find_windows(raw_desktop_find, exact=False)
            return "desktop_find", raw_desktop_find, result

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

    def _extract_error(self, data: dict | list | None) -> str | None:
        if isinstance(data, dict):
            if isinstance(data.get("error"), str) and data.get("error"):
                return data.get("error")
            for value in data.values():
                err = self._extract_error(value)
                if err:
                    return err
        elif isinstance(data, list):
            for item in data:
                err = self._extract_error(item)
                if err:
                    return err
        return None

    def _format_tool_reply(self, tool_name: str, target: str | None, result: dict | None) -> str:
        data = result or {}
        ok = data.get("ok")
        status = "✅ Success" if ok else ("⚠ Partial" if ok is None else "❌ Could not complete")

        summary = None
        if isinstance(data.get("plain_english"), str) and data.get("plain_english"):
            summary = data.get("plain_english")
        elif tool_name in {"task_create", "task_done", "task_reopen", "task_in_progress", "task_next", "task_current"}:
            if data.get("title"):
                summary = f"Task: {data.get('title')}"
            elif isinstance(data.get('items'), list):
                summary = f"Found {len(data.get('items', []))} task item(s)."
        elif tool_name == "session_list" and isinstance(data.get('items'), list):
            summary = f"Found {len(data.get('items', []))} recent session(s)."
        elif tool_name == "quick_recent_work":
            summary = "Here is a simple summary of your recent work."
        elif tool_name == "quick_setup":
            summary = data.get("plain_english") or "Here is your setup summary."
        elif tool_name == "validation_report":
            summary = data.get("plain_english") or "Here is your validation report."
        elif tool_name == "phase4_status" and data.get("percent") is not None:
            summary = f"Phase 4 is {data.get('percent')}% complete."
        elif tool_name == "model_status":
            summary = data.get("plain_english") or "Here is your local model status."
        elif tool_name == "model_configure":
            summary = data.get("plain_english") or "JARVIS updated your model configuration."
        elif data.get("fallback") == "readme_preview":
            summary = "JARVIS showed a README preview instead of opening an app."
        elif data.get("fallback") == "directory_listing":
            summary = "JARVIS showed the folder contents instead of opening an app."
        elif data.get("fallback") == "browser_link":
            summary = "JARVIS prepared a browser link for you to open manually."
        elif data.get("fallback") == "workspace_start_fallback":
            summary = "JARVIS prepared a manual project-start pack instead of opening the missing apps."
        elif tool_name.startswith("app_") and data.get("wrapper"):
            summary = f"Wrapper: {data.get('wrapper')}"
        elif tool_name == "app_project_context" and data.get("path"):
            summary = f"Project path: {data.get('path')}"
        elif tool_name == "browser_available" and isinstance(data.get('items'), list):
            summary = f"JARVIS found {len(data.get('items', []))} browser option(s)."
        elif tool_name == "app_browser_context":
            if data.get("started"):
                summary = f"Current browser page: {data.get('title') or data.get('url')}"
            elif data.get("remembered_url"):
                summary = f"Remembered browser page: {data.get('remembered_url')}"
        elif tool_name.startswith("browser_") and data.get("url"):
            summary = f"Browser URL: {data.get('url')}"
        elif tool_name == "app_recipe" and data.get("site"):
            summary = f"Scoped browser search on {data.get('site')}"
        elif tool_name.startswith("desktop_") and data.get("path"):
            summary = f"Saved artifact: {data.get('path')}"
        else:
            extracted_error = self._extract_error(data)
            if extracted_error:
                summary = extracted_error

        tip = None
        extracted_error = self._extract_error(data)
        if tool_name == "app_doctor":
            tip = "Use this to see what is ready on your machine before trying wrapper recipes."
        elif tool_name == "app_project_context":
            tip = "Try: open readme, open code here, open terminal here, or resume project."
        elif tool_name == "browser_available":
            tip = "JARVIS will try browsers in the order shown by your configured preference list."
        elif tool_name == "app_browser_context":
            tip = "Try: show me the current page, search for something, search this site for something, or open browser to a URL."
        elif tool_name == "session_list":
            tip = "In the terminal, use /sessions and then /use 1 or /resume to switch sessions."
        elif tool_name == "quick_today":
            tip = "You can say: show me today's focus, show my tasks, review this project, or start coding."
        elif tool_name == "quick_progress":
            tip = "You can say: what task should i do next, show my sessions, or show me the current page."
        elif tool_name == "validation_report":
            tip = "Use this before testing wrappers on your real machine so you know what is missing."
        elif tool_name == "model_status":
            tip = "If local GGUF models are available, you can say: use local models. If you want the old behavior, say: use mock mode."
        elif tool_name == "model_configure":
            tip = "After changing model mode, restarting the API or shell is the safest way to ensure every process picks up the new settings."
        elif tool_name == "quick_setup":
            tip = "You can say: run doctor for technical details, or open readme / start coding to keep moving." 
        elif tool_name == "quick_focus":
            tip = "You can say: work on next task, complete current task, open code here, or open terminal here."
        elif tool_name == "quick_recent_work":
            tip = "You can say: resume project, show my sessions, or show me today's focus."
        elif tool_name == "phase4_status":
            tip = "Use this to see how much of the desktop-control phase is complete and what is left."
        elif tool_name in {"task_list_open", "task_next", "task_in_progress", "task_current"}:
            tip = "You can say: add task ..., focus on task 2, work on next task, complete next task, done with task 2, or reopen task 2."
        elif data.get("fallback") == "readme_preview":
            tip = "The app was unavailable, so JARVIS gave you the README directly to keep you moving."
        elif data.get("fallback") == "directory_listing":
            tip = "The app was unavailable, so JARVIS showed the folder contents instead."
        elif data.get("fallback") == "browser_link":
            tip = "Browser automation was unavailable, so JARVIS gave you a link you can open manually."
        elif data.get("fallback") == "workspace_start_fallback":
            tip = "The normal coding apps were unavailable, so JARVIS returned the project essentials you can use manually."
        elif not ok and extracted_error and "Playwright is not installed" in extracted_error:
            tip = "Install browser support locally with .\\scripts\\install-browser.ps1, then retry."
        elif not ok and extracted_error and "code: not found" in extracted_error:
            tip = "VS Code command line launcher is missing on this machine. Make sure `code` is on PATH."
        elif not ok and extracted_error and ("start powershell" in extracted_error or "PowerShell" in extracted_error):
            tip = "This terminal wrapper expects PowerShell on Windows. Retry on your real laptop environment."
        elif not ok and tool_name.startswith("app_recipe"):
            tip = "If this is a Windows app or browser flow, retry it on your local machine where the actual app exists."
        elif not ok and tool_name.startswith("app_ensure"):
            tip = "Run app doctor to check whether the wrapper has what it needs."

        pretty = json.dumps(data, indent=2, ensure_ascii=False)
        lines = [f"{status} — `{tool_name}` on `{target}`"]
        if summary:
            lines.append(summary)
        if data.get("next_action"):
            lines.append(f"Next: {data.get('next_action')}")
        if isinstance(data.get("manual_steps"), list) and data.get("manual_steps"):
            lines.append("Manual steps:")
            lines.extend(f"- {step}" for step in data.get("manual_steps", [])[:6])
        if tip:
            lines.append(f"Tip: {tip}")
        lines.append("Details:")
        lines.append(pretty)
        return "\n".join(lines)

    def handle_chat(self, message: str, session_id: str | None, use_tools: bool = True, confirmed: bool = False) -> dict:
        sid = memory_service.ensure_session(session_id)
        memory_service.add_message(sid, "user", message)

        steps: list[str] = []
        context = memory_service.recent_messages(sid, limit=8)
        steps.append("loaded_recent_memory")

        tool_name = None
        target = None
        tool_result = None

        confirmation = None
        requires_confirmation = False

        if use_tools:
            classification = operator_mode_service.classify_command(message)
            if classification.get("requires_confirmation") and not confirmed:
                requires_confirmation = True
                confirmation = classification
                reply = (
                    f"Approval required before JARVIS will run this command.\n"
                    f"Risk: {classification.get('risk')} ({classification.get('label')})\n"
                    f"Reason: {classification.get('reason')}"
                )
                model_name = "confirmation_gate"
                steps.append("confirmation_required")
                audit_service.log_event(
                    "confirmation_required",
                    {"session_id": sid, "message": message, "classification": classification},
                )
            else:
                tool_name, target, tool_result = self._handle_prefixed_tool(message, sid)
                if tool_name:
                    audit_service.log_event(
                        tool_name,
                        {"session_id": sid, "target": target, "result": tool_result},
                    )
                    steps.append(f"executed_{tool_name}")

        if not requires_confirmation:
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
                "requires_confirmation": requires_confirmation,
            },
        )

        return {
            "session_id": sid,
            "reply": reply,
            "steps": steps,
            "requires_confirmation": requires_confirmation,
            "confirmation": confirmation,
        }


orchestrator = Orchestrator()
