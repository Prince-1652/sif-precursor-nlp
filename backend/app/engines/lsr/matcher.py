import re
from typing import List
from app.engines.lsr.rule_loader import LSRRuleDef
from app.engines.nlp_utils import get_token_context

class LSRMatcher:
    def __init__(self, rules: List[LSRRuleDef]):
        self.rules = rules

    def match(self, normalized_text: str) -> dict:
        text_lower = normalized_text.lower()
        matches = []
        
        for rule in self.rules:
            matched_phrases = []
            matched_phrases_with_offsets = []
            score = 0.0
            
            # Check danger patterns first (highest weight)
            for pattern in rule.danger_patterns:
                for match in re.finditer(r'\b' + re.escape(pattern) + r'\b', text_lower):
                    # verify it's not in a negative context (local window only)
                    local_context = get_token_context(text_lower, match.start(), match.end(), window_size=10)
                    context_safe = True
                    for neg in rule.negative_contexts:
                        if re.search(r'\b' + re.escape(neg) + r'\b', local_context):
                            context_safe = False
                            break
                    if context_safe:
                        matched_phrases.append(pattern)
                        matched_phrases_with_offsets.append({
                            "text": pattern,
                            "start": match.start(),
                            "end": match.end()
                        })
                        score += 0.8
                        break # score once per pattern
                    
            # Check positive terms
            for term in rule.positive_terms:
                for match in re.finditer(r'\b' + re.escape(term) + r'\b', text_lower):
                    # verify it's not in a negative context (local window only)
                    local_context = get_token_context(text_lower, match.start(), match.end(), window_size=10)
                    context_safe = True
                    for neg in rule.negative_contexts:
                        if re.search(r'\b' + re.escape(neg) + r'\b', local_context):
                            context_safe = False
                            break
                    if context_safe:
                        if term not in matched_phrases:
                            matched_phrases.append(term)
                        matched_phrases_with_offsets.append({
                            "text": term,
                            "start": match.start(),
                            "end": match.end()
                        })
                        score += 0.3
                        break
                        
            if score > 0:
                final_score = min(1.0, score)
                matches.append({
                    "rule_id": rule.rule_code,
                    "score": final_score,
                    "confidence": 1.0,
                    "matched_phrases": matched_phrases,
                    "matched_phrases_with_offsets": matched_phrases_with_offsets,
                    "method": "deterministic_v1"
                })
                
        return matches
