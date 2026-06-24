from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="JARVIS Local", alias="APP_NAME")
    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    debug: bool = Field(default=True, alias="DEBUG")
    app_allowed_origins: str = Field(default="http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1,http://localhost,null", alias="APP_ALLOWED_ORIGINS")
    app_allowed_hosts: str = Field(default="127.0.0.1,localhost", alias="APP_ALLOWED_HOSTS")
    app_request_max_bytes: int = Field(default=1048576, alias="APP_REQUEST_MAX_BYTES")

    data_dir: Path = Field(default=Path("./data"), alias="DATA_DIR")
    model_dir: Path = Field(default=Path("./data/models"), alias="MODEL_DIR")
    memory_db_path: Path = Field(default=Path("./data/memory/jarvis.db"), alias="MEMORY_DB_PATH")
    audit_log_path: Path = Field(default=Path("./data/logs/audit.jsonl"), alias="AUDIT_LOG_PATH")

    default_fast_model: str = Field(default="Qwen2.5-3B-Instruct-Q4_K_M.gguf", alias="DEFAULT_FAST_MODEL")
    default_main_model: str = Field(default="Qwen2.5-7B-Instruct-Q4_K_M.gguf", alias="DEFAULT_MAIN_MODEL")
    default_model_provider: str = Field(default="mock", alias="DEFAULT_MODEL_PROVIDER")

    allow_shell_tool: bool = Field(default=True, alias="ALLOW_SHELL_TOOL")
    shell_timeout_seconds: int = Field(default=20, alias="SHELL_TIMEOUT_SECONDS")

    allow_file_tool: bool = Field(default=True, alias="ALLOW_FILE_TOOL")
    workspace_root: Path = Field(default=Path("."), alias="WORKSPACE_ROOT")
    max_file_read_bytes: int = Field(default=200000, alias="MAX_FILE_READ_BYTES")

    allow_browser_tool: bool = Field(default=True, alias="ALLOW_BROWSER_TOOL")
    browser_headless: bool = Field(default=False, alias="BROWSER_HEADLESS")
    browser_default_timeout_ms: int = Field(default=15000, alias="BROWSER_DEFAULT_TIMEOUT_MS")
    browser_artifact_dir: Path = Field(default=Path("./data/browser"), alias="BROWSER_ARTIFACT_DIR")
    browser_channel_preference: str = Field(default="chrome,msedge,brave,firefox,playwright_chromium", alias="BROWSER_CHANNEL_PREFERENCE")

    allow_process_tool: bool = Field(default=True, alias="ALLOW_PROCESS_TOOL")
    process_start_timeout_seconds: int = Field(default=5, alias="PROCESS_START_TIMEOUT_SECONDS")

    allow_desktop_tool: bool = Field(default=True, alias="ALLOW_DESKTOP_TOOL")
    desktop_artifact_dir: Path = Field(default=Path("./data/desktop"), alias="DESKTOP_ARTIFACT_DIR")
    desktop_key_interval_seconds: float = Field(default=0.01, alias="DESKTOP_KEY_INTERVAL_SECONDS")
    desktop_action_pause_seconds: float = Field(default=0.1, alias="DESKTOP_ACTION_PAUSE_SECONDS")

    checkpoint_dir: Path = Field(default=Path("./data/checkpoints"), alias="CHECKPOINT_DIR")
    wrapper_state_path: Path = Field(default=Path("./data/memory/app_wrapper_state.json"), alias="WRAPPER_STATE_PATH")
    maintenance_settings_path: Path = Field(default=Path("./data/memory/maintenance_settings.json"), alias="MAINTENANCE_SETTINGS_PATH")
    max_chat_message_chars: int = Field(default=12000, alias="MAX_CHAT_MESSAGE_CHARS")
    audit_max_field_chars: int = Field(default=4000, alias="AUDIT_MAX_FIELD_CHARS")
    audit_max_collection_items: int = Field(default=40, alias="AUDIT_MAX_COLLECTION_ITEMS")

    llama_n_ctx: int = Field(default=4096, alias="LLAMA_N_CTX")
    llama_n_threads: int = Field(default=0, alias="LLAMA_N_THREADS")
    llama_n_gpu_layers: int = Field(default=0, alias="LLAMA_N_GPU_LAYERS")
    llama_max_tokens: int = Field(default=384, alias="LLAMA_MAX_TOKENS")


settings = Settings()
