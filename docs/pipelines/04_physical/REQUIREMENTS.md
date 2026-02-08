# Physical & Topographical - Requirements & Data Spec

## 1. Objective
Assess the **Constructability** of a parcel based on slope, aspect, and soil conditions. Steep slopes (>15%) require expensive grading and engineering.

**Key Metrics:**
*   **Slope:** < 10% is ideal. 10-15% is marginal. > 15% is often non-viable.
*   **Aspect:** South-facing (180°) is ideal. North-facing (> 315° or < 45°) is penalized.
*   **Soil Type:** Structural stability (avoid peat/hydric soils). Depth to bedrock (blasting risk).
*   **Land Cover:** Forest vs Open. Clearing forest adds cost and permitting complexity.

## 2. Data Sources
| Provider | Dataset Name | Type | URL / Access Method | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **MassGIS** | LiDAR DEM (Digital Elevation Model) | Raster (GeoTIFF) | [MassGIS](https://www.mass.gov/info-details/massgis-data-lidar-dem-2013-2015) | 1m or 2m resolution. Very detailed. |
| **USDA** | SSURGO Soils (Web Soil Survey) | WFS / Shapefile | [USDA NRCS](https://websoilsurvey.sc.egov.usda.gov/App/HomePage.htm) | Standard for hydric soils/bedrock. |
| **MassGIS** | Land Use / Land Cover (2016) | Raster / Vector | [MassGIS](https://www.mass.gov/info-details/massgis-data-land-use-2016) | Distinguish between Forest and Open Land. |

## 3. Ingestion Pipeline Specification
**Script Name:** `ingest_physical.py`

### Step 3.1: Slope & Aspect Analysis
*   **Action:** Process LiDAR DEM Rasters (GDAL/Rasterio).
*   **Process:**
    1.  **Calculate Slope:** Generate slope raster (percent).
    2.  **Calculate Aspect:** Generate aspect raster (degrees).
    3.  **Zonal Statistics:**
        *   For each Parcel:
        *   Calculate `mean_slope`, `max_slope`, `slope_std_dev`.
        *   Calculate `mean_aspect` (circular mean).
        *   Calculate `area_slope_lt_10` (Area with slope < 10%).
        *   Calculate `area_slope_gt_15` (Area with slope > 15%).
*   **Output:** `parcel_slope_stats` table.

### Step 3.2: Soil & Bedrock
*   **Action:** Ingest SSURGO polygons.
*   **Attribute:** `hydric_rating` (Yes/No), `depth_to_bedrock` (cm).
*   **Process:**
    1.  Spatial Intersection: Parcel vs SSURGO.
    2.  Check for `hydric_rating = 'Yes'` (Wetland indicator, often redundant with DEP but good confirmation).
    3.  Check for `depth_to_bedrock < 100cm` (Shallow bedrock -> Blasting risk).
*   **Output:** `parcel_soil_stats` table.

### Step 3.3: Constructability Scoring
*   **Logic:**
    *   `IF area_slope_gt_15_pct > 0.50 THEN status = 'NON_VIABLE'` (Too steep).
    *   `IF land_cover == 'FOREST' THEN clearing_penalty = TRUE` (Adds cost).
    *   `IF depth_to_bedrock < 50cm THEN blasting_risk = TRUE`.

## 4. Final Data Output (JSONB in `parcels` table)
```json
"physical_status": {
  "mean_slope_pct": 5.2,
  "max_slope_pct": 12.0,
  "area_slope_lt_15_pct": 0.95,
  "mean_aspect_deg": 185.0, // South
  "soil_type": "Sandy Loam",
  "hydric_soil": false,
  "depth_to_bedrock_cm": 150,
  "land_cover": "FOREST",
  "status": "VIABLE"
}
```

## 5. Preliminary Research Notes
*   **LiDAR Processing:** Raster processing is CPU/Memory intensive. Use `tiles` or `vrt` to process in chunks.
*   **North Facing Slopes:** While suboptimal for yield, they are buildable. The constraint is economic, not physical. Slope is the hard constraint.
*   **Tree Clearing:** MA has strict rules on forest clearing (SMART program adders/subtractors). Clearing > X acres triggers MEPA review. This pipeline should flag "Forest" parcels for scrutiny.
