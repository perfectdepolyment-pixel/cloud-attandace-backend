from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120
    allowed_origins: str = "http://localhost:5173"
    # Optional: matches Vercel preview URLs too, e.g. https://.*\.vercel\.app
    # Leave unset for local dev; set in Render's env vars once you know your
    # Vercel project's domain pattern.
    allowed_origin_regex: str | None = None

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    class Config:
        env_file = ".env"


settings = Settings()
