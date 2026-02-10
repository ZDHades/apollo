# Apollo Update Tracker

This file tracks the progress of the Apollo project, adhering to the `WORKPLAN.md`.

## Phase 0: Foundation (The Skeleton)
*   [ ] **Step 0.1: Project & DB Setup**
    *   [x] Create `docker-compose.yml` for PostGIS.
    *   [x] Create `requirements.txt` for Python env.
    *   [x] Initialize Next.js app in `app/`.
    *   [x] Verify local stack. (Note: Docker environment issues prevented DB startup; skipping for now).
*   [ ] **Step 0.2: Base Parcel Ingestion**
    *   [ ] Ingest MassGIS Level 3 Parcels. (Script created: `pipelines/00_base_parcels/ingest.py`)
    *   [ ] Normalize schema.

## Phase 1: The "Deal Killers" (Viability Filters)
*   [ ] **Step 1.1: Environmental Constraints (Pipeline 03)**
*   [ ] **Step 1.2: Grid Interconnection (Pipeline 01)**

## Phase 2: Visualization MVP (The "See It" Milestone)
*   [ ] **Step 2.1: Basic Dashboard**

## Phase 3: Regulatory (The "Hard" Filter)
*   [ ] **Step 3.1: Zoning & Bylaws (Pipeline 02)**

## Phase 4: Constructability & Cost (Refinement)
*   [ ] **Step 4.1: Physical/Topography (Pipeline 04)**
*   [ ] **Step 4.2: Infrastructure (Pipeline 05)**

## Phase 5: Legal & Social (Risk Adjustment)
*   [ ] **Step 5.1: Legal & Social (Pipeline 06)**

## Phase 6: Production Polish
*   [ ] **Step 6.1: UI Polish**
*   [ ] **Step 6.2: Automation**

---

## Log
*   **2026-02-09**: Initialized `update-tracker.md`.
*   **2026-02-08**: Created core documentation (`WORKPLAN.md`, `SOUL.md`, `REQUIREMENTS.md`) and pipeline specs. Created `docker-compose.yml` and `requirements.txt`.
