# Apollo Implementation Workplan

## Executive Summary
This plan prioritizes "Fail Fast" logic. We build the foundational layers first, then the "Deal Killer" constraints (Grid, Wetlands), followed by the complex Regulatory layer. Visualization is introduced early (MVP) to validate data, then refined.

**Total Estimated Timeline:** ~4-6 Weeks for MVP.

---

## Phase 0: Foundation (The Skeleton)
*Goal: Establish the database and the "Universal Parcel Record".*

*   **Step 0.1: Project & DB Setup**
    *   Init Next.js repo, Python env, Dockerized PostGIS.
    *   **Expectation:** A running local stack.
*   **Step 0.2: Base Parcel Ingestion**
    *   Ingest MassGIS Level 3 Parcels (Standardized).
    *   Normalize schema (Town, Address, Owner, Geom).
    *   **Expectation:** 2M+ rows in PostGIS. We can query "Select * from parcels where town='Amherst'".
*   **Time:** 2 Days.

---

## Phase 1: The "Deal Killers" (Viability Filters)
*Goal: Eliminate the 90% of land that is physically or electrically impossible.*

*   **Step 1.1: Environmental Constraints (Pipeline 03)**
    *   *Why First?* High criticality, easy data (MassGIS WFS).
    *   Ingest Wetlands, 100ft Buffers, NHESP, Flood Zones.
    *   Compute: `usable_area` for every parcel.
    *   **Expectation:** Flag parcels with < 50% usable area as `NON_VIABLE`.
*   **Step 1.2: Grid Interconnection (Pipeline 01)**
    *   *Why Second?* Absolute hard constraint. If no capacity, no project.
    *   Scrape/Ingest National Grid & Eversource Hosting Maps.
    *   Compute: Join circuits to parcels. Filter for Green/Yellow.
    *   **Expectation:** A massive filter that drops ~60% of remaining parcels.
*   **Time:** 1 Week.

---

## Phase 2: Visualization MVP (The "See It" Milestone)
*Goal: Validate Phase 1 data on a map before building complex scrapers.*

*   **Step 2.1: Basic Dashboard**
    *   Next.js + Mapbox GL JS.
    *   Vector Tiles generation (Tipper/Mbtiles) for performance.
    *   **Expectation:** A map where I can click a parcel and see: "Grid: Green, Wetland: 40%".
*   **Time:** 3 Days.

---

## Phase 3: Regulatory (The "Hard" Filter)
*Goal: Tackle the unstructured data challenge (Zoning).*

*   **Step 3.1: Zoning & Bylaws (Pipeline 02)**
    *   *Why Later?* Hardest technical task (LLM/PDF Scraping). We only want to run this costly compute on parcels that survived Phase 1.
    *   Ingest MassGIS Zoning Polygons (Geometry).
    *   Build LLM Pipeline to scrape Town Bylaws for Setbacks/Use Tables.
    *   **Expectation:** A structured rules engine. "Town X allows Solar by Right in Industrial Zone".
*   **Time:** 1.5 Weeks.

---

## Phase 4: Constructability & Cost (Refinement)
*Goal: Filter out "Technically viable but too expensive to build" sites.*

*   **Step 4.1: Physical/Topography (Pipeline 04)**
    *   Ingest LiDAR (Raster).
    *   Compute Slope & Aspect.
    *   **Expectation:** Discard North-facing steep cliffs.
*   **Step 4.2: Infrastructure (Pipeline 05)**
    *   Check Road Frontage and Access.
    *   **Expectation:** Ensure we can physically access the site.
*   **Time:** 1 Week.

---

## Phase 5: Legal & Social (Risk Adjustment)
*Goal: Assess "Soft" risks.*

*   **Step 5.1: Legal & Social (Pipeline 06)**
    *   Check Ownership (Municipal/Private).
    *   Check CR/APR status (Protected land).
    *   Calculate Abutter Density (NIMBY score).
    *   **Expectation:** A "Risk Score" (0-100) for every viable parcel.
*   **Time:** 3 Days.

---

## Phase 6: Production Polish
*Goal: Launch.*

*   **Step 6.1: UI Polish**
    *   Advanced Filtering (Slider for "Distance to Substation").
    *   Saved Searches / Alerts.
*   **Step 6.2: Automation**
    *   Set up cron jobs to refresh Grid/Parcel data monthly.
*   **Time:** 1 Week.

---

## Summary of Milestones

1.  **Milestone 1 (Week 1):** Database live with Base Parcels + Wetlands + Grid. (We can technically find sites now).
2.  **Milestone 2 (Week 2):** UI Dashboard live. We can visualize the data.
3.  **Milestone 3 (Week 4):** Zoning data integrated. The "Holy Grail" of datasets.
4.  **Milestone 4 (Week 6):** Full Constructability + Risk scoring. Production Ready.
