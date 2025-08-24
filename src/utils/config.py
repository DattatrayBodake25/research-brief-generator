import os
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional


class Settings(BaseSettings):
    # API Keys
    mistral_api_key: str = Field(..., env="MISTRAL_API_KEY")
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")

    # Optional Search Providers
    tavily_api_key: Optional[str] = Field(None, env="TAVILY_API_KEY")
    serpapi_api_key: Optional[str] = Field(None, env="SERPAPI_API_KEY")
    brave_search_api_key: Optional[str] = Field(None, env="BRAVE_SEARCH_API_KEY")

    # LangSmith (Observability)
    langsmith_api_key: Optional[str] = Field(None, env="LANGSMITH_API_KEY")
    langsmith_project: str = Field("research-brief-generator", env="LANGSMITH_PROJECT")
    langsmith_tracing: bool = Field(False, env="LANGSMITH_TRACING")

    # App Settings
    log_level: str = Field("INFO", env="LOG_LEVEL")
    max_retries: int = Field(2, env="MAX_RETRIES")
    default_depth: int = Field(2, env="DEFAULT_DEPTH")

    search_results_per_step: int = Field(5, env="SEARCH_RESULTS_PER_STEP")
    summary_source_limit: int = Field(3, env="SUMMARY_SOURCE_LIMIT")

    # Model Settings
    mistral_model: str = Field("mistral-small", env="MISTRAL_MODEL")
    gemini_model: str = Field("gemini-1.5-flash", env="GEMINI_MODEL")

    @validator("langsmith_tracing", pre=True)
    def validate_langsmith_tracing(cls, v):
        return str(v).lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()