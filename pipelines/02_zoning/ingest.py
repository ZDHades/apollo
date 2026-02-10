import os
import json
from sqlalchemy import create_engine, text

# Configuration
DB_URL = os.getenv("DATABASE_URL", "postgresql://apollo:solar_password@localhost:5432/apollo")

# Mock Solar Rules for Amherst (Derived from Research/Hypothesis)
# Real implementation would use an LLM to parse current PDFs.
AMHERST_SOLAR_RULES = {
    "town": "Amherst",
    "large_scale_ground_mount": {
        "allowed_districts": ["IND", "LI", "PRD", "COM"],
        "special_permit_districts": ["RO", "RR", "R-LD"],
        "prohibited_districts": ["R-VC", "R-G", "R-N"],
        "setbacks_ft": {
            "front": 50,
            "side": 30,
            "rear": 30
        },
        "min_lot_size_ac": 5.0,
        "max_lot_coverage_pct": 50
    }
}

def process_zoning():
    print("Connecting to database...")
    engine = create_engine(DB_URL)
    
    # 0. Ensure 'zoning_status' column exists
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE parcels ADD COLUMN IF NOT EXISTS zoning_status JSONB;"))
    
    # 1. Fetch parcels with their current 'ZONING' field (from MassGIS)
    print("Fetching parcels for zoning evaluation...")
    with engine.connect() as conn:
        # In a real Town GIS, 'ZONING' is more granular. MassGIS has raw strings.
        parcels = conn.execute(text('SELECT "OBJECTID", "ZONING", "LOT_SIZE" FROM parcels')).fetchall()
        
    print(f"Evaluating zoning for {len(parcels)} parcels...")
    
    rules = AMHERST_SOLAR_RULES["large_scale_ground_mount"]
    
    with engine.begin() as conn:
        for p in parcels:
            oid = p[0]
            raw_zone = str(p[1]) if p[1] else "UNKNOWN"
            lot_size_raw = p[2] if p[2] else 0.0 # Assuming LOT_SIZE is in sqft or acres? 
            # MassGIS LOT_SIZE is often in acres for Level 3.
            
            # Simple matching logic
            use_type = "PROHIBITED"
            status = "NON_VIABLE"
            
            # Extract base code (e.g. "R-O (Residential)" -> "RO")
            clean_zone = raw_zone.replace("-", "").split()[0].upper()
            
            if clean_zone in rules["allowed_districts"]:
                use_type = "BY_RIGHT"
                status = "VIABLE"
            elif clean_zone in rules["special_permit_districts"]:
                use_type = "SPECIAL_PERMIT"
                status = "REVIEW"
            
            # Lot size check
            if lot_size_raw < rules["min_lot_size_ac"]:
                status = "NON_VIABLE"
                notes = f"Lot size {lot_size_raw}ac < {rules['min_lot_size_ac']}ac requirement."
            else:
                notes = f"District: {raw_zone}"

            zoning_data = {
                "zone_code": raw_zone,
                "use_type": use_type,
                "min_lot_size_ac": rules["min_lot_size_ac"],
                "status": status,
                "notes": notes
            }
            
            conn.execute(
                text('UPDATE parcels SET zoning_status = :status WHERE "OBJECTID" = :oid'),
                {"status": json.dumps(zoning_data), "oid": oid}
            )

    print("Zoning processing complete.")

if __name__ == "__main__":
    process_zoning()
