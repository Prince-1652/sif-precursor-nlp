import os
from app.providers.base import AIProvider
from app.providers.gemini import GeminiProvider
from app.providers.mock import MockAIProvider
from app.core.config import settings

def get_ai_provider() -> AIProvider:
    provider_name = settings.AI_PROVIDER.lower()
    
    if provider_name == "mock":
        return MockAIProvider()
    elif provider_name == "gemini":
        return GeminiProvider()
    else:
        # Default to mock if unspecified or invalid, to prevent unexpected charges
        return MockAIProvider()
