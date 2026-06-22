from __future__ import annotations

import socket
import threading
import time
import webbrowser

from app.core.config import settings


def _wait_for_port(host: str, port: int, timeout: float = 15.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            try:
                sock.connect((host, port))
                return True
            except OSError:
                time.sleep(0.2)
    return False


def _start_uvicorn() -> None:
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=False,
        log_level="warning",
    )


def main() -> None:
    server_thread = threading.Thread(target=_start_uvicorn, daemon=True)
    server_thread.start()

    host = settings.app_host
    port = settings.app_port
    url = f"http://{host}:{port}/ui/app-shell"

    if not _wait_for_port(host, port):
        raise RuntimeError("Local JARVIS server did not start in time.")

    try:
        import webview  # type: ignore

        webview.create_window("JARVIS Shell", url, width=1600, height=980)
        webview.start()
    except Exception:
        webbrowser.open(url)
        print(f"Opened JARVIS Shell in your browser: {url}")
        input("Press Enter to exit the shell launcher...")


if __name__ == "__main__":
    main()
