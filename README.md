# Apollo Solar Site Selection System

## Overview
Apollo is a high-performance Solar Site Selection System for Massachusetts. It identifies viable solar development sites by analyzing geospatial data against strict grid, zoning, environmental, and physical constraints.

## Getting Started
See [SOUL.md](SOUL.md) for detailed setup and contribution guidelines.
See [WORKPLAN.md](WORKPLAN.md) for the project roadmap.
See [update-tracker.md](update-tracker.md) for recent progress.

## Quick Start
1.  Start Database: `docker-compose up -d`
2.  Install Python dependencies: `pip install -r requirements.txt`
3.  Run Base Parcel Ingestion: `python -m pipelines.00_base_parcels.ingest`
4.  Start Frontend: `cd app && npm run dev`

## Architecture
See [docs/architecture.md](docs/architecture.md) for system design.
