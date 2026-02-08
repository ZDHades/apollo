# Solar Site Selection System - Requirements & Attribute Map

## Project Goal
Identify, rank, and visualize land parcels in Massachusetts ideal for solar energy generation (lease/purchase) based on specific grid, zoning, environmental, and physical constraints.

## 1. Grid Interconnection Attributes
*Critical viability factors. Must be "Green/Yellow" circuits.*

| Attribute | Description | Data Source (Potential) |
| :--- | :--- | :--- |
| **Utility Territory** | Service provider (National Grid vs Eversource) | MassGIS, Utility Service Maps |
| **Hosting Capacity** | Available capacity on the circuit (MW) | Mass CEC, Utility Hosting Capacity Maps |
| **Feeder Congestion** | Status of feeder saturation | Utility Hosting Capacity Maps |
| **Distance to Substation** | Linear/road distance to nearest interconnect | MassGIS (Infrastructure Layers), OpenStreetMap |
| **Phase** | Three-phase vs Single-phase availability | Utility Maps (often indicates 3-phase lines) |
| **Voltage** | Distribution voltage (kV) | Utility Maps |

## 2. Zoning & Land Use Attributes
*Regulatory feasibility. Precedent often outweighs raw rules.*

| Attribute | Description | Data Source (Potential) |
| :--- | :--- | :--- |
| **Zoning District** | Base zoning code (Residential, Industrial, etc.) | MassGIS (Standardized Zoning), Town GIS |
| **Solar Permitting** | Allowed by Right vs Special Permit vs Prohibited | Town Bylaws (Text extraction/LLM analysis) |
| **Max System Size** | Cap on MW or acreage per parcel | Town Bylaws |
| **Use Type** | Primary vs Accessory use regulations | Town Bylaws |
| **On-site Load Cap** | Constraints based on existing load | Utility/Town Rules |
| **Parcel Type** | Municipal, Industrial, Commercial, Landfill | MassGIS (Land Use codes), MassDEP (Landfills) |
| **Prior Decisions** | Historical planning board approvals/denials | Town Meeting Minutes, Planning Board Records |

## 3. Environmental Constraints
*Hard exclusion zones and buffers.*

| Attribute | Description | Data Source (Potential) |
| :--- | :--- | :--- |
| **Wetlands** | Presence of wetlands on site | MassGIS (DEP Wetlands) |
| **Wetland Buffer** | 100' buffer zone encroachment | Calculated (GIS Buffer) |
| **Vernal Pools** | Certified or potential vernal pools | MassGIS (NHESP Layers) |
| **Priority Habitats** | Endangered species protection zones | MassGIS (NHESP Priority Habitats) |
| **Floodplains** | FEMA flood zones (A, AE, etc.) | MassGIS (FEMA National Flood Hazard Layer) |
| **Hydric Soils** | Wet soils unsuitable for construction | USDA Web Soil Survey (SSURGO) |

## 4. Physical & Topographical Attributes
*Constructability and cost factors.*

| Attribute | Description | Data Source (Potential) |
| :--- | :--- | :--- |
| **Slope** | Grade percentage (Reject > 10-15%) | MassGIS (LiDAR / Digital Elevation Models) |
| **Aspect** | Solar exposure (South-facing preference) | Derived from DEM |
| **Soil Type** | Structural suitability (Ledge, Fill, Sandy) | USDA Web Soil Survey |
| **Land Cover** | Forest, Open, Impervious, Cultivated | MassGIS (Land Use / Land Cover) |
| **Ledge/Bedrock** | Depth to bedrock (blasting risk) | USDA / USGS Geological Maps |

## 5. Accessibility & Infrastructure
*Logistics for construction and maintenance.*

| Attribute | Description | Data Source (Potential) |
| :--- | :--- | :--- |
| **Road Frontage** | Legal frontage length | MassGIS (Parcel/Tax Map Layers) |
| **Access Width** | Construction vehicle access | Google Maps API / Satellite Analysis |
| **Road Weight Limits** | Bridge/culvert restrictions | MassDOT, Town DPW data |
| **Scenic Roads** | Designated scenic byway status (restrictions) | MassDOT, Town Lists |

## 6. Legal & Encumbrances
*Ownership and title risks.*

| Attribute | Description | Data Source (Potential) |
| :--- | :--- | :--- |
| **Conservation Restrictions (CR)** | Permanent protection status | MassGIS (Protected Open Space), Registry of Deeds |
| **APR** | Agricultural Preservation Restrictions | MassGIS (APR Layers) |
| **Easements/ROWs** | Utility or access easements | Registry of Deeds (OCR/Search required) |
| **Owner Type** | Private, Municipal, Trust, Corporate | MassGIS (Level 3 Assessors Data) |

## 7. Social & Political Risk
*Community opposition indicators.*

| Attribute | Description | Data Source (Potential) |
| :--- | :--- | :--- |
| **Abutter Density** | Proximity to residential neighborhoods | MassGIS (Parcel adjacency analysis) |
| **Visibility** | Line of sight from homes/scenic roads | Viewshed Analysis (GIS) |
| **Sensitive Receptors** | Near schools, historic sites, HOA | OpenStreetMap, MassGIS |
| **Local Sentiment** | "Solar" mentions in town meetings/socials | Facebook Groups, Town Meeting Minutes (Scraped) |

## 8. Positive Indicators (Bonus)
*Features that increase viability.*
* **Closed Landfills:** MassDEP Landfill list.
* **Large Flat Rooftops:** Parking garages, warehouses (Satellite ML detection).
* **Brownfields:** EPA/State databases.
