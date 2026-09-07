from app.providers.base import AIProvider, NormalizationResult

class MockAIProvider(AIProvider):
    async def normalize_text(self, text: str) -> NormalizationResult:
        return NormalizationResult(
            normalized_text=f"Normalized: {text}",
            language_detected="es",
            confidence=0.95
        )

    async def generate_embedding(self, text: str) -> list[float]:
        return [0.1] * 768
