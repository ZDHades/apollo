# Grid Interconnection - Requirements & Data Spec

## 1. Objective
Determine the **Grid Viability** of every parcel in MA. A parcel is viable if it can connect to a circuit with available hosting capacity (MW) and appropriate voltage/phase, without triggering expensive upgrades.

**Key Metrics:**
*   **Hosting Capacity (MW):** > 0 required (ideally > 1-5 MW).
*   **Voltage:** Preference for 13.8kV or higher distribution voltages.
*   **Phases:** 3-Phase lines are mandatory for MW-scale projects.
*   **Distance:** Proximity to Substation or 3-Phase Line (< 1-2 miles).
*   **Utility:** National Grid (NGRID) vs Eversource (ES).

## 2. Data Sources
| Provider | Dataset Name | Type | URL / Access Method | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Eversource** | MA Hosting Capacity Map | ArcGIS REST / CSV | [OpenEnergyDataPortal](https://openenergyhub.ornl.gov/) or ES Portal | Often updated monthly. Contains circuit-level capacity. |
| **National Grid** | System Data Portal | ArcGIS REST / CSV | [NGRID Portal](https://ngrid-system-data-portal.com/) | Look for "Hosting Capacity" layer. |
| **MassGIS** | Transmission Lines | WFS / Shapefile | MassGIS | For high-voltage context (usually too high for DG). |
| **OpenStreetMap** | Power Infrastructure | PBF / Overpass | OpenStreetMap | Good for locating substations if utility data is missing. |

## 3. Ingestion Pipeline Specification
**Script Name:** `ingest_grid_capacity.py`

### Step 3.1: Fetch & Normalize
*   **Action:** Connect to Utility ArcGIS REST endpoints or download CSVs.
*   **Schema Normalization:**
    *   Map `Circuit_ID` / `Feeder_ID` to a common field.
    *   Map `Available_MW` / `Hosting_Capacity_MW` to `capacity_mw` (Float).
    *   Map `Voltage_kV` to `voltage_kv` (Float).
    *   Map `Phases` (e.g., "3", "1", "ABC") to `phases` (Integer: 1 or 3).
*   **Output:** `grid_circuits` (PostGIS Table) with geometry (LineString or Polygon representing the feeder service area).

### Step 3.2: Substation Proximity
*   **Action:** Ingest Substation points from Utility data or OSM.
*   **Compute:** Calculate distance from Parcel Centroid to nearest Substation.
*   **Output:** Update `grid_substations` table.

### Step 3.3: Parcel Association (The "Spatial Join")
*   **Logic:**
    1.  For each Parcel in `parcels` table:
    2.  Find intersecting or nearest `grid_circuits` geometry.
    3.  Assign `circuit_id`, `utility`, `capacity_mw`, `voltage`, `phases`.
    4.  Calculate `distance_to_3phase` (if circuit geometry is precise lines) or `distance_to_substation`.
*   **Constraint Check:**
    *   `IF capacity_mw <= 0 THEN status = 'CONGESTED'`
    *   `IF phases < 3 THEN status = 'SINGLE_PHASE_Risk'`
    *   `IF distance > 3km THEN status = 'FAR_INTERCONNECT'`

## 4. Final Data Output (JSONB in `parcels` table)
```json
"grid_status": {
  "utility": "Eversource",
  "circuit_id": "21-505",
  "capacity_mw": 3.5,
  "voltage_kv": 13.8,
  "phases": 3,
  "distance_substation_km": 1.2,
  "status": "VIABLE", // or "CONGESTED", "REVIEW"
  "last_updated": "2023-10-27"
}
```

## 5. Preliminary Research Notes
*   **Eversource:** Uses a "Heat Map" approach. Polygons often represent feeder sections. We need to grab the attribute table behind these polygons.
*   **National Grid:** Often provides "feeders" as LineStrings. Buffer these lines by ~50ft to join to parcels, or find nearest line.
*   **Data Gaps:** Some areas may lack digital circuit maps. In these cases, `Distance to Substation` is the proxy metric.
