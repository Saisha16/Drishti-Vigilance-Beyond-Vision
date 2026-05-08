"""
One-Command Database Setup for Demo
Generates data, ingests it, establishes baselines, runs analysis
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"[*] {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] {result.stderr}")
        sys.exit(1)
    
    print(result.stdout)
    print(f"[OK] {description} - Complete!")


def main():
    print("""
+===========================================================+
|                                                           |
|          DRISHTI DATABASE SETUP                           |
|             Vigilance Beyond Vision                       |
|                                                           |
+===========================================================+
    """)
    
    # Step 1: Generate synthetic data
    run_command(
        "python generate_demo_data.py --output-dir demo_data",
        "Step 1/4: Generating synthetic dataset (100 users, 10 threats)"
    )
    
    # Step 2: Ingest data
    run_command(
        "python ingest_data.py demo_data/activities.json --format json",
        "Step 2/4: Ingesting activity logs into database"
    )
    
    # Step 3: Establish baselines
    print(f"\n{'='*60}")
    print("[*] Step 3/4: Establishing behavioral baselines")
    print(f"{'='*60}")
    
    from src.models.configuration import Configuration
    from src.database.database import Database
    from src.analysis_pipeline import AnalysisPipeline
    
    config = Configuration.default()
    db = Database("intent_drift_ai.db", encryption_enabled=True)
    pipeline = AnalysisPipeline(config, db)
    
    result = pipeline.establish_baselines_for_all_users()
    print(f"[OK] Baselines established: {result['successful']} successful, {result['failed']} failed")
    
    # Step 4: Run initial analysis
    print(f"\n{'='*60}")
    print("[*] Step 4/4: Running initial threat analysis")
    print(f"{'='*60}")
    
    results = pipeline.run_daily_analysis()
    alerts = sum(1 for r in results if r.get("alert"))
    
    print(f"[OK] Analysis complete!")
    print(f"   Users analyzed: {len(results)}")
    print(f"   Alerts generated: {alerts}")
    
    print(f"\n{'='*60}")
    print("[SUCCESS] DATABASE SETUP COMPLETE!")
    print(f"{'='*60}")
    print("\n[*] Next steps:")
    print("   1. Start API: uvicorn api.main:app --reload --port 8000")
    print("   2. View API docs: http://localhost:8000/docs")
    print("   3. Start frontend and connect to API")
    print()


if __name__ == "__main__":
    main()
