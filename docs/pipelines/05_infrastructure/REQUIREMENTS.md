# Infrastructure & Access - Requirements & Data Spec

## 1. Objective
Verify **Site Access** for construction and maintenance. A perfect site is useless if you can't get a truck to it legally.

**Key Metrics:**
*   **Frontage:** Legal road frontage (ft). Usually > 50ft required.
*   **Access Road:** Width/condition of public way (Paved vs Dirt).
*   **Weight Limits:** Bridges/Culverts rated < 20 tons (Concrete trucks are heavy).
*   **Scenic Roads:** Designated scenic byways (tree cutting restrictions).
*   **Distance to Major Road:** Proximity to State/Interstate highways (logistics cost).

## 2. Data Sources
| Provider | Dataset Name | Type | URL / Access Method | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **MassDOT** | Roads (2020) | WFS / Shapefile | [MassDOT](https://www.mass.gov/info-details/massgis-data-massdot-roads) | Detailed attributes (width, speed limit, lanes). |
| **MassGIS** | Bridges | WFS / Shapefile | [MassGIS](https://www.mass.gov/info-details/massgis-data-bridges) | Includes weight restrictions. |
| **MassGIS** | Scenic Byways | WFS / Shapefile | [MassGIS](https://www.mass.gov/info-details/massgis-data-scenic-byways) | Specific designation for scenic routes. |

## 3. Ingestion Pipeline Specification
**Script Name:** `ingest_infrastructure.py`

### Step 3.1: Road Analysis
*   **Action:** Ingest MassDOT Roads.
*   **Process:**
    1.  **Buffer:** Buffer roads by 10ft (to ensure intersection).
    2.  **Spatial Join:** Intersect Parcel boundary with Road buffer.
    3.  **Calculate Frontage:** Length of intersection (Parcel Polygon Exterior Ring vs Road Line).
*   **Output:** `parcel_frontage_ft` (Float).

### Step 3.2: Weight Limits
*   **Action:** Ingest Bridge data.
*   **Process:**
    1.  Identify bridges on the *path* to the site (Advanced: Network Analysis).
    2.  Simpler approach (MVP): Flag any weight-restricted bridges within 1 mile radius.
*   **Output:** `weight_limit_warning` (Boolean).

### Step 3.3: Scenic Road Check
*   **Action:** Ingest Scenic Byways layer.
*   **Process:**
    1.  Intersect Parcel Frontage with Scenic Byway Line.
    2.  If intersects: `scenic_road_flag = TRUE`.
*   **Output:** `scenic_road_status` (Boolean).

## 4. Final Data Output (JSONB in `parcels` table)
```json
"infrastructure_status": {
  "frontage_ft": 150.5,
  "access_road_name": "Main Street",
  "road_type": "Minor Arterial",
  "scenic_road": false,
  "weight_limit_bridge_nearby": false,
  "distance_to_highway_mi": 2.5,
  "status": "VIABLE"
}
```

## 5. Preliminary Research Notes
*   **Frontage Calculation:** GIS frontage calculation can be tricky due to digitizing errors (gaps between parcel and road centerline). Use a generous buffer (e.g., 20-30ft) around the road centerline to catch the parcel boundary.
*   **"Paper Streets":** Some roads exist on maps but are unbuilt (paper streets). Check `MassDOT_Roads.SURFACE_TYPE` (e.g., Unimproved/Earth). Avoid parcels with only "paper street" access.
