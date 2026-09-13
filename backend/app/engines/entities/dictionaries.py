from typing import Dict, List

# Simple dictionary-based lookups for entity extraction
DICTIONARIES: Dict[str, List[str]] = {
    "ACTIVITY": [
        "maintenance", "inspection", "lifting", "drilling", "welding", 
        "cutting", "grinding", "cleaning", "driving"
    ],
    "EQUIPMENT": [
        "pump", "crane", "scaffold", "pipeline", "valve", 
        "harness", "truck", "forklift", "vessel", "tank"
    ],
    "PERSON_ROLE": [
        "technician", "operator", "supervisor", "welder", 
        "driver", "contractor", "worker"
    ],
    "HAZARD": [
        "energized equipment", "suspended load", "gas exposure", 
        "confined space", "height", "spark", "pinch point", "spill"
    ],
    "BARRIER": [
        "loto", "lockout tagout", "lockout/tagout", "permit", "gas test", 
        "guarding", "safety guard", "fall protection", "seatbelt", "barricade"
    ],
    "BODY_PART": [
        "head", "eye", "arm", "hand", "finger", "leg", "foot", "toe", 
        "back", "shoulder", "chest"
    ],
    "OUTCOME": [
        "fatality", "amputation", "fracture", "burn", "laceration", "concussion"
    ]
}
