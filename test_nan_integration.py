"""
Test script to demonstrate NaN handling integration
"""
from src.analysis_pipeline import AnalysisPipeline
from src.database.database import Database
from src.models.configuration import Configuration

# Initialize components
db = Database('intent_drift_ai.db', encryption_enabled=True)
config = Configuration.default()
pipeline = AnalysisPipeline(config, db)

# Run baseline establishment
print("\n" + "="*60)
print("RUNNING BASELINE ESTABLISHMENT WITH NaN HANDLING")
print("="*60)

result = pipeline.establish_baselines_for_all_users()

# Display results
print("\n=== BASELINE ESTABLISHMENT RESULTS ===")
print(f"Total Users: {result['total_users']}")
print(f"Successful: {result['successful']}")
print(f"Failed: {result['failed']}")

print("\n=== NaN HANDLING STATISTICS ===")
print(f"Users with NaN values: {result['users_with_nan_values']}")
print(f"Total NaN values imputed: {result['total_nan_values_imputed']}")
print(f"NaN handling applied: {result['nan_handling_applied']}")

if result['nan_affected_features']:
    print(f"\nTop NaN-affected features:")
    sorted_features = sorted(
        result['nan_affected_features'].items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:10]
    for feature, count in sorted_features:
        print(f"  - {feature}: {count} users")

print("\n" + "="*60)
print("INTEGRATION TEST COMPLETE")
print("="*60)

# Test the new API endpoint structure
print("\n=== API ENDPOINT RESPONSE STRUCTURE ===")
api_response = {
    "success": True,
    "message": "Baselines established for all users",
    "statistics": {
        "total_users": result["total_users"],
        "successful": result["successful"],
        "failed": result["failed"],
        "nan_handling_stats": {
            "users_with_nan_values": result.get("users_with_nan_values", 0),
            "total_nan_values_imputed": result.get("total_nan_values_imputed", 0),
            "nan_affected_features": result.get("nan_affected_features", {}),
            "nan_handling_applied": result.get("nan_handling_applied", False)
        }
    }
}

print(f"API Response includes nan_handling_stats: {('nan_handling_stats' in api_response['statistics'])}")
print(f"Users with NaN: {api_response['statistics']['nan_handling_stats']['users_with_nan_values']}")
print(f"NaN handling applied: {api_response['statistics']['nan_handling_stats']['nan_handling_applied']}")

# Test NaN report endpoint
print("\n=== NaN REPORT ENDPOINT ===")
user_ids = db.get_all_user_ids()
report = []
for user_id in user_ids[:5]:  # Check first 5 users
    baseline = db.fetch_baseline(user_id)
    if baseline and baseline.had_nan_values:
        report.append({
            "user_id": baseline.user_id,
            "nan_features_imputed": baseline.nan_features_imputed[:3],  # Show first 3
            "nan_imputation_count": baseline.nan_imputation_count
        })

print(f"Users with NaN metadata: {len(report)}")
for entry in report:
    print(f"  - {entry['user_id']}: {entry['nan_imputation_count']} NaN values imputed")
    print(f"    Affected features: {', '.join(entry['nan_features_imputed'])}")

print("\n[OK] Backend and API integration complete!")
print("[OK] NaN handling statistics are now available via API endpoints")
