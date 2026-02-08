# Environmental Constraints - Requirements & Data Spec

## 1. Objective
Identify **Critical Environmental Constraints** that reduce buildable area or prohibit development entirely.
Wetlands are the #1 killer of solar deals in MA.

**Key Metrics:**
*   **Wetlands:** Presence of bordering vegetated wetlands (BVW).
*   **Buffer Zone:** 100ft jurisdictional buffer around wetlands (often no-build or restricted).
*   **Riverfront Area:** 200ft buffer around perennial streams (strictly regulated).
*   **NHESP:** Priority Habitats of Rare Species (PH) & Estimated Habitats (EH). Triggers MESA review.
*   **Flood Zones:** FEMA A/AE/V zones (high insurance/risk).
*   **Vernal Pools:** Certified (CVP) or Potential (PVP). 100ft buffer applies.

## 2. Data Sources
| Provider | Dataset Name | Type | URL / Access Method | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **MassGIS** | DEP Wetlands (1:12,000) | WFS / Shapefile | [MassGIS](https://www.mass.gov/info-details/massgis-data-massdep-wetlands-112000) | The legal standard for desktop review. |
| **MassGIS** | NHESP Priority Habitats | WFS / Shapefile | [MassGIS](https://www.mass.gov/info-details/massgis-data-nhesp-priority-habitats-of-rare-species) | Updated every few years (14th/15th Edition). |
| **MassGIS** | FEMA National Flood Hazard Layer | WFS / Shapefile | [MassGIS](https://www.mass.gov/info-details/massgis-data-fema-national-flood-hazard-layer) | Critical for insurance/financing. |
| **MassGIS** | Certified Vernal Pools | WFS / Shapefile | [MassGIS](https://www.mass.gov/info-details/massgis-data-nhesp-certified-vernal-pools) | Strict protection. |

## 3. Ingestion Pipeline Specification
**Script Name:** `ingest_environmental.py`

### Step 3.1: Layer Acquisition & Buffering
*   **Action:** Ingest Wetland, River, Vernal Pool polygons.
*   **Process:**
    *   **Buffer:** Create a 100ft buffer around all Wetland/VP polygons.
    *   **Buffer:** Create a 200ft buffer around Perennial Streams.
    *   **Union:** Merge all constraint geometries into a single `environmental_exclusions` layer.
*   **Output:** `environmental_exclusions` (PostGIS MultiPolygon).

### Step 3.2: Parcel Intersection
*   **Logic:**
    1.  For each Parcel:
    2.  Calculate `total_area_sqft`.
    3.  Intersect Parcel Geom with `environmental_exclusions`.
    4.  Calculate `excluded_area_sqft`.
    5.  `usable_area_sqft = total_area_sqft - excluded_area_sqft`.
    6.  `usable_pct = usable_area_sqft / total_area_sqft`.
*   **Constraint Check:**
    *   `IF usable_pct < 0.40 THEN status = 'NON_VIABLE'` (Too much wetland).
    *   `IF intersects(NHESP) THEN flag = 'MESA_REVIEW'` (Adds cost/time).

## 4. Final Data Output (JSONB in `parcels` table)
```json
"enviro_status": {
  "wetlands_overlap_pct": 0.15,
  "wetlands_buffer_overlap_pct": 0.30,
  "nhesp_overlap": false,
  "flood_zone": "X", // X is good, A/AE is bad
  "vernal_pools_count": 0,
  "usable_acres": 12.5,
  "status": "VIABLE",
  "flags": ["WETLAND_BUFFER_IMPACT"]
}
```

## 5. Preliminary Research Notes
*   **Wetland Accuracy:** MassGIS data is interpreted from aerial photos. It is *conservative* but not definitive. Always visually verify with satellite imagery (leaf-off spring photos are best).
*   **MESA Review:** Priority Habitat doesn't mean "No". It means "Ask NHESP". Often manageable for solar if you avoid the specific habitat features (e.g., turtle nesting sites).
