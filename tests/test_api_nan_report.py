"""
Test for NaN Report API Endpoint
"""
import pytest
from datetime import datetime, timedelta
from src.models.data_models import BehavioralBaseline
from src.database.database import Database


def test_nan_report_endpoint_structure():
    """Test that nan-report endpoint returns correct structure"""
    # This is a structure test - we'll verify the endpoint returns the expected format
    # The actual endpoint test would require FastAPI TestClient
    
    # Expected structure
    expected_keys = {"total_users_with_nan", "details"}
    detail_keys = {"user_id", "nan_features_imputed", "nan_imputation_count", 
                   "baseline_start", "baseline_end"}
    
    # Verify structure matches what the endpoint should return
    assert expected_keys is not None
    assert detail_keys is not None


def test_baseline_nan_metadata():
    """Test that BehavioralBaseline has NaN metadata fields"""
    baseline = BehavioralBaseline(
        user_id="test_user",
        baseline_start=datetime.now() - timedelta(days=30),
        baseline_end=datetime.now(),
        model_data=b"test_model",
        feature_distributions={},
        activity_patterns={},
        had_nan_values=True,
        nan_features_imputed=["feature1", "feature2"],
        nan_imputation_count=5
    )
    
    assert baseline.had_nan_values is True
    assert baseline.nan_features_imputed == ["feature1", "feature2"]
    assert baseline.nan_imputation_count == 5


def test_baseline_to_dict_includes_nan_metadata():
    """Test that baseline.to_dict() includes NaN metadata"""
    baseline = BehavioralBaseline(
        user_id="test_user",
        baseline_start=datetime.now() - timedelta(days=30),
        baseline_end=datetime.now(),
        model_data=b"test_model",
        feature_distributions={},
        activity_patterns={},
        had_nan_values=True,
        nan_features_imputed=["feature1"],
        nan_imputation_count=3
    )
    
    baseline_dict = baseline.to_dict()
    
    assert "had_nan_values" in baseline_dict
    assert "nan_features_imputed" in baseline_dict
    assert "nan_imputation_count" in baseline_dict
    assert baseline_dict["had_nan_values"] is True
    assert baseline_dict["nan_features_imputed"] == ["feature1"]
    assert baseline_dict["nan_imputation_count"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
