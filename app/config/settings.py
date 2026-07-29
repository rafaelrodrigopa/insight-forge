import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Configurações globais e variáveis de ambiente do Insight Forge.
    """

    # Diretórios do projeto
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    POSTS_DIR: Path = BASE_DIR / "posts"
    SPECS_DIR: Path = BASE_DIR / "specs"

    # Configurações do ambiente
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "t", "yes")

    # Chaves de Provedores de IA
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")

    # LinkedIn credentials
    LINKEDIN_CLIENT_ID: str | None = os.getenv("CLIENT_ID_LINKEDIN")
    LINKEDIN_CLIENT_SECRET: str | None = os.getenv("CLIENT_SECRET_LINKEDIN")
    LINKEDIN_ACCESS_TOKEN: str | None = os.getenv("LINKEDIN_ACCESS_TOKEN")


settings = Settings()