import os
import json
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DATABASE_URL", "postgresql://apollo:solar_password@localhost:5432/apollo")

def calculate_viability():
    print("Connecting to database...")
    engine = create_engine(DB_URL)
    
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE parcels ADD COLUMN IF NOT EXISTS viability_score FLOAT DEFAULT 0.0;"))
        conn.execute(text("ALTER TABLE parcels ADD COLUMN IF NOT EXISTS viability_rank TEXT;"))

    print("Scoring all parcels (Optimization V3)...")
    with engine.connect() as conn:
        parcels = conn.execute(text("""
            SELECT "OBJECTID", enviro_status, grid_status, zoning_status, physical_status, legal_social_status, infrastructure_status 
            FROM parcels
        """)).fetchall()
        
    print(f"Processing {len(parcels)} records...")
    
    with engine.begin() as conn:
        for p in parcels:
            oid, enviro, grid, zoning, physical, legal, infra = p
            
            # Baseline 70 ensures most parcels stay visible in the 'Amber' range 
            # unless they hit multiple deal-killers.
            score = 70.0 
            
            # 1. ZONING (Largest Friction)
            if zoning:
                if zoning.get("use_type") == "BY_RIGHT":
                    score += 20 
                elif zoning.get("use_type") == "PROHIBITED":
                    score -= 50 # Significant but not an instant zero
                
                if zoning.get("status") == "NON_VIABLE":
                    score -= 15 # Size constraint
            
            # 2. SOCIAL/OWNER
            if legal:
                if legal.get("owner_type") == "MUNICIPAL":
                    score += 15 
                if legal.get("conservation_restriction"):
                    score -= 70 # High friction
            
            # 3. ENVIRONMENTAL
            if enviro:
                overlap = enviro.get("wetlands_overlap_pct", 0.0)
                if overlap > 0.1:
                    score -= (overlap * 100) # Dynamic penalty
                if overlap > 0.4:
                    score -= 30 # Extra heavy penalty for deal-breaker levels
            
            # 4. GRID
            if grid:
                if grid.get("status") == "CONGESTED":
                    score -= 50
            
            # 5. INFRASTRUCTURE
            if infra:
                if infra.get("status") == "VIABLE":
                    score += 5

            final_score = max(0, min(100, score)) / 100.0
            
            rank = "POOR"
            if final_score > 0.8: rank = "EXCELLENT"
            elif final_score > 0.6: rank = "GOOD"
            elif final_score > 0.4: rank = "FAIR"
            
            conn.execute(
                text('UPDATE parcels SET viability_score = :score, viability_rank = :rank WHERE "OBJECTID" = :oid'),
                {"score": final_score, "rank": rank, "oid": oid}
            )

    print("Optimization Complete.")

if __name__ == "__main__":
    calculate_viability()
