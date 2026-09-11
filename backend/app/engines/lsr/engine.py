from typing import List, Dict, Any
from app.engines.lsr.rule_loader import load_rules
from app.engines.lsr.matcher import LSRMatcher

class LSREngine:
    def __init__(self):
        self.rules = load_rules()
        self.TYPE_EXCLUSIONS = {
            "Spill": ["SAFE_MECHANICAL_LIFTING", "DRIVING", "WORKING_AT_HEIGHT", "LINE_OF_FIRE"],
            "Unsafe Condition": ["DRIVING"]
        }

    async def analyze(self, normalized_text: str, report_type: str = None) -> List[Dict[str, Any]]:
        text_lower = normalized_text.lower()
        
        # Filter rules based on report_type context
        exclusions = self.TYPE_EXCLUSIONS.get(report_type, []) if report_type else []
        active_rules = [r for r in self.rules if r.rule_code not in exclusions]

        matcher = LSRMatcher(active_rules)
        predictions = matcher.match(text_lower)
        return predictions

lsr_engine = LSREngine()
