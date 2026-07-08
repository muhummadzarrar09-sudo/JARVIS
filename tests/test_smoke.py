from pathlib import Path

from bravo1.config import Settings
from bravo1.core.operator import Operator


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
        shell_timeout_seconds=20,
        model_request_timeout_seconds=1,
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

    run_result = operator.handle("/run echo bravo1")
    assert "bravo1" in run_result["reply"].lower()

    capture_result = operator.handle("/note remember the web shell bootstrap")
    assert "remember the web shell bootstrap" in capture_result["reply"].lower()

    health_result = operator.handle("/web-health")
    assert "Runtime reachability" in health_result["reply"]

    summary_result = operator.handle("/summarize")
    assert "Session summary written" in summary_result["reply"]
    summary_path = Path(summary_result["reply"].split(": ", 1)[1])
    assert summary_path.exists()
