from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llava:13b"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8100

    # Market Data
    binance_api_key: str = ""
    coingecko_api_key: str = ""

    # Risk Defaults
    default_risk_percent: float = 2.0
    default_account_balance: float = 10000.0

    # Language
    report_language: str = "hu"


settings = Settings()
