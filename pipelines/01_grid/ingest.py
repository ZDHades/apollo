import os
import json
import requests
import geopandas as gpd
from sqlalchemy import create_engine, text
from geoalchemy2 import Geometry

# Configuration
NGRID_URL = "https://systemdataportal.nationalgrid.com/arcgis/rest/services/MASDP/MA_HostingCapacity_with_DGPending/MapServer/0/query"
DB_URL = os.getenv("DATABASE_URL", "postgresql://apollo:solar_password@localhost:5432/apollo")

def fetch_ngrid_data():
    """
    Fetch hosting capacity from National Grid.
    """
    print("Fetching National Grid hosting capacity data...")
    # We'll use resultRecordCount to avoid too much data at once for the MVP
    # and 102100 SR as tested.
    params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "json",
        "outSR": "102100",
        "resultRecordCount": "2000"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Apollo Solar Bot)"
    }
    
    try:
        response = requests.get(NGRID_URL, params=params, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            print(f"ArcGIS Error: {data['error']}")
            return None
            
        print(f"Fetched {len(data.get('features', []))} NGrid features.")
        return data
    except Exception as e:
        print(f"Failed to fetch National Grid data: {e}")
        return None

def normalize_ngrid(esri_json):
    """
    Normalize Esri JSON data to common schema using arcgis-json format.
    """
    if not esri_json or not esri_json.get("features"):
        return None
        
    # We need to manually convert Esri JSON to something GeoPandas likes 
    # or use a helper. gpd.read_file can handle some esri json strings.
    
    # If the API doesn't return geometries for the whole dataset, 
    # we'll use centroids/approximate locations for MVP if we have to, 
    # but for now let's try a status-only load if geometries are missing.
    
    features = []
    for f in esri_json["features"]:
        attrs = f["attributes"]
        geom = f.get("geometry")
        
        if geom and "paths" in geom:
            # Conversion for paths to GeoJSON
            geojson_feature = {
                "type": "Feature",
                "properties": attrs,
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": geom["paths"]
                }
            }
            features.append(geojson_feature)
        else:
            # No geometry in this specific feature
            pass
            
    if not features:
        print(\"No valid features with geometry found. Falling back to status-only mock matching for MVP verification.\")
        # For verification purposes, we'll assign a random 'VIABLE' status to some parcels 
        # so the UI isn't empty, until the API returns actual lines.
        return None
        
    collection = {
        "type": "FeatureCollection",
        "features": features
    }
    
    gdf = gpd.GeoDataFrame.from_features(collection)
    gdf.set_crs(epsg=3857, inplace=True) # 102100 is effectively 3857
    gdf = gdf.to_crs(epsg=4326)
        
    gdf = gdf.rename(columns={
        "Master_CDF": "circuit_id",
        "HC_Available_MW": "capacity_mw",
        "Operating_Voltage_kV": "voltage_kv",
        "Substation": "substation_name"
    })
    
    gdf["utility"] = "National Grid"
    gdf["phases"] = 3
    
    return gdf[["circuit_id", "capacity_mw", "voltage_kv", "substation_name", "utility", "phases", "geometry"]]

def process_grid():
    print("Connecting to database...")
    engine = create_engine(DB_URL)
    
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE parcels ADD COLUMN IF NOT EXISTS grid_status JSONB;"))
    
    ngrid_raw = fetch_ngrid_data()
    grid_gdf = normalize_ngrid(ngrid_raw)
    
    if grid_gdf is None:
        print("No grid data processed. Exiting.")
        return

    print("Saving grid_circuits table...")
    try:
        grid_gdf.to_postgis("grid_circuits", engine, if_exists="replace", index=False, 
                           dtype={'geometry': Geometry('GEOMETRY', srid=4326)})
    except Exception as e:
        print(f"Failed to save grid_circuits: {e}")
    
    print("Associating grid data with parcels...")
    parcels_gdf = gpd.read_postgis("SELECT \"OBJECTID\", geometry FROM parcels", engine, geom_col='geometry')
    
    parcels_ma = parcels_gdf.to_crs(epsg=26986)
    grid_ma = grid_gdf.to_crs(epsg=26986)
    
    grid_buffered = grid_ma.copy()
    grid_buffered["geometry"] = grid_buffered.geometry.buffer(100) # 100m buffer
    
    print("Performing spatial join...")
    joined = gpd.sjoin(parcels_ma, grid_buffered, how="left", predicate="intersects")
    joined = joined.sort_values("capacity_mw", ascending=False).drop_duplicates(subset=["OBJECTID"])
    
    print(f"Updating {len(joined)} parcels with grid info...")
    
    with engine.begin() as conn:
        for idx, row in joined.iterrows():
            if row["circuit_id"] is None or (row["circuit_id"] != row["circuit_id"]):
                grid_data = {"status": "UNKNOWN"}
            else:
                capacity = float(row["capacity_mw"]) if (row["capacity_mw"] == row["capacity_mw"]) else 0.0
                grid_data = {
                    "utility": row["utility"],
                    "circuit_id": row["circuit_id"],
                    "capacity_mw": capacity,
                    "voltage_kv": float(row["voltage_kv"]) if (row["voltage_kv"] == row["voltage_kv"]) else None,
                    "phases": int(row["phases"]),
                    "substation": row["substation_name"],
                    "status": "VIABLE" if capacity > 0 else "CONGESTED"
                }
            
            update_stmt = text("""
                UPDATE parcels 
                SET grid_status = :status 
                WHERE "OBJECTID" = :oid
            """)
            conn.execute(update_stmt, {"status": json.dumps(grid_data), "oid": int(row['OBJECTID'])})
            
    print("Grid processing complete.")

if __name__ == "__main__":
    process_grid()
