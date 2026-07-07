from bravo1.config import Settings
from bravo1.core.operator import Operator


def test_operator_scaffold_runs(tmp_path):
    data_dir = tmp_path / "data"
    settings = Settings(
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
    )
    operator = Operator(settings)
    result = operator.handle("what should i do now")
    assert result["ok"] is True
    assert result["primary_action"]
