import os
import json
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DATABASE_URL", "postgresql://apollo:solar_password@localhost:5432/apollo")

def calculate_viability():
    print("Connecting to database...")
    engine = create_engine(DB_URL)
    
    # 0. Ensure 'viability_score' column exists
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE parcels ADD COLUMN IF NOT EXISTS viability_score FLOAT DEFAULT 0.0;"))
        conn.execute(text("ALTER TABLE parcels ADD COLUMN IF NOT EXISTS viability_rank TEXT;"))

    print("Fetching enriched parcels for scoring...")
    with engine.connect() as conn:
        parcels = conn.execute(text("""
            SELECT "OBJECTID", enviro_status, grid_status, zoning_status, physical_status, legal_social_status 
            FROM parcels
        """)).fetchall()
        
    print(f"Scoring {len(parcels)} parcels...")
    
    with engine.begin() as conn:
        for p in parcels:
            oid, enviro, grid, zoning, physical, legal = p
            
            score = 50.0 # Baseline
            flags = []

            # 1. Grid (Max +30, Min -100)
            if grid:
                if grid.get("status") == "VIABLE":
                    score += 30
                    if grid.get("capacity_mw", 0) > 2.0: score += 10
                elif grid.get("status") == "CONGESTED":
                    score -= 80
                    flags.append("CONGESTED_GRID")
            
            # 2. Environmental (Deal Killer)
            if enviro:
                overlap = enviro.get("wetlands_overlap_pct", 1.0)
                if overlap > 0.4:
                    score -= 100
                    flags.append("HIGH_WETLAND_IMPACT")
                elif overlap < 0.1:
                    score += 20
            
            # 3. Zoning (Max +20)
            if zoning:
                if zoning.get("use_type") == "BY_RIGHT":
                    score += 20
                elif zoning.get("use_type") == "PROHIBITED":
                    score -= 100
                    flags.append("ZONING_PROHIBITED")
                
                if zoning.get("status") == "NON_VIABLE":
                    score -= 50 # likely lot size issue
            
            # 4. Physical (Max +15)
            if physical:
                slope = physical.get("mean_slope_pct", 20.0)
                if slope < 5.0: score += 15
                elif slope > 15.0: 
                    score -= 60
                    flags.append("STEEP_SLOPE")
            
            # 5. Legal/Social (Max +10)
            if legal:
                if legal.get("owner_type") == "MUNICIPAL":
                    score += 15
                risk = legal.get("social_risk_score", 10.0)
                if risk < 3.0: score += 5
                elif risk > 7.0: score -= 20

            # Normalize 0-100
            final_score = max(0, min(100, score)) / 100.0
            
            rank = "POOR"
            if final_score > 0.8: rank = "EXCELLENT"
            elif final_score > 0.6: rank = "GOOD"
            elif final_score > 0.4: rank = "FAIR"
            
            conn.execute(
                text('UPDATE parcels SET viability_score = :score, viability_rank = :rank WHERE "OBJECTID" = :oid'),
                {"score": final_score, "rank": rank, "oid": oid}
            )

    print("Scoring complete.")

if __name__ == "__main__":
    calculate_viability()
