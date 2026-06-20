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
from app.services.memory import memory_service
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
        "  /wrappers             show wrapper status\n"
        "  /recipes              show wrapper recipes\n"
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
        "  app open: <name> [::: target]\n"
        "  app ensure: <name> [::: target]\n"
        "  app focus: <name> | app focusexact: <name>\n"
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
    wrappers_panel = Panel.fit(
        f"Wrappers online: {running_count}/{len(wrapper_items)}\n"
        f"Active wrapper(s): {', '.join(active_names) if active_names else 'none'}\n"
        f"Recipes: {app_wrapper_service.list_recipes().get('count', 0)}\n"
        f"Tools: {len(tool_registry.list_tools())}",
        title="Control Surface",
        border_style="magenta",
    )

    console.print(Columns([session_panel, wrappers_panel], equal=True))
    console.print(_wrapper_status_table())


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
    console.print("[dim]Tip: use /status, /wrappers, /recipes, or /tools for console panels.[/dim]")


@app.command()
def chat(message: str, session_id: Optional[str] = None) -> None:
    """Send one message to JARVIS from the terminal."""
    memory_service.initialize()
    task_service.initialize()
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
        if user_input in {"/exit", "exit", "quit"}:
            console.print("[bold yellow]Session ended.[/bold yellow]")
            break
        if user_input == "/help":
            _print_help()
            continue
        if user_input == "/status":
            _print_dashboard(sid)
            continue
        if user_input == "/wrappers":
            console.print(_wrapper_status_table())
            continue
        if user_input == "/recipes":
            console.print(_recipes_table())
            continue
        if user_input == "/tools":
            console.print(_tools_table())
            continue
        if user_input == "/clear":
            console.clear()
            _print_banner(sid)
            continue

        result = orchestrator.handle_chat(message=user_input, session_id=sid, use_tools=True)
        console.print(Panel(result["reply"], title="JARVIS"))
        console.print(f"[dim]steps: {', '.join(result['steps'])}[/dim]")


if __name__ == "__main__":
    app()
