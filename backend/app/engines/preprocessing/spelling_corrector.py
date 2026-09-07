import json
import re
import os
from typing import Tuple, List, Dict, Any

class SpellingCorrector:
    def __init__(self, config_path: str = None):
        self.corrections = {}
        self._load_config(config_path)
        if self.corrections:
            escaped_keys = [re.escape(k) for k in self.corrections.keys()]
            self.pattern = re.compile(r'\b(' + '|'.join(escaped_keys) + r')\b')
        else:
            self.pattern = None

    def _load_config(self, config_path: str):
        if not config_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
            config_path = os.path.join(base_dir, "config", "spelling", "domain_corrections_v1.json")
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.corrections = {k.lower(): v.lower() for k, v in data.items()}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load spelling config from {config_path}: {e}")
            self.corrections = {}

    def correct(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Applies controlled spelling corrections.
        Returns: (corrected_text, normalization_trace_entries)
        """
        if not self.pattern or not text:
            return text, []
            
        trace = []
        
        def replace_match(match):
            misspelled = match.group(0)
            correction = self.corrections.get(misspelled)
            if correction:
                trace.append({
                    "from": misspelled,
                    "to": correction,
                    "rule": f"spelling:{misspelled}"
                })
                return correction
            return misspelled
            
        corrected_text = self.pattern.sub(replace_match, text)
        return corrected_text, trace
