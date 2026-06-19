from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from app.agents.orchestrator import orchestrator
from app.services.memory import memory_service

app = typer.Typer(help="JARVIS Local terminal interface")
console = Console()


def _print_help() -> None:
    console.print(
        Panel.fit(
            "Commands:\n"
            "  /exit                 quit\n"
            "  /help                 show this help\n"
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
            "  browser click: <selector>\n"
            "  browser fill: <selector> ::: <text>\n"
            "  browser press: <selector> ::: <key>\n"
            "  browser screenshot: <path>\n"
            "  browser back | browser forward | browser close\n",
            title="JARVIS Commands",
        )
    )


@app.command()
def chat(message: str, session_id: Optional[str] = None) -> None:
    """Send one message to JARVIS from the terminal."""
    memory_service.initialize()
    result = orchestrator.handle_chat(message=message, session_id=session_id, use_tools=True)
    console.print(Panel(result["reply"], title=f"JARVIS • session {result['session_id']}"))
    console.print(f"[dim]steps: {', '.join(result['steps'])}[/dim]")


@app.command()
def repl(session_id: Optional[str] = None) -> None:
    """Start an interactive JARVIS terminal session."""
    memory_service.initialize()
    sid = memory_service.ensure_session(session_id)
    console.print(Panel.fit(f"JARVIS terminal started\nSession: {sid}", title="JARVIS Local"))
    _print_help()

    while True:
        try:
            user_input = console.input("[bold cyan]you> [/bold cyan]").strip()
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

        result = orchestrator.handle_chat(message=user_input, session_id=sid, use_tools=True)
        console.print(Panel(result["reply"], title="JARVIS"))
        console.print(f"[dim]steps: {', '.join(result['steps'])}[/dim]")


if __name__ == "__main__":
    app()
