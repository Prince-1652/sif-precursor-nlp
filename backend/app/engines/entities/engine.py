from typing import List, Dict, Any
from app.engines.entities.extractors import extract_entities_from_text

class EntityEngine:
    async def extract(self, normalized_text: str) -> List[Dict[str, Any]]:
        text_lower = normalized_text.lower()
        return extract_entities_from_text(text_lower)

entity_engine = EntityEngine()
