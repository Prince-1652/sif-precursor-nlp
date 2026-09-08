import os
import logging
from app.providers.base import AIProvider
from app.providers.gemini import GeminiProvider
from app.providers.mock import MockAIProvider
try:
    from app.providers.groq_provider import GroqProvider
except ImportError:
    GroqProvider = None
from app.core.config import settings

logger = logging.getLogger(__name__)

class FallbackProvider(AIProvider):
    def __init__(self, primary: AIProvider, secondary: AIProvider):
        self.primary = primary
        self.secondary = secondary

    async def normalize_text(self, text: str):
        try:
            return await self.primary.normalize_text(text)
        except Exception as e:
            logger.warning(f"Primary provider failed: {e}. Falling back to secondary.")
            return await self.secondary.normalize_text(text)

    async def generate_embedding(self, text: str) -> list[float]:
        try:
            return await self.primary.generate_embedding(text)
        except Exception as e:
            logger.warning(f"Primary provider failed embedding: {e}. Falling back to secondary.")
            return await self.secondary.generate_embedding(text)

def get_ai_provider() -> AIProvider:
    provider_name = settings.AI_PROVIDER.lower()
    
    if provider_name == "mock":
        return MockAIProvider()
    elif provider_name == "gemini":
        gemini = GeminiProvider()
        if getattr(settings, "GROQ_API_KEY", None) and GroqProvider:
            groq = GroqProvider()
            return FallbackProvider(primary=gemini, secondary=groq)
        return gemini
    elif provider_name == "groq" and GroqProvider:
        return GroqProvider()
    else:
        # Default to mock if unspecified or invalid, to prevent unexpected charges
        return MockAIProvider()
