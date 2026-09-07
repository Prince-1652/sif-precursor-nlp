from typing import Protocol, List, Optional
from pydantic import BaseModel, Field

class NormalizationResult(BaseModel):
    normalized_english: str
    language: str
    confidence: float
    uncertain_terms: List[str] = []
    preserved_terms: List[str] = []
    semantic_notes: List[str] = []

class SafetyAnalysisResult(BaseModel):
    hazards: List[str] = Field(description="List of extracted hazards from the text")
    root_causes: List[str] = Field(description="List of potential root causes identified")
    severity_score: int = Field(description="Severity score from 1 (lowest) to 5 (highest) based on the risk")
    sif_potential: bool = Field(description="True if the report describes circumstances that could plausibly result in serious injury or fatality.")
    sif_score: float = Field(description="Confidence score for SIF potential between 0.0 and 1.0")
    risk_band: str = Field(description="Risk band: HIGH, MEDIUM, LOW")
    life_saving_rules: List[str] = Field(description="Any applicable IOGP Life-Saving Rules (e.g., Bypassing Safety Controls, Confined Space, Driving, Energy Isolation, Hot Work, Line of Fire, Safe Mechanical Lifting, Working at Height, Permit to Work)")
    precursors: List[str] = Field(description="List of structured precursor information such as failed barriers, missing controls, or dangerous behaviors")

class AIProvider(Protocol):
    async def normalize(self, report_text: str) -> NormalizationResult:
        ...
    
    async def analyze_safety(self, report_text: str) -> SafetyAnalysisResult:
        ...
        
    async def generate_embedding(self, text: str) -> List[float]:
        ...

class MockAIProvider:
    async def normalize(self, report_text: str) -> NormalizationResult:
        return NormalizationResult(
            normalized_english=f"Normalized: {report_text}",
            language="en-mock",
            confidence=0.99
        )
    
    async def analyze_safety(self, report_text: str) -> SafetyAnalysisResult:
        return SafetyAnalysisResult(
            hazards=["Mock Hazard"],
            root_causes=["Mock Root Cause"],
            severity_score=3,
            sif_potential=True,
            sif_score=0.85,
            risk_band="MEDIUM",
            life_saving_rules=["Mock Rule"],
            precursors=["Mock Precursor"]
        )
        
    async def generate_embedding(self, text: str) -> List[float]:
        return [0.0] * 768

class GeminiAIProvider:
    def __init__(self):
        from google import genai
        from app.core.config import settings
        if not settings.GEMINI_API_KEY:
            self.client = genai.Client(api_key="mock_key_for_testing")
        else:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def normalize(self, report_text: str) -> NormalizationResult:
        from google.genai import types
        prompt = f"""
        Normalize the following safety report. Translate to English if necessary.
        Extract any uncertain or preserved technical terms.
        
        Report:
        {report_text}
        """
        response = self.client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=NormalizationResult,
            ),
        )
        return response.parsed

    async def analyze_safety(self, report_text: str) -> SafetyAnalysisResult:
        from google.genai import types
        prompt = f"""
        You are an expert safety analyst for the oil and gas industry.
        Analyze the following safety report and extract the hazards, root causes, and assign a severity score (1-5).
        Also, evaluate the Serious Injury or Fatality (SIF) potential. 
        Assign any relevant IOGP Life-Saving Rules, and extract precursors (failed barriers, missing controls).
        
        Report:
        {report_text}
        """
        response = self.client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SafetyAnalysisResult,
            ),
        )
        return response.parsed

    async def generate_embedding(self, text: str) -> List[float]:
        from google.genai import types
        result = self.client.models.embed_content(
            model="gemini-embedding-2",
            contents=text,
            config=types.EmbedContentConfig(output_dimensionality=768)
        )
        return result.embeddings[0].values

def get_ai_provider() -> AIProvider:
    from app.core.config import settings
    # In a real app we might select provider based on config
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "mock_key_for_testing":
        return GeminiAIProvider()
    return MockAIProvider()
