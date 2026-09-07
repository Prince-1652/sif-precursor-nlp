import re
from typing import List, Dict, Any
from app.engines.entities.dictionaries import DICTIONARIES

def extract_entities_from_text(text_lower: str) -> List[Dict[str, Any]]:
    entities = []
    
    for entity_type, keywords in DICTIONARIES.items():
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            for match in re.finditer(pattern, text_lower):
                # Basic context extraction (e.g. for barriers)
                status = "UNKNOWN"
                if entity_type == "BARRIER":
                    start, end = match.start(), match.end()
                    context = text_lower[max(0, start-20):min(len(text_lower), end+20)]
                    if any(w in context for w in ["failed", "not", "without", "no", "missing", "bypassed"]):
                        status = "FAILED"
                    elif any(w in context for w in ["completed", "verified", "used"]):
                        status = "SUCCESSFUL"
                        
                entities.append({
                    "entity_type": entity_type,
                    "value": keyword,
                    "normalized_value": keyword,
                    "source_start": match.start(),
                    "source_end": match.end(),
                    "confidence": 1.0,
                    "extraction_method": "dictionary_v1",
                    "status": status  # only relevant for BARRIER
                })
                
    return entities
