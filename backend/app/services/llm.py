from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List
from app.core.config import settings

def get_client():
    if not settings.GEMINI_API_KEY:
        # Provide a dummy key if missing, so it doesn't crash on import/tests
        # Tests will mock the API calls anyway
        return genai.Client(api_key="mock_key_for_testing")
    return genai.Client(api_key=settings.GEMINI_API_KEY)

class SafetyAnalysis(BaseModel):
    hazards: List[str] = Field(description="List of extracted hazards from the text")
    root_causes: List[str] = Field(description="List of potential root causes identified")
    severity_score: int = Field(description="Severity score from 1 (lowest) to 5 (highest) based on the risk")

def analyze_report_text(text: str) -> SafetyAnalysis:
    prompt = f"""
    You are an expert safety analyst for the oil and gas industry.
    Analyze the following safety report and extract the hazards, root causes, and assign a severity score (1-5).
    
    Report:
    {text}
    """
    client = get_client()
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SafetyAnalysis,
        ),
    )
    return response.parsed

def generate_embedding(text: str) -> List[float]:
    client = get_client()
    result = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=768)
    )
    # The SDK returns EmbedContentResponse with embeddings list
    return result.embeddings[0].values
