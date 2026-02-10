import os
import json
import requests
import geopandas as gpd
from sqlalchemy import create_engine, text
from geoalchemy2 import Geometry

# Configuration
# National Grid FeatureServer (EMA/WMA Aggregate)
NGRID_URL = "https://systemdataportal.nationalgrid.com/arcgis/rest/services/MASDP/MA_HostingCapacity_with_DGPending/MapServer/0/query"
# placeholder for Eversource
ES_URL_EMA = "https://epochprodgasdist.eversource.com/wamgasgis/rest/services/DG_Hosting/Generation_Capacity_External_Viewers_EMA/MapServer/27/query"

DB_URL = os.getenv("DATABASE_URL", "postgresql://apollo:solar_password@localhost:5432/apollo")

def fetch_ngrid_data():
    """
    Fetch all hosting capacity lines from National Grid.
    """
    print("Fetching National Grid hosting capacity data...")
    params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson",
        "outSR": "4326"
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

def normalize_ngrid(geojson_data):
    """
    Normalize National Grid data to common schema.
    """
    if not geojson_data or not geojson_data.get("features"):
        return None
        
    gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)
        
    # Mapping fields
    # Master_CDF -> circuit_id
    # HC_Available_MW -> capacity_mw
    # Operating_Voltage_kV -> voltage_kv
    
    gdf = gdf.rename(columns={
        "Master_CDF": "circuit_id",
        "HC_Available_MW": "capacity_mw",
        "Operating_Voltage_kV": "voltage_kv",
        "Substation": "substation_name"
    })
    
    gdf["utility"] = "National Grid"
    gdf["phases"] = 3 # Based on layer name "3 Phase"
    
    return gdf[["circuit_id", "capacity_mw", "voltage_kv", "substation_name", "utility", "phases", "geometry"]]

def process_grid():
    print("Connecting to database...")
    engine = create_engine(DB_URL)
    
    # 0. Ensure 'grid_status' column exists in parcels table
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE parcels ADD COLUMN IF NOT EXISTS grid_status JSONB;"))
    
    # 1. Fetch & Normalize
    ngrid_raw = fetch_ngrid_data()
    grid_gdf = normalize_ngrid(ngrid_raw)
    
    if grid_gdf is None:
        print("No grid data fetched. Exiting.")
        return

    # 2. Save grid_circuits table for reference
    print("Saving grid_circuits table...")
    grid_gdf.to_postgis("grid_circuits", engine, if_exists="replace", index=False, 
                       dtype={'geometry': Geometry('MULTILINESTRING', srid=4326)})
    
    # 3. Parcel Association (Spatial Join)
    print("Associating grid data with parcels...")
    # Reproject to MA State Plane for distance calculations if needed, 
    # but for intersection we can stay in 4326 or use PostGIS ST_Distance.
    
    # Load parcels
    parcels_gdf = gpd.read_postgis("SELECT \"OBJECTID\", geometry FROM parcels", engine, geom_col='geometry')
    
    # We'll use a spatial join. Since grid circuits are lines, we find the nearest line.
    # To keep it simple for MVP, we'll join by intersection with a small buffer.
    
    # Reproject to 26986 for buffering
    parcels_ma = parcels_gdf.to_crs(epsg=26986)
    grid_ma = grid_gdf.to_crs(epsg=26986)
    
    # Buffer grid lines by 50 meters to catch nearby parcels
    grid_buffered = grid_ma.copy()
    grid_buffered["geometry"] = grid_buffered.geometry.buffer(50)
    
    print("Performing spatial join...")
    joined = gpd.sjoin(parcels_ma, grid_buffered, how="left", predicate="intersects")
    
    # Group by parcel ID and take the best circuit (highest capacity) if multiple match
    joined = joined.sort_values("capacity_mw", ascending=False).drop_duplicates(subset=["OBJECTID"])
    
    print(f"Updating {len(joined)} parcels with grid info...")
    
    for idx, row in joined.iterrows():
        if row["circuit_id"] is None or (isinstance(row["circuit_id"], float) and os.path.isnan(row["circuit_id"])):
            status = "UNKNOWN"
            grid_data = {"status": status}
        else:
            capacity = float(row["capacity_mw"]) if not os.path.isnan(row["capacity_mw"]) else 0.0
            status = "VIABLE" if capacity > 0 else "CONGESTED"
            
            grid_data = {
                "utility": row["utility"],
                "circuit_id": row["circuit_id"],
                "capacity_mw": capacity,
                "voltage_kv": float(row["voltage_kv"]) if not os.path.isnan(row["voltage_kv"]) else None,
                "phases": int(row["phases"]),
                "substation": row["substation_name"],
                "status": status
            }
            
        update_stmt = text("""
            UPDATE parcels 
            SET grid_status = :status 
            WHERE "OBJECTID" = :oid
        """)
        
        with engine.begin() as conn:
            conn.execute(update_stmt, {"status": json.dumps(grid_data), "oid": row['OBJECTID']})
            
    print("Grid processing complete.")

if __name__ == "__main__":
    process_grid()
