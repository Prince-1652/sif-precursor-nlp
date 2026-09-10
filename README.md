# SIF Precursor Detection System

An advanced, AI-augmented safety analytics platform designed to proactively identify Serious Injury and Fatality (SIF) precursors from raw, unstructured field safety observations.

## Project Overview

Safety reports are often messy, written in local slang (like Hinglish), and lack standard categorization. This system solves that problem by providing a massive-scale ingestion pipeline that reads raw text, translates and normalizes it, and runs it through a set of highly optimized deterministic and AI engines to extract Life Saving Rule (LSR) violations, key entities, and ultimately assign a SIF Risk Band.

The project features a sleek, real-time dashboard for EHS (Environment, Health, and Safety) managers, providing drill-down analytics and a Human-in-the-Loop review process to ensure AI accuracy.

---

## Comprehensive Documentation

To understand the specific layers of this platform, please refer to the detailed architecture and flow documents linked below:

- **[System Architecture](file:///architecture.md):** Complete overview of the decoupled client-server architecture, highlighting the separation of Next.js and FastAPI.
- **[Technology Stack](file:///tech_stack.md):** The full list of technologies used across the stack and the explicit justifications for choosing them over alternatives.
- **[Application Flow](file:///flow.md):** A detailed step-by-step breakdown (with sequence diagrams) of how data moves from a user's upload all the way through the backend database.
- **[Core Engines](file:///engines.md):** Deep dive into the 5 distinct processing engines (Language Gate, SIF Engine, LSR Engine, Entity Extraction, Decision Orchestrator).
- **[Frontend Architecture](file:///frontend.md):** Details on the Next.js App Router setup, React components, and client-side URL filtering.
- **[Backend Architecture](file:///backend.md):** Details on the FastAPI routing, Pydantic validation, and background task queues.
- **[Database Schema](file:///database.md):** Overview of the SQLite persistence layer, ORM mapping, and table definitions.

---

## API Endpoints

The FastAPI backend exposes the following primary REST endpoints:

### Ingestion & Processing
- **`POST /api/v1/reports/upload`**
  - **Description:** Upload a bulk CSV file of historical safety reports.
  - **Behavior:** Validates file size, saves to SQLite, and instantly spins off an async `BackgroundTasks` queue to process rows without blocking the client.
- **`POST /api/v1/reports/manual`**
  - **Description:** Submit a single safety report as a JSON payload.
  - **Behavior:** Hashes the text for deduplication. If new, it creates a `READY` record and triggers background processing.
- **`POST /api/v1/reports/analyze`**
  - **Description:** Synchronous testing endpoint. Runs text through the entire pipeline (Language Gate -> Engines -> Decision) and returns raw JSON without saving to the database.

### Dashboard & Analytics
- **`GET /api/v1/analytics/dashboard`**
  - **Description:** Fetches aggregated metrics for the UI metric cards (Total Reports, SIF Potential, High Risk, Pending Review) and data for the Recharts visualizations.

### Report Management & Review
- **`GET /api/v1/reports`**
  - **Description:** Retrieves a paginated list of all safety reports.
- **`GET /api/v1/reports/{id}`**
  - **Description:** Retrieves the complete drill-down details of a specific report, including its original text, normalized text, extracted entities, and LSR violations.
- **`POST /api/v1/reports/{id}/review`**
  - **Description:** The Human-in-the-Loop endpoint. Allows a user to submit a decision (`CONFIRM`, `EDIT`, or `REJECT`) which updates the report's `processing_status` and logs an audit trail.

---

## Setup & Run Instructions

### 1. Backend Setup
1. Open a terminal and navigate to the `backend/` directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### 2. Frontend Setup
1. Open a new terminal and navigate to the `frontend/` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the Next.js development server:
   ```bash
   npm run dev
   ```

### 3. Unified Runner (Optional)
A custom Python script `run.py` is provided in the root directory to kill hanging ports and spin up both the frontend and backend simultaneously.
```bash
python run.py
```
