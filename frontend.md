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

### 2. Reports Table (`/reports/page.tsx`)
This page fetches the `/api/v1/reports` endpoint to display a comprehensive list of all observations. 
- **URL-Driven State:** It reads `searchParams` (`statusFilter` and `riskFilter`) directly from the URL. This allows users to bookmark specific views (e.g., "Show me all Pending SIF reports").
- **Real-time Filtering:** A client-side `.filter()` method reacts instantly to the search box, updating the table without needing a full server round-trip.

### 3. Review Interface (`/reports/[id]/page.tsx`)
When a report is clicked, the user enters the drill-down view.
- **Split View:** The screen is divided. The left side displays the raw, unaltered text entered by the field worker. The right side displays the AI's deductions: exact text snippets that triggered SIF rules, extracted entities (People, Hazards), and the Final Risk Score.
- **Action Buttons:** At the bottom, the user can override the AI by clicking "Confirm", "Reject", or "Edit", which POSTs back to the backend and updates the `processing_status`.

## Error Boundaries
To ensure the app never crashes to a blank white screen (a common issue in SPAs), robust Next.js error boundaries are implemented.
- `error.tsx` catches runtime rendering errors within specific route segments and displays a localized "Something went wrong" UI with a `reset()` button.
- `global-error.tsx` acts as the final safety net for the entire application.
