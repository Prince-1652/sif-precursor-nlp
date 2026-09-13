# Core Engines

The SIF Precursor system differentiates itself by moving away from "black box" LLM wrappers. Instead, it utilizes a highly structured, hybrid pipeline composed of deterministic rules engines and targeted LLM tasks.

## 1. Preprocessing & Language Gate
Before any heavy lifting occurs, the text is cleaned.
- **Preprocessor:** Uses regular expressions to strip out PII, redundant whitespace, and formatting anomalies.
- **Language Detector (FastText):** A lightning-fast, locally-run model categorizes the text. If the text is standard English, it proceeds. If the text is recognized as Hinglish or contains heavy regional slang, it is routed to an LLM for translation.
- **Normalization:** The LLM translates the slang into standard English (e.g., "helmet nahi pehna tha" -> "was not wearing a helmet").

## 2. SIF Engine (Serious Injury & Fatality)
This is a purely deterministic engine, built for speed and absolute traceability.
- **How it works:** It scans the normalized text against a JSON configuration (`config/sif_rules/sif_rules_v1.json`). It looks for specific Hazards (e.g., "energized equipment"), Activities (e.g., "work at height"), and Barriers (e.g., "fall protection").
- **Token-Aware Context & Multipliers:** It utilizes a token-aware context extraction algorithm via `nlp_utils.py` (extracting exact surrounding words rather than blind character slicing to prevent truncation). If it spots negation words next to barriers, it aggregates the severity. It also applies dynamic risk multipliers based on the report metadata (e.g. `Incident` = 1.3x, `Observation` = 0.5x).
- **Output:** An aggregated score (0.0 to 1.0). If `>= 0.75`, the report is flagged with a `HIGH` Risk Band.

## 3. LSR Engine (Life Saving Rules)
This engine categorizes the observation against the 9 standard Life Saving Rules (e.g., Confined Space, Line of Fire, Energy Isolation).
- **How it works:** Similar to the SIF engine, it uses NLP pattern matching to map vocabulary.
- **Context-Aware Exclusions:** The engine intelligently bypasses irrelevant rules based on the report type (e.g., skipping `DRIVING` or `SAFE_MECHANICAL_LIFTING` rule checks if the report is classified as a `Spill`), radically reducing false positives.

## 4. Entity Extraction Engine
This engine leverages the reasoning capabilities of the LLM provider (Google Gemini or Groq).
- **How it works:** It prompts the LLM to act as a strict data extractor, asking it to pull out specific nouns from the text and categorize them into `PERSON`, `EQUIPMENT`, `LOCATION`, and `HAZARD`. 
- **Deduplication:** Extracted entities are deduplicated by consolidating their source offsets into an `occurrences` array, preserving all data locations without cluttering the UI.
- **Output Validation:** The LLM is forced to return strict JSON, which the backend then validates to ensure it perfectly matches the expected entity structure.

## 5. Decision Orchestrator
The final step in the pipeline. It gathers the results from the SIF, LSR, and Entity engines and makes a final judgment.
- **Calculating Confidence:** If the SIF engine generated a high score, but the Entity engine failed to find any `HAZARD` entities, the Decision Engine lowers the overall confidence score.
- **Contradiction Checking:** It actively looks for conflicting conclusions between the deterministic and AI engines.
- **Final Status:** If confidence is low or contradictions exist, it overrides the `COMPLETED` status and marks the report as `REVIEW_REQUIRED`, ensuring a "Human-in-the-Loop" for uncertain data.

## 6. Sequential AI Insights (Summary & Solutions)
Used selectively by the frontend for detailed report views or live analysis.
- **How it works:** Once deterministic calculations are complete, the LLM provides two sequential passes: first, a concise AI Summary that professionally evaluates the SIF status; second, actionable AI Suggestions (preventative solutions) formatted strictly as bullet points.
- **Strict Guardrails:** The LLM is heavily prompted to remain objective and explicitly state "No solution needed" for positive safety observations (e.g., Good Catches).
