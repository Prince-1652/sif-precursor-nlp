from dataclasses import dataclass
from typing import List

@dataclass
class SIFRule:
    text_pattern: str
    concept: str
    type: str
    base_weight: float

# Base deterministic rules for SIF
# Weights: >0.8 usually implies HIGH SIF potential
SIF_RULES: List[SIFRule] = [
    SIFRule("energized equipment", "ENERGIZED_EQUIPMENT", "HAZARD", 0.9),
    SIFRule("confined space", "CONFINED_SPACE", "HAZARD", 0.9),
    SIFRule("suspended load", "SUSPENDED_LOAD", "HAZARD", 0.9),
    SIFRule("work at height", "WORK_AT_HEIGHT", "ACTIVITY", 0.8),
    SIFRule("bypassed safety control", "BYPASSED_CONTROL", "BARRIER_FAILURE", 0.9),
    SIFRule("fall protection", "FALL_PROTECTION", "BARRIER", 0.5),
    SIFRule("lockout tagout", "LOTO", "BARRIER", 0.5),
    SIFRule("loto", "LOTO", "BARRIER", 0.5),
    SIFRule("crushed", "CRUSH_HAZARD", "OUTCOME", 0.9),
    SIFRule("amputation", "AMPUTATION", "OUTCOME", 1.0),
    SIFRule("fatality", "FATALITY", "OUTCOME", 1.0),
    SIFRule("explosion", "EXPLOSION", "HAZARD", 0.9),
    SIFRule("fire", "FIRE", "HAZARD", 0.7),
    SIFRule("arc flash", "ARC_FLASH", "HAZARD", 0.9),
    SIFRule("trench collapse", "EXCAVATION_HAZARD", "HAZARD", 0.9),
    # Added based on user feedback
    SIFRule("machinery guarding", "MACHINE_GUARDING", "BARRIER", 0.7),
    SIFRule("inside the machinery", "POINT_OF_OPERATION_HAZARD", "HAZARD", 0.9),
    SIFRule("not secured", "UNSECURED_ENERGY", "BARRIER_FAILURE", 0.8),
    SIFRule("without applying a lock", "BYPASSED_LOTO", "BARRIER_FAILURE", 0.9),
    SIFRule("almost turned", "NEAR_MISS", "ACTIVITY", 0.6),
]
