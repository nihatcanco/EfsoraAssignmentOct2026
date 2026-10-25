from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    database_url: str = "postgresql+psycopg://briefbase:briefbase@localhost:5433/briefbase"
    jwt_secret: str
    jwt_expire_minutes: int = 60 * 24

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-opus-5-5"

    # comma separated list
    cors_origins: str = "http://localhost:3000"

    @property
    def sqlalchemy_url(self) -> str:
        url = self.database_url
        for prefix in ("postgres://", "postgresql://"):
            if url.startswith(prefix):
                return "postgresql+psycopg://" + url[len(prefix):]
        return url

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
