from dataclasses import dataclass, field
from typing import List, Dict, Any

from app.engines.preprocessing.validation import validate_text
from app.engines.preprocessing.text_cleaner import clean_text
from app.engines.preprocessing.abbreviation_expander import AbbreviationExpander
from app.engines.preprocessing.spelling_corrector import SpellingCorrector
from app.engines.preprocessing.concept_mapper import ConceptMapper

@dataclass
class PreprocessingResult:
    original_text: str
    normalized_text: str = ""
    normalization_trace: List[Dict[str, Any]] = field(default_factory=list)
    abbreviations_found: List[str] = field(default_factory=list)
    safety_concepts: List[str] = field(default_factory=list)
    is_valid: bool = False
    validation_errors: List[str] = field(default_factory=list)
    processing_status: str = "READY"


class PreprocessingPipeline:
    def __init__(self):
        self.expander = AbbreviationExpander()
        self.corrector = SpellingCorrector()
        self.mapper = ConceptMapper()

    def process(self, original_text: str) -> PreprocessingResult:
        result = PreprocessingResult(original_text=original_text)
        
        # Stage 1: Validation
        is_valid, errors, status = validate_text(original_text)
        if not is_valid:
            result.is_valid = False
            result.validation_errors = errors
            result.processing_status = status
            return result
            
        result.is_valid = True
        
        # Stage 2-5: Cleaning (HTML, Unicode, Case, Whitespace)
        cleaned = clean_text(original_text)
        
        # Stage 6: Abbreviation Expansion
        expanded, expand_trace, abbr_found = self.expander.expand(cleaned)
        result.normalization_trace.extend(expand_trace)
        result.abbreviations_found = abbr_found
        
        # Stage 7: Spelling Correction
        corrected, spell_trace = self.corrector.correct(expanded)
        result.normalization_trace.extend(spell_trace)
        
        # Stage 8: Concept Mapping
        final_text, map_trace, concepts_found = self.mapper.map_concepts(corrected)
        result.normalization_trace.extend(map_trace)
        result.safety_concepts = concepts_found
        
        # Final result
        result.normalized_text = final_text
        result.processing_status = "READY"
        
        return result

# Global singleton
pipeline = PreprocessingPipeline()

def run_preprocessing(text: str) -> PreprocessingResult:
    return pipeline.process(text)
