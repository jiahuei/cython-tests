from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

CURR_DIR = Path(__file__).resolve().parent


class EnvConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ooo_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        cli_parse_args=False,
    )
    db_path: str = "sqlite+aiosqlite:///./db.sqlite3"
    host: str = "0.0.0.0"
    port: int = 6969
    workers: int = 1


ENV_CONFIG = EnvConfig()
