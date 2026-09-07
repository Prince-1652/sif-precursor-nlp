import os
import google.generativeai as genai
from app.providers.base import AIProvider, NormalizationResult
from app.providers.retry import with_retry
from app.core.config import settings

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str = None):
        key = api_key or settings.GEMINI_API_KEY
        if not key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        genai.configure(api_key=key)
        
    def _load_prompt(self, version: str) -> str:
        # Load from config/prompts/
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        prompt_path = os.path.join(base_dir, "config", "prompts", f"{version}.txt")
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "You are a safety analysis AI. Translate and normalize the report to English."
        
    async def normalize_text(self, text: str) -> NormalizationResult:
        system_instruction = self._load_prompt("normalization_v1")
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
        
        # Protect against prompt injection by separating user input clearly
        user_message = f"<report_data>\n{text}\n</report_data>"
        
        async def call_api():
            response = await model.generate_content_async(
                user_message,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    # we use the schema fields directly here to map correctly
                    # For a true implementation we would pass a schema, but gemini python sdk 
                    # requires a specific format for response_schema
                )
            )
            # parse json
            import json
            data = json.loads(response.text)
            return NormalizationResult(**data)
            
        return await with_retry(call_api, max_retries=settings.AI_MAX_RETRIES, timeout=settings.AI_TIMEOUT_SECONDS)

    async def generate_embedding(self, text: str) -> list[float]:
        async def call_api():
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        return await with_retry(call_api, max_retries=settings.AI_MAX_RETRIES, timeout=settings.AI_TIMEOUT_SECONDS)
