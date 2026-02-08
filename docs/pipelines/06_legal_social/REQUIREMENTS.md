# Legal & Social Risk - Requirements & Data Spec

## 1. Objective
Quantify the **Execution Risk** associated with land ownership, easements, and community opposition.
A parcel may look perfect technically but be politically toxic or legally encumbered.

**Key Metrics:**
*   **Ownership Type:** Private, Municipal, Trust, Corporate (LLC).
*   **Protected Status:** CR (Conservation Restriction), APR (Agricultural Preservation), Chapter 61 (Tax status - Right of First Refusal).
*   **Abutter Density:** Number of residential dwellings within 500ft. (NIMBY Risk).
*   **Historic/Cultural:** Proximity to historic districts or tribal lands.
*   **Sentiment:** "Solar" mentions in town meeting minutes (Positive/Negative).

## 2. Data Sources
| Provider | Dataset Name | Type | URL / Access Method | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **MassGIS** | Level 3 Assessors (Parcels) | WFS / Shapefile | [MassGIS](https://www.mass.gov/info-details/massgis-data-level-3-assessors-parcels) | Contains basic owner type/use codes. |
| **MassGIS** | Protected and Recreational Open Space (PROS) | WFS / Shapefile | [MassGIS](https://www.mass.gov/info-details/massgis-data-protected-and-recreational-open-space) | Defines CRs, APRs, Article 97 lands. |
| **MassGIS** | MACRIS (Historic Inventory) | WFS / Shapefile | [MassGIS](https://www.mass.gov/info-details/massgis-data-macris-massachusetts-cultural-resource-information-system) | Historic places/areas. |
| **Town GIS** | Tax Map / Property Card | Scrape / API | Varied | More current ownership data. |

## 3. Ingestion Pipeline Specification
**Script Name:** `ingest_legal_social.py`

### Step 3.1: Ownership & Use Codes
*   **Action:** Ingest MassGIS Level 3 Assessors.
*   **Process:**
    1.  **Extract `USE_CODE`**: e.g., "101" (Single Family), "300" (Commercial), "900" (Exempt/Municipal).
    2.  **Extract `OWNER1`**: Normalize names (e.g., "TOWN OF AMHERST" -> "MUNICIPAL").
*   **Output:** `owner_type` (Private/Muni/Corp), `land_use_code`.

### Step 3.2: Conservation Restrictions (The Deal Killers)
*   **Action:** Ingest Protected Open Space (PROS).
*   **Process:**
    1.  **Spatial Join:** Intersect Parcel with PROS Polygons.
    2.  **Check `LEV_PROT`**: "P" (Perpetuity) = NON_VIABLE. "T" (Temporary) = REVIEW.
    3.  **Check `PRIM_PURP`**: "C" (Conservation), "R" (Recreation), "A" (Agriculture/APR).
*   **Output:** `conservation_status` (Protected/Unprotected).

### Step 3.3: Abutter Density (NIMBY Score)
*   **Action:** Ingest Building Structures (MassGIS Structures Layer).
*   **Process:**
    1.  **Buffer:** Create 500ft buffer around Parcel boundary.
    2.  **Count:** Count residential structures within buffer.
    3.  **Calculate:** `abutter_density` (Houses per Acre).
*   **Output:** `social_risk_score` (0-10, based on density).

## 4. Final Data Output (JSONB in `parcels` table)
```json
"legal_social_status": {
  "owner_type": "MUNICIPAL", // "PRIVATE", "TRUST"
  "use_code": "930", // Vacant Municipal
  "conservation_restriction": false,
  "chapter_61_status": "NONE", // "61A" (Ag), "61B" (Rec)
  "abutter_count_500ft": 2,
  "social_risk_score": 1.5, // Low risk
  "historic_district_nearby": false,
  "status": "HIGH_POTENTIAL"
}
```

## 5. Preliminary Research Notes
*   **Chapter 61:** Land under Ch. 61 tax breaks gives the Town "Right of First Refusal" upon sale/conversion. This is a process hurdle (120 days) but often surmountable.
*   **Article 97:** Constitutionally protected land (often municipal parks/conservation). Converting this requires a 2/3 vote of the Legislature. Avoid at all costs.
*   **Municipal Land:** Often the best targets (landfills, DPW yards). Town gets lease revenue + cheap power. Win-Win.
