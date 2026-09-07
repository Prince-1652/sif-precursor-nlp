from dataclasses import dataclass
import fasttext
import os
import re

@dataclass
class LanguageDetectionResult:
    language_code: str       # "en", "es", "mixed", etc.
    confidence: float        # 0.0-1.0
    is_mixed: bool
    is_reliable: bool

class LanguageDetector:
    def __init__(self, model_path: str = None):
        if not model_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            model_path = os.path.join(base_dir, "models", "lid.176.ftz")
            
        self.model = None
        if os.path.exists(model_path):
            # suppress warning for windows
            fasttext.FastText.eprint = lambda x: None
            self.model = fasttext.load_model(model_path)
            
    def detect(self, text: str) -> LanguageDetectionResult:
        if not text or len(text.strip()) < 5:
            return LanguageDetectionResult(language_code="unknown", confidence=0.0, is_mixed=False, is_reliable=False)
            
        if not self.model:
            # Fallback if model not loaded
            return LanguageDetectionResult(language_code="en", confidence=1.0, is_mixed=False, is_reliable=True)
            
        # Fasttext requires single line text
        clean_text = text.replace('\n', ' ')
        
        predictions = self.model.predict(clean_text, k=2)
        labels = predictions[0]
        probs = predictions[1]
        
        # Labels are like '__label__en'
        primary_lang = labels[0].replace('__label__', '')
        primary_conf = float(probs[0])
        
        is_mixed = False
        if len(labels) > 1:
            secondary_conf = float(probs[1])
            # If secondary language is also relatively high, flag as mixed
            if secondary_conf > 0.3:
                is_mixed = True
                
        # Simple ASCII heuristic
        ascii_ratio = sum(1 for c in text if ord(c) < 128) / max(len(text), 1)
        if primary_lang == 'en' and ascii_ratio < 0.5:
            # English should be mostly ASCII. If it's not, confidence drops
            primary_conf *= ascii_ratio
            
        is_reliable = len(text.strip()) >= 10
        
        return LanguageDetectionResult(
            language_code=primary_lang,
            confidence=primary_conf,
            is_mixed=is_mixed,
            is_reliable=is_reliable
        )
