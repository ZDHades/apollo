import os
import json
import random
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DATABASE_URL", "postgresql://apollo:solar_password@localhost:5432/apollo")

def mock_grid_association():
    print("Connecting to database...")
    engine = create_engine(DB_URL)
    
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE parcels ADD COLUMN IF NOT EXISTS grid_status JSONB;"))
    
    print("Loading parcels from DB...")
    with engine.connect() as conn:
        parcels = conn.execute(text('SELECT "OBJECTID" FROM parcels')).fetchall()
    
    print(f"Assigning mock grid status to {len(parcels)} parcels...")
    
    with engine.begin() as conn:
        for p in parcels:
            oid = p[0]
            # Randomly assign status
            is_viable = random.random() > 0.3
            grid_data = {
                "utility": "National Grid",
                "circuit_id": f"MOCK-{random.randint(1000, 9999)}",
                "capacity_mw": round(random.uniform(0, 5.0), 2) if is_viable else 0.0,
                "voltage_kv": random.choice([13.2, 13.8, 23.0]),
                "phases": 3,
                "substation": "MOCK-SUB",
                "status": "VIABLE" if is_viable else "CONGESTED"
            }
            
            conn.execute(
                text('UPDATE parcels SET grid_status = :status WHERE "OBJECTID" = :oid'),
                {"status": json.dumps(grid_data), "oid": oid}
            )

    print("Mock grid processing complete.")

if __name__ == "__main__":
    mock_grid_association()
