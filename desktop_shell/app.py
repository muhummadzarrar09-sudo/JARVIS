from __future__ import annotations

import argparse
import json
import socket
import threading
import time
import webbrowser
from urllib.error import URLError
from urllib.request import urlopen

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


def _start_uvicorn(host: str, port: int) -> None:
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="warning",
    )


def _fetch_json(url: str, timeout: float = 5.0) -> dict | None:
    try:
        with urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


def _startup_diagnostics(base_url: str) -> dict[str, object]:
    health = _fetch_json(f"{base_url}/health")
    validation = _fetch_json(f"{base_url}/validation/report")
    models = _fetch_json(f"{base_url}/models/status")
    database = _fetch_json(f"{base_url}/database/status")
    audit = _fetch_json(f"{base_url}/audit/status")
    return {
        "health": health,
        "validation": validation,
        "models": models,
        "database": database,
        "audit": audit,
    }


def _print_startup_diagnostics(base_url: str) -> None:
    diagnostics = _startup_diagnostics(base_url)
    print("JARVIS shell startup diagnostics:")
    print(json.dumps(diagnostics, indent=2))


def _wait_for_http_ready(base_url: str, path: str, retry_count: int, retry_delay: float) -> bool:
    for _ in range(max(1, retry_count)):
        health = _fetch_json(f"{base_url}/health", timeout=3.0)
        if isinstance(health, dict) and health.get("status") == "ok":
            try:
                with urlopen(f"{base_url}{path}", timeout=3.0) as response:
                    if response.status == 200:
                        return True
            except Exception:
                pass
        time.sleep(max(0.1, retry_delay))
    return False


def _keep_alive() -> None:
    try:
        input("Press Enter to exit the shell launcher...")
    except EOFError:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch the JARVIS packaged shell starter")
    parser.add_argument("--host", default=settings.app_host)
    parser.add_argument("--port", type=int, default=settings.app_port)
    parser.add_argument("--path", default="/ui/app-shell")
    parser.add_argument("--browser-only", action="store_true", help="Skip pywebview and open the shell in the system browser.")
    parser.add_argument("--startup-timeout", type=float, default=15.0)
    parser.add_argument("--print-diagnostics", action="store_true", help="Print startup health/validation/model diagnostics before opening the shell.")
    parser.add_argument("--retry-count", type=int, default=8, help="How many HTTP readiness retries to perform after the server port opens.")
    parser.add_argument("--retry-delay", type=float, default=1.0, help="Delay between HTTP readiness retries.")
    parser.add_argument("--open-recovery-on-failure", action="store_true", help="Open the browser shell URL even if readiness checks fail, so you can inspect recovery behavior manually.")
    args = parser.parse_args()

    server_thread = threading.Thread(target=_start_uvicorn, args=(args.host, args.port), daemon=True)
    server_thread.start()

    base_url = f"http://{args.host}:{args.port}"
    url = f"{base_url}{args.path}"
    if not _wait_for_port(args.host, args.port, timeout=args.startup_timeout):
        raise RuntimeError("Local JARVIS server did not start in time.")

    ready = _wait_for_http_ready(base_url, args.path, retry_count=args.retry_count, retry_delay=args.retry_delay)

    if args.print_diagnostics:
        _print_startup_diagnostics(base_url)

    if not ready and args.open_recovery_on_failure:
        webbrowser.open(url)
        print(f"JARVIS HTTP readiness checks failed, but recovery mode opened the shell URL in your browser: {url}")
        _keep_alive()
        return
    if not ready:
        raise RuntimeError("Local JARVIS HTTP readiness checks did not pass in time.")

    if args.browser_only:
        webbrowser.open(url)
        print(f"Opened JARVIS Shell in your browser: {url}")
        _keep_alive()
        return

    try:
        import webview  # type: ignore

        webview.create_window("JARVIS Shell", url, width=1600, height=980)
        webview.start()
    except Exception as e:
        webbrowser.open(url)
        print(f"PyWebView launch failed ({e}). Falling back to your browser: {url}")
        _keep_alive()


if __name__ == "__main__":
    main()
