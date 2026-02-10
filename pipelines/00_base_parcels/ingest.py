import os
import requests
import geopandas as gpd
from sqlalchemy import create_engine
from geoalchemy2 import Geometry

# Configuration
WFS_URL = "https://giswebservices.massgis.state.ma.us/geoserver/wfs"
TOWN_ID = 8  # Amherst (Default for MVP)
LAYER_NAME = "massgis:GISDATA.L3_TAXPAR_POLY_ASSESS"
DB_URL = os.getenv("DATABASE_URL", "postgresql://apollo:solar_password@localhost:5432/apollo")

def fetch_parcels(town_id=TOWN_ID):
    """
    Fetch parcel polygons from MassGIS WFS for a specific town.
    """
    print(f"Fetching parcels for Town ID: {town_id} from MassGIS...")
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeNames": LAYER_NAME,
        "outputFormat": "application/json",
        "cql_filter": f"TOWN_ID={town_id}",
        "srsName": "EPSG:4326"
    }
    
    try:
        response = requests.get(WFS_URL, params=params)
        response.raise_for_status()
        data = response.json()
        feature_count = len(data.get("features", []))
        print(f"Successfully fetched {feature_count} features.")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data: {e}")
        if response.content:
            print(f"Response content: {response.content[:200]}")
        raise

def load_to_db(geojson_data):
    """
    Load GeoJSON data into PostGIS 'parcels' table.
    """
    print("Processing GeoJSON into GeoDataFrame...")
    gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
    
    # Ensure CRS is set to EPSG:4326
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)
    
    print(f"GeoDataFrame loaded. Shape: {gdf.shape}")
    print("Columns:", gdf.columns.tolist())
    
    # Basic Schema Normalization (MVP)
    # MassGIS fields: PROP_ID, LOC_ID, TOWN_ID, MAP_PAR_ID, etc.
    # We might want to rename some for clarity, but keeping raw is safer for now.
    
    print(f"Connecting to database: {DB_URL}")
    engine = create_engine(DB_URL)
    
    try:
        # Write to PostGIS
        # using 'replace' to ensure clean slate for dev
        gdf.to_postgis(
            "parcels", 
            engine, 
            if_exists="replace", 
            index=False, 
            dtype={'geometry': Geometry('MULTIPOLYGON', srid=4326)}
        )
        print("Successfully loaded 'parcels' table into PostGIS.")
    except Exception as e:
        print(f"Database error: {e}")
        raise

if __name__ == "__main__":
    try:
        data = fetch_parcels()
        if data and data.get("features"):
            load_to_db(data)
        else:
            print("No features found.")
    except Exception as e:
        print(f"Pipeline failed: {e}")
