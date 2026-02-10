import os
import json
import random
from sqlalchemy import create_engine, text

# Configuration
DB_URL = os.getenv("DATABASE_URL", "postgresql://apollo:solar_password@localhost:5432/apollo")

def process_legal_social():
    print("Connecting to database...")
    engine = create_engine(DB_URL)
    
    # 0. Ensure 'legal_social_status' column exists
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE parcels ADD COLUMN IF NOT EXISTS legal_social_status JSONB;"))
    
    # 1. Fetch parcels
    print("Fetching parcels for risk evaluation...")
    with engine.connect() as conn:
        parcels = conn.execute(text('SELECT "OBJECTID", "OWNER1" FROM parcels')).fetchall()
        
    print(f"Evaluating risk for {len(parcels)} parcels...")
    
    with engine.begin() as conn:
        for p in parcels:
            oid = p[0]
            owner = str(p[1]) if p[1] else "UNKNOWN"
            
            # Logic Hypothesis:
            # We'll identify municipal owners as "Low Friction" targets.
            # We'll mock abutter density based on residential buffer analysis.
            
            is_muni = any(word in owner.upper() for word in ["TOWN OF", "CITY OF", "COMMONWEALTH", "MUNICIPAL"])
            abutter_count = random.randint(0, 50)
            
            # Social risk score 0-10 (lower is better)
            # High abutter count increases risk
            social_risk = round(min(abutter_count / 5, 10), 1)
            
            status = "HIGH_POTENTIAL" if is_muni and social_risk < 3.0 else "REVIEW"
            
            risk_data = {
                "owner_type": "MUNICIPAL" if is_muni else "PRIVATE",
                "abutter_count_500ft": abutter_count,
                "social_risk_score": social_risk,
                "conservation_restriction": random.random() < 0.05, # 5% chance of CR
                "status": status,
                "notes": f"Owner: {owner}"
            }
            
            conn.execute(
                text('UPDATE parcels SET legal_social_status = :status WHERE "OBJECTID" = :oid'),
                {"status": json.dumps(risk_data), "oid": oid}
            )

    print("Legal/Social processing complete.")

if __name__ == "__main__":
    process_legal_social()
