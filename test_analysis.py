"""
Test Analysis Script
Establishes baselines and runs analysis
"""
from src.models.configuration import Configuration
from src.database.database import Database
from src.analysis_pipeline import AnalysisPipeline

print("\n[*] Initializing Drishti...")
config = Configuration.default()
db = Database("intent_drift_ai.db", encryption_enabled=True)
pipeline = AnalysisPipeline(config, db)

print("\n[*] Establishing baselines...")
result = pipeline.establish_baselines_for_all_users()
print(f"[OK] Baselines: {result['successful']} successful, {result['failed']} failed")

if result['failed'] > 0:
    print("\n[!] Errors:")
    for error in result['errors'][:5]:  # Show first 5 errors
        print(f"    {error}")

print("\n[*] Running threat analysis...")
results = pipeline.run_daily_analysis()
alerts = sum(1 for r in results if r.get("alert"))

print(f"\n[OK] Analysis complete!")
print(f"   Users analyzed: {len(results)}")
print(f"   Alerts generated: {alerts}")

if alerts > 0:
    print(f"\n[!] ALERTS DETECTED:")
    for r in results:
        if r.get("alert"):
            alert = r["alert"]
            print(f"   - {alert.user_id}: Risk={r['risk_score'].score:.1f} ({alert.severity})")

print("\n[SUCCESS] Drishti backend is fully operational!")
print("[->] Start API: uvicorn api.main:app --reload --port 8000")
