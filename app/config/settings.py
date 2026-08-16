from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configurações globais e variáveis de ambiente do Insight Forge.
    """

    # Diretórios do projeto
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    POSTS_DIR: Path = BASE_DIR / "posts"
    SPECS_DIR: Path = BASE_DIR / "specs"

    # Configurações do ambiente
    ENV: str = "development"
    DEBUG: bool = True

    # Chaves de Provedores de IA
    GEMINI_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    # LinkedIn credentials
    LINKEDIN_CLIENT_ID: str | None = Field(None, env="CLIENT_ID_LINKEDIN")
    LINKEDIN_CLIENT_SECRET: str | None = Field(None, env="CLIENT_SECRET_LINKEDIN")
    LINKEDIN_ACCESS_TOKEN: str | None = Field(None, env="LINKEDIN_ACCESS_TOKEN")

    # PostgreSQL credentials
    POSTGRES_DB: str = Field("postgres", env="POSTGRES_DB")
    POSTGRES_USER: str = Field("postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field("", env="POSTGRES_PASSWORD")
    POSTGRES_HOST: str = Field("localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(5432, env="POSTGRES_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()