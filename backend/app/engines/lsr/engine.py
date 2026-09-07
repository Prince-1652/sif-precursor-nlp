from typing import List, Dict, Any
from app.engines.lsr.rule_loader import load_rules
from app.engines.lsr.matcher import LSRMatcher

class LSREngine:
    def __init__(self):
        self.rules = load_rules("v1")
        self.matcher = LSRMatcher(self.rules)

    async def analyze(self, normalized_text: str) -> List[Dict[str, Any]]:
        return self.matcher.match(normalized_text)

lsr_engine = LSREngine()
