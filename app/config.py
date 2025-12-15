from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, Field, field_validator


class Settings(BaseSettings):
    recipient_email: EmailStr
    recipient_name: str = Field(..., min_length=1, max_length=100)

    smtp_host: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_username: str
    smtp_password: str
    smtp_use_tls: bool = Field(default=True)

    api_title: str = Field(default="Mailbridge")
    api_version: str = Field(default="1.0.0")
    cors_origins: str = Field(default="*")

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return v
        return v

    def get_cors_origins_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()
