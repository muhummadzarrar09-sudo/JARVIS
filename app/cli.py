from pathlib import Path
from typing import Optional

import typer
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from app.agents.orchestrator import orchestrator
from app.core.config import settings
from app.services.app_wrapper_service import app_wrapper_service
from app.services.audit import audit_service
from app.services.memory import memory_service
from app.services.operator_mode import operator_mode_service
from app.services.quick_actions_service import quick_actions_service
from app.services.task_service import task_service
from app.services.tool_registry import tool_registry

app = typer.Typer(help="JARVIS Local terminal interface")
console = Console()


def _command_help_text() -> str:
    return (
        "Commands:\n"
        "  /exit                 quit\n"
        "  /help                 show this help\n"
        "  /status               show JARVIS dashboard\n"
        "  /today                show a simple day brief\n"
        "  /wrappers             show wrapper status\n"
        "  /recipes              show wrapper recipes\n"
        "  /projects             show current project context\n"
        "  /doctor               show wrapper readiness diagnostics\n"
        "  /timeline             show recent session/action timeline\n"
        "  /replay               show replayable recent commands\n"
        "  /palette              show starter command palette\n"
        "  /starter              show beginner-friendly starter guide\n"
        "  /next                 show suggested next actions\n"
        "  /focus                show your current focus\n"
        "  /tasks                show open tasks\n"
        "  /work                 start the next task\n"
        "  /done                 finish the current task\n"
        "  /sessions             show recent sessions\n"
        "  /use <session_id>     switch to a recent session (full id, short id, or list number)\n"
        "  /resume               switch to the most recent other session\n"
        "  /find <text>          search beginner commands\n"
        "  /do <goal>            run a simple natural-language goal\n"
        "  /tools                show tool registry summary\n"
        "  /clear                clear terminal\n"
        "  shell: <command>      run a shell command\n"
        "  fs list: <path>       list files\n"
        "  fs read: <path>       read a text file\n"
        "  fs write: <path> ::: <content>   write file\n"
        "  fs append: <path> ::: <content>  append file\n"
        "  fs mkdir: <path>      create directory\n"
        "  browser start         start Playwright browser\n"
        "  browser state         current browser session state\n"
        "  browser open: <url>   open a page\n"
        "  browser title         get current page title\n"
        "  browser text          snapshot visible page text\n"
        "  browser inspect: <selector>\n"
        "  browser click: <selector>   or browser click <visible text>\n"
        "  browser forceclick: <selector>\n"
        "  browser fill: <selector> ::: <text>\n"
        "  browser press: <selector> ::: <key>\n"
        "  browser screenshot: <path>\n"
        "  browser back | browser forward | browser close\n"
        "  app wrappers | app recipes | app status[: <name>] | app state[: <name>]\n"
        "  app doctor[: <name>] | app diagnose[: <name>]\n"
        "  app project[: <path>] | app context[: <path>]\n"
        "  app resume recipes: vscode.resume | browser.resume | project.resume\n"
        "  app open: <name> [::: target]\n"
        "  app ensure: <name> [::: target]\n"
        "  app focus: <name> | app focusexact: <name>\n"
        "  app reset[: <name>|all]\n"
        "  app recipe: <name> [::: payload]\n"
        "  app note: <text>\n"
        "  app explore: <path> | app code: <path> | app browse: <url>\n"
        "  desktop windows | desktop active | desktop screen\n"
        "  desktop focus: <title> | desktop focusexact: <title>\n"
        "  desktop type: <text> | desktop write: <text>\n"
        "  desktop press: <key> | desktop hotkey: ctrl+shift+t\n"
        "  desktop click: x,y [::: right]\n"
        "  desktop screenshot[: <path>]\n"
        "  proc list | proc list: <name>\n"
        "  proc windows\n"
        "  proc start: <command>\n"
        "  proc kill: <pid-or-image>\n"
        "  checkpoint create[: note] | checkpoint get\n"
        "  task create: <title>\n"
        "  task list | task open\n"
        "  task done: <id> | task reopen: <id>\n"
        "  session list | session overview\n"
    )


def _print_help() -> None:
    console.print(Panel.fit(_command_help_text(), title="JARVIS Commands"))


def _wrapper_status_table() -> Table:
    table = Table(title="Wrapper Status", show_lines=False)
    table.add_column("Wrapper", style="cyan")
    table.add_column("Running")
    table.add_column("Active")
    table.add_column("Matches")
    table.add_column("Remembered Target", style="magenta")
    table.add_column("Hint", style="dim")

    status = app_wrapper_service.wrapper_status()
    items = status.get("items", []) if status.get("ok") else []
    for item in items:
        remembered = item.get("remembered_state", {}) or {}
        target = remembered.get("last_target") or remembered.get("last_path") or remembered.get("last_url") or ""
        table.add_row(
            item.get("name", "?"),
            "yes" if item.get("running") else "no",
            "yes" if item.get("active") else "no",
            str(item.get("match_count", 0)),
            str(target)[:40],
            item.get("title_hint", ""),
        )
    if not items:
        table.add_row("(unavailable)", "-", "-", "-", "-", status.get("error", "no wrapper data"))
    return table


def _recipes_table() -> Table:
    table = Table(title="App Recipes", show_lines=False)
    table.add_column("Recipe", style="magenta")
    table.add_column("Inputs")
    table.add_column("Risk")
    table.add_column("Notes", style="dim")

    recipes = app_wrapper_service.list_recipes().get("items", [])
    for item in recipes:
        table.add_row(
            item.get("name", "?"),
            ", ".join(item.get("inputs", [])),
            item.get("risk", "?"),
            item.get("notes", ""),
        )
    return table


def _tools_table() -> Table:
    table = Table(title="Tool Registry", show_lines=False)
    table.add_column("Tool", style="green")
    table.add_column("Phase")
    table.add_column("Risk")
    table.add_column("Category")

    for item in tool_registry.list_tools():
        table.add_row(
            item.get("name", "?"),
            str(item.get("phase", "?")),
            item.get("risk", "?"),
            item.get("category", "?"),
        )
    return table


def _tasks_table(limit: int = 8) -> Table:
    table = Table(title="Open / In-Progress Tasks", show_lines=False)
    table.add_column("ID", style="yellow")
    table.add_column("Title", style="white")
    table.add_column("Priority", style="magenta")
    table.add_column("Updated", style="dim")

    items = [item for item in task_service.list_tasks(status=None, limit=limit * 2) if item.get('status') in {'open', 'in_progress'}][:limit]
    for item in items:
        label = item.get("title", "")
        if item.get("status") == "in_progress":
            label = f"▶ {label}"
        table.add_row(str(item.get("id", "?")), label, item.get("priority", "normal"), str(item.get("updated_at", ""))[-8:])
    if not items:
        table.add_row("-", "No open tasks", "-", "-")
    return table


def _sessions_table(current_session_id: str, limit: int = 8) -> Table:
    table = Table(title="Recent Sessions", show_lines=False)
    table.add_column("#", style="yellow")
    table.add_column("Current")
    table.add_column("Session", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Msgs", style="yellow")
    table.add_column("Use", style="dim")

    items = memory_service.list_sessions(limit=limit)
    for idx, item in enumerate(items, start=1):
        short_id = item.get("session_id", "")[:8]
        table.add_row(
            str(idx),
            "●" if item.get("session_id") == current_session_id else "",
            short_id,
            item.get("title", ""),
            str(item.get("message_count", 0)),
            f"/use {idx} or /use {short_id}",
        )
    if not items:
        table.add_row("-", "", "-", "No sessions", "-", "-")
    return table


def _doctor_table() -> Table:
    table = Table(title="Wrapper Doctor", show_lines=False)
    table.add_column("Wrapper", style="yellow")
    table.add_column("Ready")
    table.add_column("Binary/Context", style="magenta")
    table.add_column("Notes", style="dim")

    doctor = app_wrapper_service.wrapper_doctor()
    items = doctor.get("items", []) if doctor.get("ok") else []
    for item in items:
        context = item.get("binary") or ((item.get("context") or {}).get("url") if isinstance(item.get("context"), dict) else "") or ""
        table.add_row(
            item.get("name", "?"),
            "yes" if item.get("ready") else "no",
            str(context)[:40],
            item.get("notes", ""),
        )
    if not items:
        table.add_row("(unavailable)", "-", "-", doctor.get("error", "no diagnostics"))
    return table


def _replay_table(session_id: str, limit: int = 10) -> Table:
    table = Table(title="Replay Candidates", show_lines=False)
    table.add_column("Risk", style="red")
    table.add_column("Command", style="cyan")
    table.add_column("Event", style="dim")

    items = audit_service.replay_candidates(session_id=session_id, limit=limit)
    for item in items:
        table.add_row(item.get("risk", "?"), item.get("command", ""), item.get("event_type", ""))
    if not items:
        table.add_row("-", "No replay candidates yet", "-")
    return table


def _palette_panel() -> Panel:
    palette = operator_mode_service.palette()
    blocks = []
    for item in palette:
        commands = "\n".join(f"• {cmd}" for cmd in item.get("commands", []))
        blocks.append(f"[bold]{item.get('category')}[/bold]\n{commands}")
    return Panel.fit("\n\n".join(blocks), title="Command Palette", border_style="blue")


def _search_panel(query: str) -> Panel:
    results = quick_actions_service.search(query)
    if not results.get("ok"):
        return Panel.fit(results.get("error", "No matches"), title="Command Search", border_style="yellow")
    if not results.get("items"):
        return Panel.fit(f"No beginner commands matched: {query}", title="Command Search", border_style="yellow")
    body = "\n\n".join(
        f"[bold]{item.get('category')}[/bold]\n• {item.get('say')} — {item.get('does')}"
        for item in results.get("items", [])[:8]
    )
    return Panel.fit(body, title=f"Command Search: {query}", border_style="green")


def _next_steps_panel() -> Panel:
    steps = quick_actions_service.next_steps().get("items", [])
    body = "\n".join(f"• {item}" for item in steps) if steps else "No next steps available."
    return Panel.fit(body, title="Suggested Next Actions", border_style="bright_green")


def _today_panel() -> Panel:
    today = quick_actions_service.today_brief()
    if not today.get("ok"):
        return Panel.fit("No day brief available.", title="Today", border_style="yellow")
    lines = [today.get("headline") or "Today"]
    task_summary = today.get("task_summary", {})
    if task_summary:
        lines.append(f"Tasks — open: {task_summary.get('open', 0)}, in progress: {task_summary.get('in_progress', 0)}, done: {task_summary.get('done', 0)}")
    browser = today.get("browser", {})
    if browser:
        if browser.get("started"):
            lines.append(f"Browser: {browser.get('title') or browser.get('url')}")
        elif browser.get("remembered_url"):
            lines.append(f"Last browser page: {browser.get('remembered_url')}")
    next_steps = today.get("next_steps", [])[:4]
    if next_steps:
        lines.append("")
        lines.append("Try next:")
        lines.extend(f"• {item}" for item in next_steps)
    return Panel.fit("\n".join(lines), title="Today Brief", border_style="bright_cyan")


def _focus_panel() -> Panel:
    focus = quick_actions_service.focus()
    if not focus.get("ok"):
        return Panel.fit("No current focus available.", title="Current Focus", border_style="yellow")
    lines = [focus.get("headline", "Current Focus")]
    if focus.get("project_path"):
        lines.append(f"Project: {focus.get('project_path')}")
    recs = focus.get("recommended", [])[:4]
    if recs:
        lines.append("")
        lines.append("Try next:")
        lines.extend(f"• {item}" for item in recs)
    return Panel.fit("\n".join(lines), title="Current Focus", border_style="bright_magenta")


def _starter_panel() -> Panel:
    guide = quick_actions_service.guide()
    blocks = []
    for category in guide.get("categories", []):
        items = "\n".join(
            f"• [bold]{item.get('say')}[/bold] — {item.get('does')}"
            for item in category.get("items", [])
        )
        blocks.append(f"[bold]{category.get('name')}[/bold]\n{items}")
    return Panel.fit("\n\n".join(blocks), title=guide.get("title", "Starter Guide"), border_style="bright_green")


def _project_context_panel() -> Panel:
    context = app_wrapper_service.current_project_context(None)
    if not context.get("ok"):
        return Panel.fit(
            context.get("error", "project context unavailable"),
            title="Project Context",
            border_style="yellow",
        )

    summary = context.get("summary", {})
    project_type = ", ".join(summary.get("project_type", []))
    markers = ", ".join(item.get("name", "") for item in summary.get("markers", [])[:6]) or "none"
    recipes = ", ".join(context.get("recommended_recipes", [])[:5])
    body = (
        f"Path: {context.get('path')}\n"
        f"Type: {project_type}\n"
        f"Markers: {markers}\n"
        f"README: {summary.get('readme') or 'none'}\n"
        f"Suggested: {recipes}"
    )
    return Panel.fit(body, title="Project Context", border_style="green")


def _timeline_table(session_id: str, limit: int = 12) -> Table:
    table = Table(title="Recent Timeline", show_lines=False)
    table.add_column("Event", style="cyan")
    table.add_column("Preview", style="white")
    table.add_column("At", style="dim")

    for item in audit_service.timeline(session_id=session_id, limit=limit):
        table.add_row(
            item.get("event_type", "?"),
            item.get("preview", "")[:80],
            (item.get("ts") or "")[-14:-6] if item.get("ts") else "",
        )
    return table


def _print_dashboard(session_id: str) -> None:
    session = memory_service.session_overview(session_id)
    open_tasks = task_service.list_tasks(status="open", limit=5)
    wrappers = app_wrapper_service.wrapper_status()

    session_panel = Panel.fit(
        f"Session: {session_id}\n"
        f"Provider: {settings.default_model_provider}\n"
        f"Messages: {session.get('message_count', 0)}\n"
        f"Open tasks: {len(open_tasks)}\n"
        f"Workspace: {Path(settings.workspace_root).resolve()}",
        title="JARVIS Console",
        border_style="cyan",
    )

    wrapper_items = wrappers.get("items", []) if wrappers.get("ok") else []
    running_count = sum(1 for item in wrapper_items if item.get("running"))
    active_names = [item.get("name") for item in wrapper_items if item.get("active")]
    doctor = app_wrapper_service.wrapper_doctor()
    ready_count = sum(1 for item in doctor.get("items", []) if item.get("ready")) if doctor.get("ok") else 0
    wrappers_panel = Panel.fit(
        f"Wrappers online: {running_count}/{len(wrapper_items)}\n"
        f"Active wrapper(s): {', '.join(active_names) if active_names else 'none'}\n"
        f"Ready wrappers: {ready_count}/{len(doctor.get('items', [])) if doctor.get('ok') else 0}\n"
        f"Recipes: {app_wrapper_service.list_recipes().get('count', 0)}\n"
        f"Tools: {len(tool_registry.list_tools())}",
        title="Control Surface",
        border_style="magenta",
    )

    console.print(Columns([session_panel, wrappers_panel, _project_context_panel()], equal=True))
    console.print(_wrapper_status_table())
    console.print(Columns([_tasks_table(limit=6), _sessions_table(current_session_id=session_id, limit=6)], equal=True))
    console.print(_timeline_table(session_id=session_id, limit=8))


def _print_banner(session_id: str) -> None:
    console.print(
        Panel.fit(
            "JARVIS Console\n"
            "Claude-Code-style terminal vibe, but tailored for multi-tool local control.",
            title="JARVIS Local",
            border_style="bright_blue",
        )
    )
    _print_dashboard(session_id)
    console.print("[dim]Tip: use /starter, /today, /next, /focus, /status, /wrappers, /recipes, /projects, /doctor, /timeline, /replay, /palette, /tasks, /sessions, or /tools for console panels.[/dim]")


def _approve_if_needed(user_input: str) -> bool:
    info = operator_mode_service.classify_command(user_input)
    if not info.get("requires_confirmation"):
        return True
    console.print(
        Panel.fit(
            f"Risk: {info.get('risk')}\n"
            f"Label: {info.get('label')}\n"
            f"Reason: {info.get('reason')}\n"
            "Confirm execution? type YES to continue.",
            title="Approval Required",
            border_style="red",
        )
    )
    response = console.input("[bold red]confirm> [/bold red]").strip()
    return response == "YES"


@app.command()
def chat(message: str, session_id: Optional[str] = None) -> None:
    """Send one message to JARVIS from the terminal."""
    memory_service.initialize()
    task_service.initialize()
    if not _approve_if_needed(message):
        console.print("[yellow]Command cancelled.[/yellow]")
        return
    result = orchestrator.handle_chat(message=message, session_id=session_id, use_tools=True)
    console.print(Panel(result["reply"], title=f"JARVIS • session {result['session_id']}"))
    console.print(f"[dim]steps: {', '.join(result['steps'])}[/dim]")


@app.command()
def repl(session_id: Optional[str] = None) -> None:
    """Start an interactive JARVIS terminal session."""
    memory_service.initialize()
    task_service.initialize()
    sid = memory_service.ensure_session(session_id)
    _print_banner(sid)
    _print_help()

    while True:
        try:
            user_input = console.input("[bold cyan]jarvis> [/bold cyan]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[bold yellow]Exiting JARVIS terminal.[/bold yellow]")
            break

        if not user_input:
            continue
        lowered_input = user_input.lower()
        if user_input in {"/exit", "exit", "quit"}:
            console.print("[bold yellow]Session ended.[/bold yellow]")
            break
        if user_input == "/help":
            _print_help()
            continue
        if user_input == "/status":
            _print_dashboard(sid)
            continue
        if user_input == "/today":
            console.print(_today_panel())
            continue
        if user_input == "/wrappers":
            console.print(_wrapper_status_table())
            continue
        if user_input == "/recipes":
            console.print(_recipes_table())
            continue
        if user_input == "/projects":
            console.print(_project_context_panel())
            continue
        if user_input == "/doctor":
            console.print(_doctor_table())
            continue
        if user_input == "/timeline":
            console.print(_timeline_table(session_id=sid, limit=20))
            continue
        if user_input == "/replay":
            console.print(_replay_table(session_id=sid, limit=12))
            continue
        if user_input == "/palette":
            console.print(_palette_panel())
            continue
        if user_input == "/starter":
            console.print(_starter_panel())
            continue
        if user_input == "/next":
            console.print(_next_steps_panel())
            continue
        if user_input == "/focus":
            console.print(_focus_panel())
            continue
        if user_input == "/tasks":
            console.print(_tasks_table(limit=12))
            continue
        if user_input == "/work":
            user_input = "work on next task"
            lowered_input = user_input.lower()
        if user_input == "/done":
            user_input = "complete current task"
            lowered_input = user_input.lower()
        if user_input == "/sessions":
            console.print(_sessions_table(current_session_id=sid, limit=12))
            continue
        if user_input in {"/resume", "resume last session", "switch to last session"}:
            sessions = memory_service.list_sessions(limit=3)
            target = next((item.get("session_id") for item in sessions if item.get("session_id") != sid), None)
            if target:
                sid = target
                console.print(f"[green]Resumed recent session {sid}[/green]")
                console.print(_project_context_panel())
            else:
                console.print("[yellow]No other recent session to resume.[/yellow]")
            continue
        if user_input.startswith("/use ") or lowered_input.startswith("switch to session "):
            candidate = user_input[5:].strip() if user_input.startswith("/use ") else user_input[len("switch to session "):].strip()
            resolved = None
            if candidate.isdigit():
                index = int(candidate)
                sessions = memory_service.list_sessions(limit=20)
                if 1 <= index <= len(sessions):
                    resolved = sessions[index - 1].get("session_id")
            else:
                resolved = memory_service.resolve_session_id(candidate)
            overview = memory_service.session_overview(resolved) if resolved else {"ok": False}
            if overview.get("ok"):
                sid = resolved
                console.print(f"[green]Switched to session {sid}[/green]")
                console.print(_project_context_panel())
            else:
                console.print(f"[yellow]Session not found: {candidate}[/yellow]")
            continue
        if user_input.startswith("/find "):
            query = user_input[6:].strip()
            console.print(_search_panel(query))
            continue
        if user_input.startswith("/do "):
            user_input = user_input[4:].strip()
            if not user_input:
                console.print("[yellow]Tell JARVIS what you want after /do[/yellow]")
                continue
        if user_input == "/tools":
            console.print(_tools_table())
            continue
        if user_input == "/clear":
            console.clear()
            _print_banner(sid)
            continue

        if not _approve_if_needed(user_input):
            console.print("[yellow]Command cancelled.[/yellow]")
            continue

        result = orchestrator.handle_chat(message=user_input, session_id=sid, use_tools=True)
        console.print(Panel(result["reply"], title="JARVIS"))
        console.print(f"[dim]steps: {', '.join(result['steps'])}[/dim]")


if __name__ == "__main__":
    app()
