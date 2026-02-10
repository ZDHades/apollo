import os
import json
import math
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DATABASE_URL", "postgresql://apollo:solar_password@localhost:5432/apollo")

def calculate_viability():
    print("Connecting to database...")
    engine = create_engine(DB_URL)
    
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE parcels ADD COLUMN IF NOT EXISTS viability_score FLOAT DEFAULT 0.0;"))
        conn.execute(text("ALTER TABLE parcels ADD COLUMN IF NOT EXISTS viability_rank TEXT;"))

    print("Scoring all parcels (Topographic Yield Model V4)...")
    with engine.connect() as conn:
        parcels = conn.execute(text("""
            SELECT "OBJECTID", enviro_status, grid_status, zoning_status, physical_status, legal_social_status, infrastructure_status 
            FROM parcels
        """)).fetchall()
        
    print(f"Processing {len(parcels)} records...")
    
    with engine.begin() as conn:
        for p in parcels:
            oid, enviro, grid, zoning, physical, legal, infra = p
            
            # Baseline
            score = 60.0 
            
            # --- 1. SOLAR YIELD POTENTIAL (Granular) ---
            # Instead of a constant, we adjust yield based on Aspect (orientation).
            # Ideal aspect is 180 (South).
            yield_multiplier = 1.0
            if physical:
                aspect = physical.get("mean_aspect_deg", 180)
                slope = physical.get("mean_slope_pct", 0)
                
                # Difference from South (0 to 180)
                diff_from_south = abs(180 - aspect)
                if diff_from_south > 180: diff_from_south = 360 - diff_from_south
                
                # Penalize North-facing slopes (> 90 deg from South)
                # Especially if the slope is steep.
                if diff_from_south > 90:
                    yield_penalty = (diff_from_south - 90) / 90.0 * (slope / 20.0)
                    yield_multiplier -= min(0.3, yield_penalty) # Max 30% yield loss
                
                # Bonus for perfect South-facing gentle slopes
                if diff_from_south < 30 and slope < 10:
                    score += 15
                elif diff_from_south > 135: # Strong North-facing
                    score -= 25

            # --- 2. ZONING ---
            if zoning:
                if zoning.get("use_type") == "BY_RIGHT":
                    score += 25
                elif zoning.get("use_type") == "PROHIBITED":
                    score -= 40 
                if zoning.get("status") == "NON_VIABLE":
                    score -= 15
            
            # --- 3. SOCIAL/OWNER ---
            if legal:
                if legal.get("owner_type") == "MUNICIPAL":
                    score += 20 
                if legal.get("conservation_restriction"):
                    score -= 80
            
            # --- 4. ENVIRONMENTAL ---
            if enviro:
                overlap = enviro.get("wetlands_overlap_pct", 0.0)
                if overlap > 0.1:
                    score -= (overlap * 100)
                if overlap > 0.4:
                    score -= 30
            
            # --- 5. GRID ---
            if grid:
                if grid.get("status") == "CONGESTED":
                    score -= 50
            
            # --- 6. INFRASTRUCTURE ---
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
