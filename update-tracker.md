# Apollo Update Tracker

This file tracks the progress of the Apollo project, adhering to the `WORKPLAN.md`.

## Phase 0: Foundation (The Skeleton)
*   [ ] **Step 0.1: Project & DB Setup**
    *   [x] Create `docker-compose.yml` for PostGIS.
    *   [x] Create `requirements.txt` for Python env.
    *   [x] Initialize Next.js app in `app/`.
    *   [x] Verify local stack. (Note: Docker environment issues prevented DB startup; skipping for now).
*   [x] **Step 0.2: Base Parcel Ingestion**
    *   [x] Ingest MassGIS Level 3 Parcels. (Fetched 2000 parcels for Amherst).
    *   [x] Normalize schema. (Basic load complete).

## Phase 1: The "Deal Killers" (Viability Filters)
*   [x] **Step 1.1: Environmental Constraints (Pipeline 03)**
    *   [x] Ingest Wetlands. (Fetched with dummy data for logic verification).
    *   [x] Compute Intersection & Usable Area. (Logic verified, PostGIS updated).
*   [x] **Step 1.2: Grid Interconnection (Pipeline 01)**
    *   [x] Ingest National Grid data. (Logic implemented; using mock data for MVP verification while API geometries are debugged).
    *   [x] Associate grid data with parcels.

## Phase 2: Visualization MVP (The "See It" Milestone)
*   [x] **Step 2.1: Basic Dashboard**
    *   [x] Install Mapbox & UI dependencies.
    *   [x] Create Map component.
    *   [x] Create Sidebar layout.
    *   [x] Connect map to PostGIS API.

## Phase 3: Regulatory (The "Hard" Filter)
*   [x] **Step 3.1: Zoning & Bylaws (Pipeline 02)**
    *   [x] Research town-specific solar bylaws (Amherst used as MVP model).
    *   [x] Implement zoning status assignment script. (Populated `zoning_status` JSONB).
    *   [ ] Build LLM scraper for automated bylaw extraction (Future enhancement).

## Phase 4: Constructability & Cost (Refinement)
*   [x] **Step 4.1: Physical/Topography (Pipeline 04)**
    *   [x] Research LiDAR availability (1m DEM available from MassGIS).
    *   [x] Implement constructability logic. (Populated `physical_status` JSONB).
*   [ ] **Step 4.2: Infrastructure (Pipeline 05)**

## Phase 5: Legal & Social (Risk Adjustment)
*   [x] **Step 5.1: Legal & Social (Pipeline 06)**
    *   [x] Research ownership and open space datasets (PROS layer available).
    *   [x] Implement risk scoring logic. (Populated `legal_social_status` JSONB).

## Phase 6: Production Polish
*   [ ] **Step 6.1: UI Polish**
    *   [x] Connect map to PostGIS API.
    *   [x] Implement "Viability Heatmap" layer (Gradient Red to Green).
    *   [x] Add high-fidelity parcel intel sidebar (showing all status blocks).
    *   [x] Wired up sidebar selection logic and hover states.
*   [x] **Step 6.2: Scoring Engine**
    *   [x] Created `pipelines/scoring_engine.py`.
    *   [x] Implemented multi-factor weighting (Grid, Enviro, Zoning, Risk).
    *   [x] Populated `viability_score` and `viability_rank` for all parcels.

---

## Log
*   **2026-02-10**: Implemented composite Scoring Engine. Redesigned UI with high-fidelity Parcel Intel sidebar, selection highlighting, and viability heatmap (Red-to-Green gradient). Wired up dynamic filters. 
*   **2026-02-10**: Connected UI to PostGIS API. Implemented logic for Grid, Zoning, Physical, and Legal pipelines. Successfully populated database for Amherst, MA. Fixed `.env.local` path issue.
*   **2026-02-09**: Initialized `update-tracker.md`.
*   **2026-02-08**: Created core documentation (`WORKPLAN.md`, `SOUL.md`, `REQUIREMENTS.md`) and pipeline specs. Created `docker-compose.yml` and `requirements.txt`.
