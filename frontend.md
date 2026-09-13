# Frontend Application

The SIF Precursor frontend is a highly interactive, beautifully designed single-page application built on top of the **Next.js 14 App Router**. It is responsible for data ingestion (uploading reports), data visualization (dashboards), and the human-in-the-loop review interface.

## Directory Structure
```text
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx         # Root layout (Sidebar, Top Navigation)
│   │   ├── page.tsx           # Dashboard (MetricCards, Recharts)
│   │   ├── error.tsx          # Component-level error boundary
│   │   ├── global-error.tsx   # Root-level fallback UI
│   │   ├── reports/
│   │   │   ├── page.tsx       # Drill-down reports table with URL-based filtering
│   │   │   └── [id]/page.tsx  # Detailed review screen for a specific report
│   ├── components/            # Reusable UI components (MetricCard, etc.)
│   └── types/                 # TypeScript interfaces for API responses
└── tailwind.config.ts         # Utility styling configuration
```

## Core Components

### 1. Dashboard (`/page.tsx`)
The dashboard is the landing page. It fetches the `/api/v1/analytics/dashboard` endpoint and renders:
- **Top Metrics:** Four `MetricCard` components showing "Total Reports", "SIF Potential", and "Pending Review". These cards act as dynamic links—clicking "SIF Potential" pushes the user to `/reports?riskFilter=SIF`. 
- **Visualizations:** Uses `recharts` to render a BarChart for Monthly Trends and a PieChart for the distribution of Life Saving Rules violations.

### 2. Ingestion (`/ingestion/page.tsx`)
The primary data intake screen for single or bulk operations.
- **Upload Dropzone:** Upload a CSV for bulk processing via background tasks.
- **Manual Text Input:** A form to paste or type a single safety observation. Clicking "Analyze" sends the payload and safely redirects to the reports table using `useEffect` hooks.

### 3. Reports Table (`/reports/page.tsx`)
This page fetches the `/api/v1/reports` endpoint to display a comprehensive list of all observations. 
- **URL-Driven State:** It reads `searchParams` (`statusFilter` and `riskFilter`) directly from the URL. This allows users to bookmark specific views (e.g., "Show me all Pending SIF reports").
- **Real-time Filtering:** A client-side `.filter()` method reacts instantly to the search box, updating the table without needing a full server round-trip.

### 4. Review Interface (`/reports/[id]/page.tsx`)
When a report is clicked, the user enters the drill-down view.
- **Split View:** The screen is divided. The left side displays the AI Summary. The right side displays the AI Suggestions, extracted entities (People, Hazards), and Life Saving Rules.
- **Concurrency Control:** The "Override / Edit" button is intelligently disabled while AI insights are being generated to prevent race conditions and duplicate API calls.
- **Action Buttons:** At the bottom, the user can override the AI by clicking "Confirm" or "Edit", which POSTs back to the backend and updates the `review_actions` table.

### 5. Live Analysis Sandbox (`/analyze/page.tsx`)
A testing ground to observe the pipeline in real-time.
- **Pure Sandbox:** Metadata inputs (like Source ID or Date) are intentionally stripped from the UI to focus strictly on text extraction algorithms. Clicking "Analyze" fetches live SIF predictions, AI Summaries, and AI Suggestions.
- **Auto-Retry Resilience:** Includes an intelligent `fetch` retry loop. If the backend is actively reloading due to a code change (triggering a Next.js `500 ECONNREFUSED` proxy error), the frontend waits and auto-retries, preventing crash screens during rapid development.

## Error Boundaries
To ensure the app never crashes to a blank white screen (a common issue in SPAs), robust Next.js error boundaries are implemented.
- `error.tsx` catches runtime rendering errors within specific route segments and displays a localized "Something went wrong" UI with a `reset()` button.
- `global-error.tsx` acts as the final safety net for the entire application.
