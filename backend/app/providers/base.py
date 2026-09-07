from typing import Protocol, List
from pydantic import BaseModel, Field

class NormalizationResult(BaseModel):
    normalized_text: str = Field(description="The canonical normalized English text")
    language_detected: str = Field(description="The language that was detected in the original text")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    grammar_corrected: bool = Field(default=False, description="Whether grammar was corrected")
    domain_terms_mapped: List[str] = Field(default_factory=list, description="List of domain terms mapped")

class AIProvider(Protocol):
    async def normalize_text(self, text: str) -> NormalizationResult: ...
    async def generate_embedding(self, text: str) -> list[float]: ...
