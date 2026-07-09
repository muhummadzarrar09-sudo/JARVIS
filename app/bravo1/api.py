from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from bravo1.app import build_operator
from bravo1.core.operator import Operator


class _APIHandler(BaseHTTPRequestHandler):
    operator: Operator

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw)

    def do_GET(self) -> None:  # noqa: N802
        state = self.operator.sessions.load()
        if self.path == "/health":
            self._send_json({"ok": True, "app": "BRAVO-1 API", "status": "ok"})
            return
        if self.path == "/runtime":
            self._send_json(self.operator.runtime.status())
            return
        if self.path == "/state":
            self._send_json(self.operator.state_snapshot())
            return
        if self.path == "/session":
            self._send_json({"ok": True, "session": self.operator.sessions.snapshot(state)})
            return
        if self.path == "/brief":
            self._send_json(self.operator.handle("/brief"))
            return
        if self.path == "/project":
            self._send_json(self.operator.handle("/project"))
            return
        if self.path == "/captures":
            self._send_json(self.operator.handle("/captures"))
            return
        if self.path == "/tools":
            self._send_json(self.operator.handle("/tools"))
            return
        if self.path == "/browser":
            self._send_json(self.operator.handle("/browser-status"))
            return
        if self.path == "/windows":
            self._send_json(self.operator.handle("/windows-status"))
            return
        self._send_json({"ok": False, "error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/chat":
            try:
                payload = self._read_json()
            except json.JSONDecodeError:
                self._send_json({"ok": False, "error": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
                return
            message = str(payload.get("message") or "").strip()
            if not message:
                self._send_json({"ok": False, "error": "Message is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json(self.operator.handle(message))
            return

        try:
            payload = self._read_json()
        except json.JSONDecodeError:
            payload = {}

        if self.path == "/browser/open":
            url = str(payload.get("url") or "").strip()
            self._send_json(self.operator.handle(f"/browser {url}" if url else "/browser"))
            return
        if self.path == "/browser/open-controlled":
            url = str(payload.get("url") or "").strip()
            self._send_json(self.operator.handle(f"/browser-controlled {url}" if url else "/browser-status"))
            return
        if self.path == "/browser/fetch":
            url = str(payload.get("url") or "").strip()
            self._send_json(self.operator.handle(f"/browser-fetch {url}" if url else "/browser-fetch"))
            return
        if self.path == "/windows/find":
            query = str(payload.get("query") or "").strip()
            self._send_json(self.operator.handle(f"/windows-find {query}" if query else "/windows-status"))
            return
        if self.path == "/windows/focus":
            title = str(payload.get("title") or "").strip()
            self._send_json(self.operator.handle(f"/windows-focus {title}" if title else "/windows-status"))
            return
        if self.path == "/shell/run":
            command = str(payload.get("command") or "").strip()
            self._send_json(self.operator.handle(f"/run {command}" if command else "/help"))
            return
        if self.path == "/runtime/start":
            lane = str(payload.get("lane") or "fast")
            self._send_json(self.operator.runtime.launch(lane))
            return
        if self.path == "/runtime/stop":
            lane = str(payload.get("lane") or "fast")
            self._send_json(self.operator.runtime.stop(lane))
            return
        if self.path == "/summarize":
            self._send_json(self.operator.handle("/summarize"))
            return
        self._send_json({"ok": False, "error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


def serve_api(host: str = "127.0.0.1", port: int = 8000) -> None:
    operator = build_operator()
    handler_class = type("BRAVO1APIHandler", (_APIHandler,), {"operator": operator})
    server = ThreadingHTTPServer((host, port), handler_class)
    print(f"BRAVO-1 API running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
