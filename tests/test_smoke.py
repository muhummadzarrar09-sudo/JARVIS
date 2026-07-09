from pathlib import Path

from bravo1.adapters.browser import BrowserAdapter
from bravo1.config import Settings
from bravo1.core.operator import Operator
from bravo1.models.runtime import RuntimeBootstrap


def build_settings(tmp_path):
    data_dir = tmp_path / "data"
    return Settings(
        app_name="BRAVO-1",
        data_dir=data_dir,
        brain_dir=data_dir / "brain",
        session_dir=data_dir / "sessions",
        summary_dir=data_dir / "summaries",
        fast_model="fast.gguf",
        main_model="main.gguf",
        runtime_host="127.0.0.1",
        runtime_fast_port=8080,
        runtime_main_port=8081,
        runtime_profile="auto",
        shell_timeout_seconds=20,
        model_request_timeout_seconds=1,
        browser_fetch_timeout_seconds=2,
        auto_summary_message_interval=4,
    )


def test_operator_scaffold_runs(tmp_path):
    operator = Operator(build_settings(tmp_path))
    result = operator.handle("what should i do now")
    assert result["ok"] is True
    assert result["primary_action"]
    assert "Primary action" in result["reply"]
    assert result["kind"] == "chat"
    assert "data" in result


def test_slash_commands_and_summary(tmp_path):
    operator = Operator(build_settings(tmp_path))

    help_result = operator.handle("/help")
    assert help_result["ok"] is True
    assert "/brief" in help_result["reply"]

    operator.handle("/setgoal wire the model runtime")
    brief_result = operator.handle("/brief")
    assert "wire the model runtime" in brief_result["reply"]

    project_result = operator.handle("/project BRAVO-1 rebuild")
    assert "Project set" in project_result["reply"]

    project_inspect = operator.handle("/tool project.inspect")
    assert "BRAVO-1 rebuild" in project_inspect["reply"]

    tool_result = operator.handle("/tool runtime.inspect")
    assert "fast.gguf" in tool_result["reply"]

    browser_tool_result = operator.handle("/tool browser.inspect")
    assert "Browser status" in browser_tool_result["reply"] or "Tool result: browser.inspect" in browser_tool_result["reply"]

    run_result = operator.handle("/run echo bravo1")
    assert "bravo1" in run_result["reply"].lower()

    capture_result = operator.handle("/note remember the web shell bootstrap")
    assert "remember the web shell bootstrap" in capture_result["reply"].lower()

    browser_result = operator.handle("/browser https://example.com")
    assert "Opened browser URL" in browser_result["reply"] or "Browser action failed" in browser_result["reply"]

    browser_status = operator.handle("/browser-status")
    assert "Browser status" in browser_status["reply"]

    controlled_browser = operator.handle("/browser-controlled https://example.com")
    assert "Browser action failed" in controlled_browser["reply"] or "Opened browser URL" in controlled_browser["reply"]

    html_path = tmp_path / "browser-page.html"
    html_path.write_text("<html><head><title>Bravo Fetch</title></head><body><p>fetch works</p></body></html>", encoding="utf-8")
    browser_fetch = operator.handle(f"/browser-fetch {html_path.as_uri()}")
    assert "Browser fetch" in browser_fetch["reply"]
    assert "Bravo Fetch" in browser_fetch["reply"]

    windows_status = operator.handle("/windows-status")
    assert "Windows adapter status" in windows_status["reply"]

    windows_active = operator.handle("/windows-active")
    assert "Windows active window" in windows_active["reply"] or "Windows active-window check failed" in windows_active["reply"] or "no active titled window" in windows_active["reply"]

    windows_find = operator.handle("/windows-find code")
    assert "Window search" in windows_find["reply"] or "Window search failed" in windows_find["reply"]

    health_result = operator.handle("/web-health")
    assert "Runtime reachability" in health_result["reply"]

    state_snapshot = operator.state_snapshot()
    assert state_snapshot["ok"] is True
    assert (build_settings(tmp_path).data_dir / "app_state.json").exists()

    summary_result = operator.handle("/summarize")
    assert "Session summary written" in summary_result["reply"]
    summary_path = Path(summary_result["reply"].split(": ", 1)[1])
    assert summary_path.exists()


def test_runtime_status_shapes(tmp_path):
    settings = build_settings(tmp_path)
    runtime = RuntimeBootstrap(settings)
    status = runtime.status()
    assert status["ok"] is True
    assert status["fast"]["endpoint"].endswith("/v1/chat/completions")
    assert "health" in status["fast"]
    assert "health" in status["main"]


def test_browser_fetch_snapshot(tmp_path):
    adapter = BrowserAdapter(tmp_path / "browser", fetch_timeout_seconds=2)
    html_path = tmp_path / "page.html"
    html_path.write_text("<html><head><title>Bravo Page</title></head><body><h1>Hello</h1><p>World</p></body></html>", encoding="utf-8")
    result = adapter.fetch_page(html_path.as_uri())
    assert result["ok"] is True
    assert result["title"] == "Bravo Page"
    assert "Hello World" in result["text"]

    controlled = adapter.open_url_controlled("https://example.com")
    assert controlled["ok"] is False
    assert controlled["mode"] == "controlled"
