import subprocess
import argparse
import sys

def run_pipeline(module, args=[]):
    print(f"\n>>> Running {module}...")
    cmd = [sys.executable, "-m", module] + args
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"Error: {module} failed.")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Apollo Pipeline Orchestrator")
    parser.add_argument("--towns", type=str, help="Comma separated Town IDs", default="8")
    args = parser.parse_args()
    
    town_ids = args.towns.split(",")
    
    for i, tid in enumerate(town_ids):
        print(f"\n{'='*40}")
        print(f"STARTING INGESTION FOR TOWN {tid}")
        print(f"{'='*40}")
        
        # 1. Base Parcels (Append if not first town)
        append_flag = ["--append"] if i > 0 else []
        if not run_pipeline("pipelines.00_base_parcels.ingest", ["--town", tid] + append_flag):
            continue
            
        # 2. Environmental (Calculates intersection for all in DB)
        run_pipeline("pipelines.03_environmental.ingest")
        
        # 3. Grid (Using mock for now for all in DB)
        run_pipeline("pipelines.01_grid.mock_ingest")
        
        # 4. Zoning
        run_pipeline("pipelines.02_zoning.ingest")
        
        # 5. Physical
        run_pipeline("pipelines.04_physical.ingest")
        
        # 6. Legal
        run_pipeline("pipelines.06_legal_social.ingest")
        
        # 7. Infrastructure (Fixed)
        run_pipeline("pipelines.05_infrastructure.ingest")
        
        # 8. Scoring
        run_pipeline("pipelines.scoring_engine")

    print("\nOrchestration Complete. All towns enriched.")

if __name__ == "__main__":
    main()
