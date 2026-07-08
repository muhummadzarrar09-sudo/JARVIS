from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from bravo1.config import Settings
from bravo1.core.operator import Operator


class _WebHandler(BaseHTTPRequestHandler):
    operator: Operator
    shell_html: str

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_html(self, html: str) -> None:
        data = html.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in {"/", "/index.html"}:
            self._send_html(self.shell_html)
            return
        if self.path == "/api/health":
            self._send_json({"ok": True, "app": "BRAVO-1 web shell bootstrap", "status": "ok"})
            return
        if self.path == "/api/runtime":
            self._send_json(self.operator.runtime.status())
            return
        self._send_json({"ok": False, "error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/chat":
            self._send_json({"ok": False, "error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            self._send_json({"ok": False, "error": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
            return
        message = str(payload.get("message") or "").strip()
        if not message:
            self._send_json({"ok": False, "error": "Message is required"}, status=HTTPStatus.BAD_REQUEST)
            return
        self._send_json(self.operator.handle(message))

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


def _shell_html_path() -> Path:
    return Path(__file__).resolve().parents[2] / "shell" / "web" / "index.html"


def serve_web_shell(host: str = "127.0.0.1", port: int = 8011) -> None:
    settings = Settings.load()
    operator = Operator(settings)
    shell_path = _shell_html_path()
    shell_html = shell_path.read_text(encoding="utf-8") if shell_path.exists() else "<h1>BRAVO-1 shell missing</h1>"

    handler_class = type(
        "BRAVO1WebHandler",
        (_WebHandler,),
        {"operator": operator, "shell_html": shell_html},
    )
    server = ThreadingHTTPServer((host, port), handler_class)
    print(f"BRAVO-1 web shell bootstrap running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
