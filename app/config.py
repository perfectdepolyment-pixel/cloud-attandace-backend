import re

from pydantic import field_validator
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
    # Optional: if all three are set, an ADMIN account is created on startup
    # when no account with that email exists yet.
    admin_name: str | None = None
    admin_email: str | None = None
    admin_password: str | None = None

    @field_validator("allowed_origin_regex", mode="before")
    @classmethod
    def _clean_origin_regex(cls, value):
        # Blank (e.g. an empty env var on Render) means "not set".
        if value is None or not str(value).strip():
            return None
        value = str(value).strip()
        try:
            re.compile(value)
        except re.error as exc:
            raise ValueError(
                f"ALLOWED_ORIGIN_REGEX is not a valid regular expression ({exc}). "
                r"Use a regex such as https://.*\.vercel\.app, not a wildcard like *.vercel.app. "
                "Leave it empty if you don't need it."
            ) from exc
        return value

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    class Config:
        env_file = ".env"


settings = Settings()
