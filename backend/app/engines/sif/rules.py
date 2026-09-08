import json
import os
from dataclasses import dataclass
from typing import List

@dataclass
class SIFRule:
    text_pattern: str
    concept: str
    type: str
    base_weight: float

def load_sif_rules(version: str = "v1") -> List[SIFRule]:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    path = os.path.join(base_dir, "config", "sif_rules", f"sif_rules_{version}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [SIFRule(**d) for d in data]
    except FileNotFoundError:
        return []

SIF_RULES: List[SIFRule] = load_sif_rules()
