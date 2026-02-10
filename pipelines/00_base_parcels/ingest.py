import os
import requests
import geopandas as gpd
import argparse
from sqlalchemy import create_engine
from geoalchemy2 import Geometry

# Configuration
FEATURE_SERVER_URL = "https://services1.arcgis.com/hGdibHYSPO59RG1h/arcgis/rest/services/L3_TAXPAR_POLY_ASSESS_gdb/FeatureServer/0/query"
DEFAULT_TOWN_ID = 8  # Amherst
DB_URL = os.getenv("DATABASE_URL", "postgresql://apollo:solar_password@localhost:5432/apollo")

def fetch_parcels(town_id=DEFAULT_TOWN_ID):
    """
    Fetch parcel polygons from MassGIS ArcGIS FeatureServer for a specific town.
    """
    print(f"Fetching parcels for Town ID: {town_id} from MassGIS ArcGIS...")
    
    # ArcGIS REST API parameters
    params = {
        "where": f"TOWN_ID={town_id}",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Apollo Solar Bot)"
    }
    
    try:
        response = requests.get(FEATURE_SERVER_URL, params=params, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            raise Exception(f"ArcGIS Error: {data['error']}")
            
        feature_count = len(data.get("features", []))
        print(f"Successfully fetched {feature_count} features.")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data: {e}")
        raise

def load_to_db(geojson_data, append=False):
    """
    Load GeoJSON data into PostGIS 'parcels' table.
    """
    if not geojson_data or not geojson_data.get("features"):
        return
        
    print("Processing GeoJSON into GeoDataFrame...")
    gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
    
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)
    
    # Standardize geometry to MULTIPOLYGON
    gdf['geometry'] = [g if g.geom_type == 'MultiPolygon' else gpd.GeoSeries([g]).iloc[0] for g in gdf.geometry]
    
    engine = create_engine(DB_URL)
    
    try:
        # Use 'append' if we want to add multiple towns
        mode = "append" if append else "replace"
        print(f"Loading to database (mode={mode})...")
        
        gdf.to_postgis(
            "parcels", 
            engine, 
            if_exists=mode, 
            index=False, 
            dtype={'geometry': Geometry('GEOMETRY', srid=4326)}
        )
        print(f"Successfully loaded parcels into PostGIS.")
    except Exception as e:
        print(f"Database error: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--town", type=int, default=DEFAULT_TOWN_ID)
    parser.add_argument("--append", action="store_true")
    args = parser.parse_args()
    
    try:
        data = fetch_parcels(args.town)
        load_to_db(data, args.append)
    except Exception as e:
        print(f"Pipeline failed: {e}")
