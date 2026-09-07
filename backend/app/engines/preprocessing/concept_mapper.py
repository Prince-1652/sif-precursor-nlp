import json
import re
import os
from typing import Tuple, List, Dict, Any

class ConceptMapper:
    def __init__(self, config_path: str = None):
        self.concepts = {}
        self._load_config(config_path)
        
        # Sort keys by length descending so longer phrases match first
        if self.concepts:
            sorted_keys = sorted(self.concepts.keys(), key=len, reverse=True)
            escaped_keys = [re.escape(k) for k in sorted_keys]
            self.pattern = re.compile(r'\b(' + '|'.join(escaped_keys) + r')\b')
        else:
            self.pattern = None

    def _load_config(self, config_path: str):
        if not config_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
            config_path = os.path.join(base_dir, "config", "safety_lexicon", "safety_concepts_v1.json")
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.concepts = {k.lower(): v for k, v in data.items()}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load safety lexicon from {config_path}: {e}")
            self.concepts = {}

    def map_concepts(self, text: str) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """
        Maps surface forms to canonical concepts.
        We don't replace the text in this stage, we just tag it (record in trace/found).
        Actually, PRD implies we might just find them or replace them.
        Let's just tag them to build the safety_concepts list, and return the text unmodified.
        """
        if not self.pattern or not text:
            return text, [], []
            
        found_concepts = set()
        trace = []
        
        # We use finditer instead of sub to just find and log them without modifying the text.
        for match in self.pattern.finditer(text):
            surface_form = match.group(0)
            canonical = self.concepts.get(surface_form)
            if canonical:
                found_concepts.add(canonical)
                trace.append({
                    "found": surface_form,
                    "concept": canonical,
                    "rule": f"concept_map:{canonical}"
                })
                
        return text, trace, list(found_concepts)
