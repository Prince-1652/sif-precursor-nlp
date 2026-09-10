# Backend Application

The SIF Precursor backend is the computational powerhouse of the system, built with **FastAPI**. It manages data ingestion, coordinates the complex AI pipeline, handles database persistence, and exposes RESTful endpoints for the frontend.

## Directory Structure
```text
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── analytics.py   # Dashboard aggregation queries
│   │   │   └── reports.py     # Upload, manual creation, and review endpoints
│   ├── core/
│   │   ├── config.py          # Environment variables and Pydantic BaseSettings
│   │   └── security.py        # Rate limiting and CORS configurations
│   ├── engines/               # The AI and Deterministic logic (SIF, LSR, etc.)
│   ├── models/                # SQLAlchemy database schema definitions
│   ├── schemas/               # Pydantic validation models for HTTP requests
│   └── services/              # Orchestration logic linking endpoints to engines
├── tests/                     # Pytest suite
└── main.py                    # FastAPI application entry point
```

## Key Architectural Concepts

### 1. Asynchronous I/O (`async` / `await`)
Safety report processing is heavily I/O bound (making HTTP calls to external LLMs and executing database queries). FastAPI natively supports `asyncio`, allowing the server to handle thousands of concurrent requests without blocking the main thread.

### 2. Background Tasks
When a user uploads a CSV containing 500 reports, processing them synchronously would cause a timeout. Instead, the `POST /api/v1/reports/upload` endpoint instantly returns a `202 Accepted` response with a `job_id`. 
The actual parsing and engine execution is passed to a FastAPI `BackgroundTasks` queue, which runs the `process_pending_reports` function silently in the background.

### 3. Pydantic Validation
Every incoming request (e.g., submitting a manual report or a review decision) is strictly validated against a Pydantic schema in `app/schemas/`. If the frontend accidentally sends an integer where a string is expected, FastAPI immediately intercepts the bad request and returns a structured `422 Unprocessable Entity` error, protecting the database from malformed data.

### 4. SQLAlchemy ORM & Alembic
The backend uses SQLAlchemy to interact with the SQLite database. Rather than writing raw SQL, the logic relies on object-oriented queries. 
Example from Analytics Aggregator:
```python
high_risk_count = db.query(SIFPrediction).filter(
    SIFPrediction.is_current == True, 
    SIFPrediction.risk_band == "HIGH"
).count()
```
This abstracts away the underlying SQL dialect, meaning the entire system could be pointed to a PostgreSQL database by simply changing the `DATABASE_URL` in the `.env` file.

## Testing Strategy
The backend is fortified by a comprehensive `pytest` suite located in the `tests/` directory.
- Tests mock the external LLM calls (using `unittest.mock.patch`), ensuring that the test suite runs in under 1 second, costs $0, and does not fail if the internet disconnects.
- Features like `pytest-asyncio` are used to test the asynchronous pipeline functions effectively.
