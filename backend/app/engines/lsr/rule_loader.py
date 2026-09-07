import json
import os
from dataclasses import dataclass
from typing import List

@dataclass
class LSRRuleDef:
    rule_code: str
    positive_terms: List[str]
    negative_contexts: List[str]
    danger_patterns: List[str]

def load_rules(version: str = "v1") -> List[LSRRuleDef]:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    path = os.path.join(base_dir, "config", "lsr_rules", f"lsr_rules_{version}.json")
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    return [LSRRuleDef(**d) for d in data]
