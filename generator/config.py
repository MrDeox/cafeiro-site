from dataclasses import dataclass
from dotenv import load_dotenv
import os


load_dotenv()


@dataclass
class Config:
    # Marca e site
    SITE_NAME: str = os.getenv("SITE_NAME", "Cafeiro")
    SITE_TAGLINE: str = os.getenv("SITE_TAGLINE", "Guia prático de café em casa")
    SITE_URL: str = os.getenv("SITE_URL", "https://example.com")
    CONTACT_EMAIL: str = os.getenv("CONTACT_EMAIL", "contato@example.com")

    # Localização e idioma
    LANGUAGE: str = os.getenv("LANGUAGE", "pt-BR")
    TIMEZONE: str = os.getenv("TIMEZONE", "America/Sao_Paulo")

    # Diretórios
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "public")
    CACHE_DIR: str = os.getenv("CACHE_DIR", "cache")

    # LLM/OpenRouter
    OPENROUTER_API_KEY: str | None = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat-v3.1:free")
    LLM_MAX_CALLS_PER_RUN: int = int(os.getenv("LLM_MAX_CALLS_PER_RUN", "3"))
    GENERATE_WITH_LLM: bool = os.getenv("GENERATE_WITH_LLM", "true").lower() in {"1", "true", "yes"}

    # Limites de geração
    MAX_POSTS_TOTAL: int = int(os.getenv("MAX_POSTS_TOTAL", "200"))
    MAX_NEW_PAGES_PER_RUN: int = int(os.getenv("MAX_NEW_PAGES_PER_RUN", "10"))

    # Afiliados
    AMAZON_TAG_BR: str = os.getenv("AMAZON_TAG_BR", "SEU_TAG-20")

    # Analytics
    GA_MEASUREMENT_ID: str | None = os.getenv("GA_MEASUREMENT_ID")

    # Deploy
    GITHUB_PAGES_BRANCH: str = os.getenv("GITHUB_PAGES_BRANCH", "gh-pages")


cfg = Config()
