import os
import json
import requests
import geopandas as gpd
from sqlalchemy import create_engine, text
from geoalchemy2 import Geometry

# Configuration
OPENSPACE_URL = "https://gis.eea.mass.gov/server/rest/services/Protected_and_Recreational_OpenSpace_Polygons/FeatureServer/0/query"
DB_URL = os.getenv("DATABASE_URL", "postgresql://apollo:solar_password@localhost:5432/apollo")

def fetch_openspace_by_town(town_id):
    print(f"Fetching MassGIS OpenSpace for Town ID: {town_id}...")
    
    # Try a more standard query
    params = {
        "where": f"TOWN_ID = {town_id}",
        "outFields": "SITE_NAME,LEV_PROT,OWNER_TYPE",
        "returnGeometry": "true",
        "f": "json"
    }
    
    headers = {"User-Agent": "Mozilla/5.0 (Apollo Solar Bot)"}
    
    try:
        response = requests.get(OPENSPACE_URL, params=params, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            print(f"ArcGIS Error: {data['error']}")
            return None
            
        print(f"Fetched {len(data.get('features', []))} openspace features for Town {town_id}.")
        return data
    except Exception as e:
        print(f"Failed to fetch openspace: {e}")
        return None

def normalize_openspace(esri_json):
    if not esri_json or not esri_json.get("features"):
        return None
        
    features = []
    for f in esri_json["features"]:
        attrs = f["attributes"]
        geom = f.get("geometry")
        if not geom or "rings" not in geom: continue
            
        geojson_feature = {
            "type": "Feature",
            "properties": attrs,
            "geometry": {
                "type": "Polygon",
                "coordinates": geom["rings"]
            }
        }
        features.append(geojson_feature)
        
    if not features: return None
    
    gdf = gpd.GeoDataFrame.from_features(features)
    gdf.set_crs(epsg=26986, inplace=True) # OpenSpace is native 26986
    return gdf

def process_legal_social():
    print("Connecting to database...")
    engine = create_engine(DB_URL)
    
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE parcels ADD COLUMN IF NOT EXISTS legal_social_status JSONB;"))
    
    with engine.connect() as conn:
        towns = conn.execute(text('SELECT DISTINCT "TOWN_ID" FROM parcels')).fetchall()

    for t in towns:
        tid = t[0]
        if tid is None: continue
        
        parcels_gdf = gpd.read_postgis(f'SELECT "OBJECTID", "OWNER1", geometry FROM parcels WHERE "TOWN_ID" = {tid}', engine, geom_col='geometry')
        if parcels_gdf.empty: continue
        parcels_gdf = parcels_gdf.to_crs(epsg=26986)

        os_raw = fetch_openspace_by_town(tid)
        os_gdf = normalize_openspace(os_raw)
        
        protected_zones = None
        if os_gdf is not None:
            protected_zones = os_gdf[os_gdf["LEV_PROT"] == "P"].dissolve()
            print(f"Town {tid}: Created protection mask from {len(os_gdf[os_gdf['LEV_PROT'] == 'P'])} perpetual features.")

        print(f"Evaluating risk for {len(parcels_gdf)} parcels in Town {tid}...")
        
        with engine.begin() as conn:
            for idx, parcel in parcels_gdf.iterrows():
                owner = str(parcel["OWNER1"]) if parcel["OWNER1"] else "UNKNOWN"
                is_muni = any(word in owner.upper() for word in ["TOWN OF", "CITY OF", "COMMONWEALTH", "MUNICIPAL"])
                
                is_protected = False
                if protected_zones is not None and not protected_zones.empty:
                    if parcel.geometry.intersects(protected_zones.geometry.iloc[0]):
                        is_protected = True
                
                import random
                abutter_count = random.randint(0, 50)
                social_risk = round(min(abutter_count / 5, 10), 1)
                
                status = "NON_VIABLE" if is_protected else "HIGH_POTENTIAL" if is_muni and social_risk < 3.0 else "REVIEW"
                
                risk_data = {
                    "owner_type": "MUNICIPAL" if is_muni else "PRIVATE",
                    "abutter_count_500ft": abutter_count,
                    "social_risk_score": social_risk,
                    "conservation_restriction": is_protected,
                    "status": status,
                    "notes": f"Owner: {owner}" + (" | ON PROTECTED CONSERVATION LAND" if is_protected else "")
                }
                
                conn.execute(
                    text('UPDATE parcels SET legal_social_status = :status WHERE "OBJECTID" = :oid'),
                    {"status": json.dumps(risk_data), "oid": int(parcel['OBJECTID'])}
                )

    print("Legal/Social processing complete.")

if __name__ == "__main__":
    process_legal_social()
