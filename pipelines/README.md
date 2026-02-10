# Apollo Data Pipelines

## Overview
This directory contains modular ETL pipelines for ingesting and processing solar site data.
Each pipeline corresponds to a "Phase" in the `WORKPLAN.md`.

## Pipeline Structure
*   `00_base_parcels/`: Base ingestion of MassGIS Level 3 Parcels (WFS -> PostGIS).
*   `01_grid/`: Grid hosting capacity scraping (Grid -> PostGIS).
*   `02_zoning/`: Town bylaw scraping (LLM -> PostGIS).
*   `03_environmental/`: Constraints analysis (Wetlands/NHESP -> PostGIS).
*   `04_physical/`: Topography (LiDAR -> PostGIS).
*   `05_infrastructure/`: Roads/Access checks.
*   `06_legal_social/`: Ownership/Abutters.

## Usage
Activate the Python environment:
```bash
source ../venv/bin/activate
# or
..\venv\Scripts\activate
```

Run a pipeline:
```bash
python -m pipelines.00_base_parcels.ingest
python -m pipelines.01_grid.ingest
```

## Environment Variables
*   `DATABASE_URL`: Connection string for PostGIS (default: `postgresql://apollo:solar_password@localhost:5432/apollo`).
