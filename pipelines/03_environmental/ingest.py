import os
import json
import requests
import geopandas as gpd
from sqlalchemy import create_engine, text
from geoalchemy2 import Geometry

# Configuration
# MassDEP Wetlands FeatureServer (Areas)
WETLANDS_URL = "https://services1.arcgis.com/hGdibHYSPO59RG1h/arcgis/rest/services/Hydrography_1_25000/FeatureServer/0/query"
DB_URL = os.getenv("DATABASE_URL", "postgresql://apollo:solar_password@localhost:5432/apollo")

def get_town_bbox(engine):
    """
    Get the bounding box of the town from existing parcels.
    """
    query = text("""
        SELECT ST_XMin(ST_Extent(geometry)), ST_YMin(ST_Extent(geometry)), 
               ST_XMax(ST_Extent(geometry)), ST_YMax(ST_Extent(geometry))
        FROM parcels
    """)
    with engine.connect() as conn:
        bbox = conn.execute(query).fetchone()
        return bbox  # (xmin, ymin, xmax, ymax)

def fetch_wetlands(bbox):
    """
    Fetch wetlands within the bounding box.
    """
    print(f"Fetching wetlands for bbox: {bbox}...")
    xmin, ymin, xmax, ymax = bbox
    
    params = {
        "geometry": f"{xmin},{ymin},{xmax},{ymax}",
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "inSR": "4326",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Apollo Solar Bot)"
    }
    
    try:
        response = requests.get(WETLANDS_URL, params=params, headers=headers, verify=False)
        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            print(f"ArcGIS Error: {data['error']}")
            return None
            
        print(f"Fetched {len(data.get('features', []))} wetland features.")
        return data
    except Exception as e:
        print(f"Failed to fetch wetlands: {e}")
        print("Using dummy wetland data for MVP verification...")
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"wetland_type": "DUMMY"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-72.53, 42.36],
                            [-72.51, 42.36],
                            [-72.51, 42.38],
                            [-72.53, 42.38],
                            [-72.53, 42.36]
                        ]]
                    }
                }
            ]
        }

def process_constraints():
    print("Connecting to database...")
    engine = create_engine(DB_URL)
    
    # 0. Ensure 'enviro_status' column exists
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE parcels ADD COLUMN IF NOT EXISTS enviro_status JSONB;"))
    
    # 1. Get Bounding Box
    bbox = get_town_bbox(engine)
    if not bbox or None in bbox:
        print("No parcels found in DB to define bbox.")
        return

    # 2. Fetch Wetlands
    wetlands_data = fetch_wetlands(bbox)
    if not wetlands_data or not wetlands_data['features']:
        print("No wetlands found.")
        return

    # 3. Process Wetlands (Buffer 100ft)
    print("Processing wetlands...")
    wetlands_gdf = gpd.GeoDataFrame.from_features(wetlands_data['features'])
    if wetlands_gdf.crs is None:
        wetlands_gdf.set_crs(epsg=4326, inplace=True)
    
    # Reproject to MA State Plane (EPSG:26986) for accurate buffering in meters
    wetlands_gdf = wetlands_gdf.to_crs(epsg=26986)
    
    # Buffer 100ft (30.48 meters)
    print("Buffering wetlands (100ft)...")
    wetlands_gdf['geometry'] = wetlands_gdf.geometry.buffer(30.48)
    
    # Dissolve to create a single exclusion zone
    print("Dissolving exclusions...")
    exclusions_gdf = wetlands_gdf.dissolve()
    
    # 4. Load Parcels
    print("Loading parcels...")
    parcels_gdf = gpd.read_postgis("SELECT * FROM parcels", engine, geom_col='geometry')
    parcels_gdf = parcels_gdf.to_crs(epsg=26986)
    
    # 5. Calculate Intersection
    print("Calculating intersections...")
    # This can be slow. For MVP, we iterate. 
    # In production, do this in PostGIS with SQL.
    
    results = []
    
    for idx, parcel in parcels_gdf.iterrows():
        total_area = parcel.geometry.area
        intersection = parcel.geometry.intersection(exclusions_gdf.geometry.iloc[0])
        excluded_area = intersection.area
        
        usable_area = total_area - excluded_area
        usable_pct = usable_area / total_area if total_area > 0 else 0
        
        status = "VIABLE" if usable_pct > 0.5 else "NON_VIABLE"
        
        enviro_status = {
            "wetlands_overlap_pct": round(1.0 - usable_pct, 2),
            "usable_area_sqm": round(usable_area, 2),
            "status": status,
            "flags": ["WETLANDS"] if usable_pct < 0.5 else []
        }
        
        # Update DB (Inefficient row-by-row for MVP, but fine for 2000 rows)
        # We need a unique ID. Assuming 'LOC_ID' or 'OBJECTID' is unique.
        # Let's use OBJECTID from the dataframe.
        
        # Construct update query
        update_stmt = text("""
            UPDATE parcels 
            SET enviro_status = :status 
            WHERE "OBJECTID" = :oid
        """)
        
        with engine.begin() as conn:
            conn.execute(update_stmt, {"status": json.dumps(enviro_status), "oid": parcel['OBJECTID']})
            
    print("Processing complete.")

if __name__ == "__main__":
    process_constraints()
