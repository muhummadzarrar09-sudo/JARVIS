from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    app_name: str
    data_dir: Path
    brain_dir: Path
    session_dir: Path
    summary_dir: Path
    fast_model: str
    main_model: str
    runtime_host: str
    runtime_fast_port: int
    runtime_main_port: int
    runtime_profile: str
    shell_timeout_seconds: int
    model_request_timeout_seconds: int
    browser_fetch_timeout_seconds: int
    auto_summary_message_interval: int

    @classmethod
    def load(cls) -> "Settings":
        data_dir = Path(os.getenv("BRAVO1_DATA_DIR", "./data")).resolve()
        brain_dir = Path(os.getenv("BRAVO1_BRAIN_DIR", str(data_dir / "brain"))).resolve()
        session_dir = Path(os.getenv("BRAVO1_SESSION_DIR", str(data_dir / "sessions"))).resolve()
        summary_dir = Path(os.getenv("BRAVO1_SUMMARY_DIR", str(data_dir / "summaries"))).resolve()
        return cls(
            app_name=os.getenv("BRAVO1_APP_NAME", "BRAVO-1"),
            data_dir=data_dir,
            brain_dir=brain_dir,
            session_dir=session_dir,
            summary_dir=summary_dir,
            fast_model=os.getenv("BRAVO1_MODEL_FAST", "qwen2.5-3b-instruct-q4_k_m.gguf"),
            main_model=os.getenv("BRAVO1_MODEL_MAIN", "qwen2.5-7b-instruct-q4_k_m.gguf"),
            runtime_host=os.getenv("BRAVO1_RUNTIME_HOST", "127.0.0.1"),
            runtime_fast_port=int(os.getenv("BRAVO1_RUNTIME_FAST_PORT", "8080")),
            runtime_main_port=int(os.getenv("BRAVO1_RUNTIME_MAIN_PORT", "8081")),
            runtime_profile=os.getenv("BRAVO1_RUNTIME_PROFILE", "auto").strip().lower() or "auto",
            shell_timeout_seconds=int(os.getenv("BRAVO1_SHELL_TIMEOUT_SECONDS", "20")),
            model_request_timeout_seconds=int(os.getenv("BRAVO1_MODEL_REQUEST_TIMEOUT_SECONDS", "8")),
            browser_fetch_timeout_seconds=int(os.getenv("BRAVO1_BROWSER_FETCH_TIMEOUT_SECONDS", "8")),
            auto_summary_message_interval=max(0, int(os.getenv("BRAVO1_AUTO_SUMMARY_MESSAGE_INTERVAL", "8"))),
        )

    def ensure_dirs(self) -> None:
        for path in (self.data_dir, self.brain_dir, self.session_dir, self.summary_dir):
            path.mkdir(parents=True, exist_ok=True)
