import re
from typing import List, Dict, Any
from app.engines.entities.dictionaries import DICTIONARIES
from app.engines.nlp_utils import get_token_context, detect_status

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
                    context = get_token_context(text_lower, start, end, window_size=10)
                    status = detect_status(context)
                        
                # Calculate confidence based on context clarity
                confidence = 0.8  # Base confidence for dictionary match
                if entity_type == "BARRIER":
                    if status == "FAILED":
                        confidence = 0.95  # Clear failure context
                    elif status == "SUCCESSFUL":
                        confidence = 0.90
                    else:
                        confidence = 0.6  # Unknown status = less confident

                entities.append({
                    "entity_type": entity_type,
                    "value": keyword,
                    "normalized_value": keyword,
                    "source_start": match.start(),
                    "source_end": match.end(),
                    "confidence": confidence,
                    "extraction_method": "dictionary_v1",
                    "status": status  # only relevant for BARRIER
                })
                
    # Post-Processing: Aggregation / Deduplication Layer
    # Deduplicate entities based on (entity_type, normalized_value) to prevent 
    # the same concept from crowding the UI if mentioned multiple times in one report.
    unique_entities = {}
    for ent in entities:
        key = (ent["entity_type"], ent["normalized_value"])
        if key not in unique_entities:
            ent["occurrences"] = [{"start": ent["source_start"], "end": ent["source_end"]}]
            unique_entities[key] = ent
        else:
            unique_entities[key]["occurrences"].append({
                "start": ent["source_start"], 
                "end": ent["source_end"]
            })
            
    return list(unique_entities.values())
