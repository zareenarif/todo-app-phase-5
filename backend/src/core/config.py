"""
Application configuration module.
Loads environment variables and provides settings.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str

    # Authentication
    BETTER_AUTH_SECRET: str

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # Optional
    DEBUG: bool = False

    # LLM Configuration (Groq - free tier)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Ollama Configuration (local fallback)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # Agent Configuration
    LLM_PROVIDER: str = "groq"  # "groq" or "ollama"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1024

    # Phase 3: OpenAI Configuration (for Agents SDK)
    OPENAI_API_KEY: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
