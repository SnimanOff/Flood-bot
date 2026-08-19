from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):

    database: str
    bot: str
    github_repo: str = ""
    github_token: str | None = None
    github_branch: str = "main"
    root_id: int | None = None  # env ROOT_ID

    bot_mode: str = "webhook"  # webhook | polling
    webhook_host: str = ""  # https://bot.example.com  (no trailing slash)
    webhook_path: str = "/telegram/webhook"
    webhook_secret: str = ""  # random string, Telegram secret_token
    webhook_port: int = 8080
    domain: str = ""  # bot.example.com for Caddy (optional, for docs)

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def webhook_url(self) -> str:
        return f"{self.webhook_host.rstrip('/')}{self.webhook_path}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
