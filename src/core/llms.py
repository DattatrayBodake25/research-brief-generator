from typing import Dict, List
from langchain_core.language_models.base import BaseLanguageModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI

from ..utils.config import settings
from ..utils.logger import logger


class LLMFactory:
    """Factory for creating LLM instances with different providers"""

    @staticmethod
    def create_mistral_llm() -> BaseLanguageModel:
        """Create Mistral LLM instance"""
        return ChatMistralAI(
            model=settings.mistral_model,   # e.g., "mistral-small"
            api_key=settings.mistral_api_key,
        )

    @staticmethod
    def create_gemini_llm() -> BaseLanguageModel:
        """Create Google Gemini LLM instance"""
        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            api_key=settings.gemini_api_key,
            temperature=0.7,
            max_retries=settings.max_retries,
        )

    @staticmethod
    def get_llm(provider: str = "mistral") -> BaseLanguageModel:
        """Get LLM instance by provider"""
        if provider == "mistral":
            return LLMFactory.create_mistral_llm()
        elif provider == "gemini":
            return LLMFactory.create_gemini_llm()
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

    @staticmethod
    def get_llm_for_purpose(purpose: str) -> BaseLanguageModel:
        """Get appropriate LLM for specific purpose"""
        # Use Gemini for planning (faster, cheaper)
        if purpose in ["planning", "summarization", "context"]:
            return LLMFactory.create_gemini_llm()
        # Use Mistral for complex tasks (better quality)
        else:
            return LLMFactory.create_mistral_llm()


# Export LLM instances
planning_llm = LLMFactory.get_llm_for_purpose("planning")
research_llm = LLMFactory.get_llm_for_purpose("research")