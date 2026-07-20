from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    slack_bot_token: str = ""
    slack_signing_secret: str = ""
    openai_api_key: str = ""
    database_url: str = "sqlite:///./rye.db"
    github_webhook_secret: str = "supersecret"
    api_admin_token: str = "admin_token_123"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
