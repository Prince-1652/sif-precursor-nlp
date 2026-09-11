# Database Architecture

The persistence layer of the SIF Precursor system is built using a highly scalable **PostgreSQL** database managed by SQLAlchemy. 

## Why PostgreSQL?
For a production-grade analytics platform, PostgreSQL is the undisputed choice for scalability and reliability.
- **High Concurrency:** As hundreds of IoT sensors, manual safety entries, and CSV bulk uploads stream into the backend, Postgres easily handles concurrent asynchronous write connections from FastAPI background workers without locking the database.
- **Complex Querying:** The dashboard performs heavy aggregations (e.g., grouping LSR violations, calculating volume trends). PostgreSQL handles these analytical joins exponentially faster than flat-file databases.
- **Future-Proofing:** Postgres natively supports `pgvector` and JSONB, which allows future implementations to store LLM embeddings directly inside the database for semantic search on past safety reports.

## Database Schema & Tables

The schema is highly relational, utilizing One-to-Many relationships to map a single report to multiple predictions and entities.

### 1. `reports` Table
The central hub for all data.
- **Fields:** `id`, `original_text`, `normalized_text`, `report_type`, `processing_status`, `sif_potential`, `risk_band`.
- **Purpose:** Stores the core observation data. The `report_type` field explicitly drives the NLP engines, dynamically scaling Risk Bands and applying Life-Saving Rule exclusions based on context before generating the final aggregated status.

### 2. `sif_predictions` Table
- **Fields:** `id`, `report_id`, `score`, `risk_band`, `is_current`.
- **Purpose:** Stores the exact mathematical output of the SIF Engine. The `is_current` flag allows for versioning—if an algorithm is updated and the report is reprocessed, the old prediction is kept for auditing, but `is_current` is set to false.

### 3. `lsr_predictions` Table
- **Fields:** `id`, `report_id`, `rule_id`, `confidence`, `matched_phrases`.
- **Purpose:** Links a report to a specific Life Saving Rule violation, including the exact text snippet (`matched_phrases`) that triggered the rule.

### 4. `entities` Table
- **Fields:** `id`, `report_id`, `entity_type` (e.g., EQUIPMENT, PERSON), `entity_value`, `context`.
- **Purpose:** Stores the parsed JSON outputs from the LLM Entity Extraction engine.

### 5. `review_actions` Table
- **Fields:** `id`, `report_id`, `reviewer_id`, `decision` (CONFIRM/EDIT/REJECT), `comment`.
- **Purpose:** Provides a complete audit trail for the Human-in-the-Loop system. Every time a user overrides or confirms an AI prediction, a record is stored here for compliance and future model training.

### 6. `processing_jobs` Table
- **Fields:** `id`, `filename`, `status`, `total_records`, `processed_records`.
- **Purpose:** Tracks the progress of bulk CSV uploads. The frontend queries this table to display progress bars during massive data ingestions.
