# Zoning & Regulatory - Requirements & Data Spec

## 1. Objective
Assess the **Permitting Viability** of a parcel based on local zoning bylaws and land use regulations. Solar development is highly sensitive to municipal rules.

**Key Metrics:**
*   **Zoning District:** Code (e.g., "R1", "I", "C"). Industrial/Commercial > Residential.
*   **Allowable Use:** "By Right", "Special Permit" (SP), "Site Plan Review" (SPR), or "Prohibited".
*   **Setbacks:** Front/Side/Rear setbacks (ft).
*   **Overlay District:** Solar overlay, aquifer protection overlay (often restricts).
*   **Minimum Lot Size:** e.g., 5 acres for large-scale ground mount.

## 2. Data Sources
| Provider | Dataset Name | Type | URL / Access Method | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **MassGIS** | Level 3 Standardized Zoning (Parcel-Based) | WFS / Shapefile | [MassGIS](https://www.mass.gov/info-details/massgis-data-land-use-2005) | Good baseline but lacks specific bylaw text. |
| **Town GIS** | Local Zoning Maps | WFS / PDF | Varied (Scraping needed) | Often more current than MassGIS. |
| **Town Websites** | Zoning Bylaws / Ordinances | PDF / Text | Varied (Scraping needed) | **Critical:** Contains the rules. |
| **Smart Solar MA** | Solar Bylaw Database | Database / CSV | (Proprietary/Public?) | Potential goldmine if accessible. |

## 3. Ingestion Pipeline Specification
**Script Name:** `ingest_zoning.py`

### Step 3.1: Base Zoning Map (Geometric)
*   **Action:** Ingest MassGIS Level 3 Standardized Zoning Polygons.
*   **Schema Normalization:**
    *   Map `ZONE_CODE` to internal `zone_code`.
    *   Map `ZONE_DESC` to `zone_desc`.
    *   Map `USE_CODE` to `use_code` (Residential, Commercial, Industrial).
*   **Output:** `zoning_polygons` (PostGIS Table).

### Step 3.2: Bylaw Text Analysis (The Hard Part)
*   **Action:** Scrape zoning bylaw PDFs for target towns.
*   **Process:**
    1.  Convert PDF to Text.
    2.  Use LLM (GPT-4/Claude) to extract structured rules for "Large-Scale Ground Mounted Solar Photovoltaic Installations".
    3.  Extract: `allowed_districts`, `setbacks`, `max_coverage`, `special_permit_required`.
*   **Output:** `town_solar_rules` (JSON Table keyed by Town Name).

### Step 3.3: Parcel Association
*   **Logic:**
    1.  Spatial Join: `parcels` -> `zoning_polygons` (Get `zone_code`).
    2.  Lookup: `parcels.town` -> `town_solar_rules` (Get rules for town).
    3.  Rule Check:
        *   `IF zone_code IN allowed_districts THEN use_type = 'ALLOWED'`
        *   `ELSE IF zone_code IN special_permit_districts THEN use_type = 'SP'`
        *   `ELSE use_type = 'PROHIBITED'`
*   **Constraint Check:**
    *   `IF use_type == 'PROHIBITED' THEN status = 'ZONING_FAIL'`
    *   `IF parcel_acres < min_lot_size THEN status = 'ZONING_FAIL'`

## 4. Final Data Output (JSONB in `parcels` table)
```json
"zoning_status": {
  "zone_code": "IND-1",
  "zone_desc": "Industrial Park District",
  "use_type": "BY_RIGHT", // "SP", "PROHIBITED"
  "min_lot_size_ac": 5.0,
  "setbacks_ft": {"front": 50, "side": 30, "rear": 30},
  "status": "VIABLE",
  "notes": "Requires Site Plan Review per Section 12.4"
}
```

## 5. Preliminary Research Notes
*   **MassGIS Standardized Zoning:** Often outdated (2005-2012 layers). Local bylaws change frequently. We should prioritize scraping current town GIS/PDFs where possible.
*   **"By Right" vs "Special Permit":** "By Right" is gold. SP introduces political risk (Planning Board discretion).
*   **Moratoriums:** Check town meeting minutes for recent solar moratoriums (temporary bans). This is an advanced feature (Step 2).
