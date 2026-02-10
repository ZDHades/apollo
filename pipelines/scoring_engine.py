import os
import json
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DATABASE_URL", "postgresql://apollo:solar_password@localhost:5432/apollo")

def calculate_viability():
    print("Connecting to database...")
    engine = create_engine(DB_URL)
    
    # Ensure columns exist
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE parcels ADD COLUMN IF NOT EXISTS viability_score FLOAT DEFAULT 0.0;"))
        conn.execute(text("ALTER TABLE parcels ADD COLUMN IF NOT EXISTS viability_rank TEXT;"))

    print("Fetching enriched parcels for scoring...")
    with engine.connect() as conn:
        parcels = conn.execute(text("""
            SELECT "OBJECTID", enviro_status, grid_status, zoning_status, physical_status, legal_social_status, infrastructure_status 
            FROM parcels
        """)).fetchall()
        
    print(f"Scoring {len(parcels)} parcels (Friction-based model)...")
    
    with engine.begin() as conn:
        for p in parcels:
            oid, enviro, grid, zoning, physical, legal, infra = p
            
            # Baseline
            score = 40.0 
            
            # --- 1. ZONING FRICTION (Highest priority for implementation) ---
            if zoning:
                # By-right vs Special Permit is the biggest predictor of success
                if zoning.get("use_type") == "BY_RIGHT":
                    score += 40 # Major reduction in friction
                elif zoning.get("use_type") == "SPECIAL_PERMIT":
                    score -= 10 # Moderate friction (discretionary)
                elif zoning.get("use_type") == "PROHIBITED":
                    score -= 100 # Total friction
                
                if zoning.get("status") == "NON_VIABLE":
                    score -= 40 # Usually lot size, which is a hard friction point
            
            # --- 2. SOCIAL & POLITICAL FRICTION ---
            if legal:
                # Municipal owners want these projects (Revenue + Clean Energy goals)
                if legal.get("owner_type") == "MUNICIPAL":
                    score += 30 # Low friction path
                
                # Abutter risk (NIMBYism)
                risk_score = legal.get("social_risk_score", 5.0)
                if risk_score < 2.0:
                    score += 10 # Isolated
                elif risk_score > 6.0:
                    score -= 30 # High friction (neighborhood opposition)
                    
                if legal.get("conservation_restriction"):
                    score -= 100 # Permanent legal friction
            
            # --- 3. ENVIRONMENTAL FRICTION (Permitting hurdles) ---
            if enviro:
                overlap = enviro.get("wetlands_overlap_pct", 1.0)
                if overlap > 0.3:
                    score -= 100 # Wetlands are the #1 deal killer
                elif overlap < 0.05:
                    score += 15 # Clean sheet
            
            # --- 4. GRID (Technical but binary) ---
            if grid:
                if grid.get("status") == "VIABLE":
                    score += 10 
                elif grid.get("status") == "CONGESTED":
                    score -= 100 # No interconnection = No implementation
            
            # --- 5. INFRASTRUCTURE (Access ease) ---
            if infra:
                if infra.get("frontage_ft", 0) > 100:
                    score += 10 # Easy legal access
                elif infra.get("frontage_ft", 0) < 20:
                    score -= 20 # Potential access friction

            # --- 6. PHYSICAL (Engineering cost/friction) ---
            if physical:
                slope = physical.get("mean_slope_pct", 20.0)
                if slope > 15.0:
                    score -= 40 # Significant engineering friction
                elif slope < 7.0:
                    score += 5

            # Normalize 0-100
            final_score = max(0, min(100, score)) / 100.0
            
            rank = "POOR"
            if final_score > 0.85: rank = "EXCELLENT" # High bar for frictionless
            elif final_score > 0.65: rank = "GOOD"
            elif final_score > 0.45: rank = "FAIR"
            
            conn.execute(
                text('UPDATE parcels SET viability_score = :score, viability_rank = :rank WHERE "OBJECTID" = :oid'),
                {"score": final_score, "rank": rank, "oid": oid}
            )

    print("Scoring complete.")

if __name__ == "__main__":
    calculate_viability()
