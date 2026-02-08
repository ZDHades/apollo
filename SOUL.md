# Apollo Project Soul & Developer Guide

**Mission:** Build the "Single Pane of Glass" for Solar Site Selection in Massachusetts.
**Mantra:** "Fail Fast." Eliminate the 90% of non-viable land immediately (Grid/Wetlands) before spending compute on the complex 10% (Zoning).

---

## 🛠 Tool Preferences & Protocols

### Git Workflow (CRITICAL)
All agents/developers must follow this sequence for every change:
1.  `git add .` (Stage all changes).
2.  `git commit -m "type: Description"` (Use Conventional Commits: `feat`, `fix`, `docs`, `chore`, `refactor`).
3.  `git push` (Push to current branch).
    *   *If remote is missing:* Report it but proceed.
    *   *If conflict:* Pull --rebase, resolve, then push.

### Python (Backend/ETL)
*   **Style:** PEP8. Use `black` for formatting.
*   **Type Hinting:** Required for all function arguments and returns.
*   **Libraries:**
    *   `geopandas` for vector operations.
    *   `rasterio` for raster/LiDAR.
    *   `sqlalchemy` / `geoalchemy2` for DB interactions.
    *   `pydantic` for data validation.

### JavaScript/TypeScript (Frontend)
*   **Framework:** Next.js (App Router).
*   **Map Library:** Mapbox GL JS (or MapLibre).
*   **Styling:** Tailwind CSS.
*   **Linting:** ESLint + Prettier.

---

## 🧠 Research & Context (The "Tribal Knowledge")

### Massachusetts Nuances
*   **"Home Rule":** MA is a "Home Rule" state. Towns have immense power. Zoning bylaws override state suggestions unless specific laws (like M.G.L. c. 40A, § 3 - The Dover Amendment, though Solar has its own protections under Section 3) apply.
*   **Wetlands:** The 100ft buffer zone is often a "No Disturb" zone, not just a "buffer". Treat it as a hard exclusion for solar arrays unless the town explicitly allows it.
*   **Grid Transparency:** National Grid and Eversource maps are *estimates*. They are not real-time. "Green" means "Likely Viable", not "Guaranteed".

### Data Source Quirks
*   **MassGIS:** The `Level 3 Parcel` data is the gold standard for boundaries but often lags 1-2 years on ownership.
*   **Utility Maps:** Often hidden behind ArcGIS REST endpoints that change URLs. If a scraper fails, check the "Network" tab in the browser developer tools on their hosting map site.

---

## 🏗 Architecture & Design

### The "Universal Parcel Record"
*   **Central Truth:** The `parcels` table in PostGIS is the source of truth.
*   **Pattern:** "Enrichment". Pipelines do not *create* parcels; they *enrich* existing parcel records with new JSONB attribute blocks (`grid_status`, `enviro_status`).
*   **Idempotency:** All ingestion scripts must be idempotent. Running them twice should not duplicate data or crash.

### Directory Structure
*   `pipelines/`: Standalone Python modules for each data domain.
*   `app/`: Next.js frontend.
*   `api/`: FastAPI backend (if separate from Next.js API routes).
*   `data/`: Local cache for raw downloads (gitignored).

---

## 🚀 Running the Project (WIP)

### Prerequisites
1.  **Docker:** Required for PostGIS.
2.  **Python 3.10+:** Use `venv`.
3.  **Node.js 18+:** For frontend.

### Environment Setup
1.  **Database:**
    ```bash
    docker run --name apollo-db -e POSTGRES_PASSWORD=solar -d -p 5432:5432 postgis/postgis
    ```
2.  **Python Env:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate
    pip install -r requirements.txt
    ```

### Running Pipelines (Example)
```bash
# Activate env
source venv/bin/activate

# Run Grid Ingestion
python -m pipelines.01_grid.ingest
```

### Running Frontend
```bash
cd app
npm install
npm run dev
```
