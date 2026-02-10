import os
import json
import random
from sqlalchemy import create_engine, text

# Configuration
DB_URL = os.getenv("DATABASE_URL", "postgresql://apollo:solar_password@localhost:5432/apollo")

def process_physical():
    print("Connecting to database...")
    engine = create_engine(DB_URL)
    
    # 0. Ensure 'physical_status' column exists
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE parcels ADD COLUMN IF NOT EXISTS physical_status JSONB;"))
    
    # 1. Fetch parcels
    print("Fetching parcels for constructability evaluation...")
    with engine.connect() as conn:
        parcels = conn.execute(text('SELECT "OBJECTID" FROM parcels')).fetchall()
        
    print(f"Evaluating topography for {len(parcels)} parcels...")
    
    with engine.begin() as conn:
        for p in parcels:
            oid = p[0]
            
            # Logic Hypothesis:
            # We'll use a random generator to mock LiDAR zonal statistics.
            # Real implementation would use Rasterio to read DEMs and calculate slope/aspect.
            
            mean_slope = round(random.uniform(1.0, 20.0), 1)
            # Penalize parcels with slope > 15%
            status = "VIABLE" if mean_slope < 15.0 else "NON_VIABLE"
            
            physical_data = {
                "mean_slope_pct": mean_slope,
                "max_slope_pct": round(mean_slope * random.uniform(1.2, 2.0), 1),
                "mean_aspect_deg": random.randint(0, 360),
                "land_cover": random.choice(["OPEN", "FOREST", "DEVELOPED"]),
                "status": status,
                "notes": "Slope analysis derived from 1m LiDAR DEM (Mock)"
            }
            
            conn.execute(
                text('UPDATE parcels SET physical_status = :status WHERE "OBJECTID" = :oid'),
                {"status": json.dumps(physical_data), "oid": oid}
            )

    print("Physical processing complete.")

if __name__ == "__main__":
    process_physical()
