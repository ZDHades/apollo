import os
import json
import requests
import geopandas as gpd
from sqlalchemy import create_engine, text
from geoalchemy2 import Geometry

# Configuration
# MassDOT Road Inventory (Line layer)
ROADS_URL = "https://gis.massdot.state.ma.us/arcgis/rest/services/Roads/RoadInventoryYearEndFiles/FeatureServer/10/query"
DB_URL = os.getenv("DATABASE_URL", "postgresql://apollo:solar_password@localhost:5432/apollo")

def get_town_bbox(engine):
    query = text("""
        SELECT ST_XMin(ST_Extent(ST_Transform(geometry, 4326))), ST_YMin(ST_Extent(ST_Transform(geometry, 4326))), 
               ST_XMax(ST_Extent(ST_Transform(geometry, 4326))), ST_YMax(ST_Extent(ST_Transform(geometry, 4326)))
        FROM parcels
    """)
    with engine.connect() as conn:
        bbox = conn.execute(query).fetchone()
        return bbox

def fetch_roads(bbox):
    print(f"Fetching MassDOT roads for bbox: {bbox}...")
    xmin, ymin, xmax, ymax = bbox
    
    params = {
        "geometry": f"{xmin},{ymin},{xmax},{ymax}",
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "inSR": "4326",
        "outSR": "4326",
        "outFields": "St_Name,Surface_Tp,F_F_Class",
        "returnGeometry": "true",
        "f": "json"
    }
    
    headers = {"User-Agent": "Mozilla/5.0 (Apollo Solar Bot)"}
    
    try:
        response = requests.get(ROADS_URL, params=params, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            print(f"ArcGIS Error: {data['error']}")
            return None
            
        print(f"Fetched {len(data.get('features', []))} road features.")
        return data
    except Exception as e:
        print(f"Failed to fetch roads: {e}")
        return None

def normalize_roads(esri_json):
    if not esri_json or not esri_json.get("features"):
        return None
        
    features = []
    for f in esri_json["features"]:
        attrs = f["attributes"]
        geom = f.get("geometry")
        if not geom or "paths" not in geom:
            continue
            
        geojson_feature = {
            "type": "Feature",
            "properties": attrs,
            "geometry": {
                "type": "MultiLineString",
                "coordinates": geom["paths"]
            }
        }
        features.append(geojson_feature)
        
    if not features: return None
        
    gdf = gpd.GeoDataFrame.from_features(features)
    gdf.set_crs(epsg=4326, inplace=True)
    return gdf

def process_infrastructure():
    print("Connecting to database...")
    engine = create_engine(DB_URL)
    
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE parcels ADD COLUMN IF NOT EXISTS infrastructure_status JSONB;"))
    
    bbox = get_town_bbox(engine)
    if not bbox or None in bbox:
        print("No parcels found in DB.")
        return

    roads_raw = fetch_roads(bbox)
    roads_gdf = normalize_roads(roads_raw)
    
    if roads_gdf is None:
        print("No roads fetched. Exiting.")
        return

    print("Associating infrastructure data with parcels...")
    parcels_gdf = gpd.read_postgis("SELECT \"OBJECTID\", geometry FROM parcels", engine, geom_col='geometry')
    
    # Reproject to MA State Plane for linear measurements (frontage)
    parcels_ma = parcels_gdf.to_crs(epsg=26986)
    roads_ma = roads_gdf.to_crs(epsg=26986)
    
    print("Calculating frontage...")
    for idx, parcel in parcels_ma.iterrows():
        # Find intersecting roads (buffer road slightly to ensure overlap)
        possible_roads = roads_ma[roads_ma.intersects(parcel.geometry.buffer(10))]
        
        frontage_ft = 0
        road_names = []
        
        if not possible_roads.empty:
            boundary = parcel.geometry.boundary
            for _, road in possible_roads.iterrows():
                # Intersect parcel boundary with buffered road line
                intersect = boundary.intersection(road.geometry.buffer(5))
                frontage_ft += intersect.length * 3.28084
                if road["St_Name"]:
                    road_names.append(road["St_Name"])
        
        infra_data = {
            "frontage_ft": round(frontage_ft, 1),
            "access_roads": list(set(road_names)),
            "status": "VIABLE" if frontage_ft > 40 else "REVIEW",
            "notes": "Calculated via MassDOT Road Inventory spatial join."
        }
        
        update_stmt = text('UPDATE parcels SET infrastructure_status = :status WHERE "OBJECTID" = :oid')
        with engine.begin() as conn:
            conn.execute(update_stmt, {"status": json.dumps(infra_data), "oid": int(parcel['OBJECTID'])})

    print("Infrastructure processing complete.")

if __name__ == "__main__":
    process_infrastructure()
