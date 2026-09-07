import json
import re
import os
from typing import Tuple, List, Dict, Any

class AbbreviationExpander:
    def __init__(self, config_path: str = None):
        self.abbreviations = {}
        self._load_config(config_path)
        # Create a single regex for all abbreviations to do a fast pass
        # Use word boundaries to avoid matching inside other words
        if self.abbreviations:
            escaped_keys = [re.escape(k) for k in self.abbreviations.keys()]
            self.pattern = re.compile(r'\b(' + '|'.join(escaped_keys) + r')\b')
        else:
            self.pattern = None

    def _load_config(self, config_path: str):
        if not config_path:
            # Default path relative to project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
            config_path = os.path.join(base_dir, "config", "abbreviations", "abbreviations_v1.json")
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure keys are lowercase for matching against lowercase text
                self.abbreviations = {k.lower(): v.lower() for k, v in data.items()}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load abbreviations config from {config_path}: {e}")
            self.abbreviations = {}

    def expand(self, text: str) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """
        Expands abbreviations in the text.
        Returns: (expanded_text, normalization_trace_entries, abbreviations_found)
        """
        if not self.pattern or not text:
            return text, [], []
            
        trace = []
        found = []
        
        def replace_match(match):
            abbr = match.group(0)
            expansion = self.abbreviations.get(abbr)
            if expansion:
                found.append(abbr)
                trace.append({
                    "from": abbr,
                    "to": expansion,
                    "rule": f"abbreviation:{abbr}"
                })
                return expansion
            return abbr
            
        expanded_text = self.pattern.sub(replace_match, text)
        return expanded_text, trace, list(set(found))
