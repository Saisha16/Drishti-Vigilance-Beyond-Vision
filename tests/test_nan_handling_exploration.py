"""
Bug Condition Exploration Test for NaN Handling in Baseline Establishment

**CRITICAL**: This test is EXPECTED TO FAIL on unfixed code.
The test failure confirms that the bug exists.

**DO NOT attempt to fix the test or the code when it fails.**

This test generates synthetic user activity datasets known to produce NaN values
during feature extraction, then attempts baseline establishment on UNFIXED code.

Expected Outcome: Test FAILS with "Input X contains NaN" error
"""
import pytest
import numpy as np
from datetime import datetime, timedelta
from typing import List

from src.models.data_models import UserActivity
from src.models.configuration import Configuration
from src.ml.baseline_modeler import BaselineModeler


def generate_sparse_activity_user(user_id: str = "sparse_user") -> List[UserActivity]:
    """
    Generate user with sparse activities that pass validation but produce NaN.
    
    Strategy: Create exactly 5 activities per 7-day window for 20 days.
    This gives us ~14 feature vectors (enough to pass validation).
    The extreme sparsity (only 5 activities per window, minimum allowed)
    will produce NaN in std calculations and diversity metrics.
    """
    base_time = datetime(2024, 1, 1, 10, 0, 0)
    activities = []
    
    # Create 5 activities every 7 days for 20 days (15 total activities)
    # Spread them to ensure each 7-day window has exactly 5
    for day in [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18]:
        activities.append(
            UserActivity(
                user_id=user_id,
                timestamp=base_time + timedelta(days=day, hours=10),
                action="read",
                resource_id=f"doc_{day}",
                resource_type="documents",
                metadata={}
            )
        )
    
    return activities


def generate_single_hour_activity_user(user_id: str = "single_hour_user") -> List[UserActivity]:
    """
    Generate user with all activities in the same hour (14:00) over 20 days.
    This produces NaN in std_hour_of_activity (std of constant value = 0 or NaN).
    
    Strategy: 5-6 activities per day at hour 14, spread over 20 days.
    This ensures enough feature vectors while maintaining zero hour diversity.
    """
    base_time = datetime(2024, 1, 1, 14, 0, 0)  # Always at 2 PM
    activities = []
    
    # Create 5-6 activities per day for 20 days, all at hour 14
    for day in range(20):
        for minute in range(5):
            activities.append(
                UserActivity(
                    user_id=user_id,
                    timestamp=base_time + timedelta(days=day, minutes=minute * 10),
                    action="read",
                    resource_id=f"doc_{day}_{minute}",
                    resource_type="documents",
                    metadata={}
                )
            )
    
    return activities


def generate_single_resource_user(user_id: str = "single_resource_user") -> List[UserActivity]:
    """
    Generate user accessing only one resource repeatedly over 30+ days.
    This produces NaN in resource diversity and concentration metrics.
    
    Strategy: 100 activities over 30 days, all accessing same resource.
    This ensures enough feature vectors but with zero diversity.
    """
    base_time = datetime(2024, 1, 1, 10, 0, 0)
    activities = []
    
    # Create 100 activities over 30 days, all accessing the same resource
    for i in range(100):
        activities.append(
            UserActivity(
                user_id=user_id,
                timestamp=base_time + timedelta(hours=i * 7),  # Spread over ~29 days
                action="read",
                resource_id="doc_1",  # Same resource every time
                resource_type="documents",
                metadata={}
            )
        )
    
    return activities


def generate_no_business_hours_user(user_id: str = "no_business_hours_user") -> List[UserActivity]:
    """
    Generate user with no activities during business hours (9 AM - 5 PM) over 30+ days.
    This may produce NaN in business_hours_ratio calculations (0/0).
    
    Strategy: 80 activities over 30 days, all outside business hours.
    """
    base_time = datetime(2024, 1, 1, 22, 0, 0)  # 10 PM
    activities = []
    
    # Create 80 activities over 30 days, all outside business hours
    for i in range(80):
        # Alternate between late night (22:00) and early morning (6:00)
        hour = 22 if i % 2 == 0 else 6
        activities.append(
            UserActivity(
                user_id=user_id,
                timestamp=base_time + timedelta(hours=i * 9, days=i // 8),  # Spread over ~30 days
                action="read",
                resource_id=f"doc_{i}",
                resource_type="documents",
                metadata={}
            )
        )
    
    return activities


def generate_seven_day_gap_user(user_id: str = "seven_day_gap_user") -> List[UserActivity]:
    """
    Generate user with 7-day gaps in activity over 60+ days.
    This produces windows with < 5 activities, leading to NaN in statistical calculations.
    
    Strategy: Bursts of 6 activities, then 7-day gaps, repeated over 60 days.
    """
    base_time = datetime(2024, 1, 1, 10, 0, 0)
    activities = []
    
    # Create activity bursts with 7-day gaps (need 60+ days to get enough vectors)
    for burst in range(10):
        # Add 6 activities per burst (within a few hours)
        for i in range(6):
            activities.append(
                UserActivity(
                    user_id=user_id,
                    timestamp=base_time + timedelta(days=burst * 7, hours=i),
                    action="read",
                    resource_id=f"doc_{burst * 6 + i}",
                    resource_type="documents",
                    metadata={}
                )
            )
    
    return activities


class TestNaNHandlingExploration:
    """
    Bug Condition Exploration Tests
    
    These tests encode the EXPECTED BEHAVIOR (what should happen after the fix).
    On UNFIXED code, these tests will FAIL, confirming the bug exists.
    On FIXED code, these tests will PASS, confirming the bug is resolved.
    """
    
    @pytest.fixture
    def config(self):
        """Create default configuration"""
        return Configuration.default()
    
    @pytest.fixture
    def baseline_modeler(self, config):
        """Create baseline modeler instance"""
        return BaselineModeler(config)
    
    def test_sparse_activity_baseline_establishment(self, baseline_modeler):
        """
        Test: User with sparse activity (3 activities over 30 days) should successfully establish baseline.
        
        Expected on UNFIXED code: FAILS with "Input X contains NaN"
        Expected on FIXED code: PASSES - baseline established successfully
        
        Validates: Requirements 2.1, 2.2, 2.3
        """
        activities = generate_sparse_activity_user()
        
        # Attempt baseline establishment
        # On unfixed code, this will raise ValueError with "Input X contains NaN"
        # On fixed code, this should succeed
        baseline = baseline_modeler.establish_baseline("sparse_user", activities)
        
        # Assert baseline was created successfully
        assert baseline is not None, "Baseline should be created"
        assert baseline.user_id == "sparse_user"
        assert baseline.model_data is not None, "Model data should exist"
        assert len(baseline.model_data) > 0, "Model data should not be empty"
        
        # Verify baseline can be used for predictions (model is valid)
        model_dict = baseline.deserialize_model()
        assert 'isolation_forest' in model_dict, "IsolationForest model should exist"
        assert 'feature_names' in model_dict, "Feature names should exist"
        
        # Verify no NaN values in feature distributions
        for feature_name, distribution in baseline.feature_distributions.items():
            assert not np.isnan(distribution['mean']), f"Feature {feature_name} mean should not be NaN"
            assert not np.isnan(distribution['std']), f"Feature {feature_name} std should not be NaN"
            assert not np.isnan(distribution['min']), f"Feature {feature_name} min should not be NaN"
            assert not np.isnan(distribution['max']), f"Feature {feature_name} max should not be NaN"
    
    def test_single_hour_activity_baseline_establishment(self, baseline_modeler):
        """
        Test: User with all activities in same hour should successfully establish baseline.
        
        Expected on UNFIXED code: FAILS with "Input X contains NaN"
        Expected on FIXED code: PASSES - baseline established successfully
        
        Validates: Requirements 2.1, 2.2, 2.3
        """
        activities = generate_single_hour_activity_user()
        
        baseline = baseline_modeler.establish_baseline("single_hour_user", activities)
        
        assert baseline is not None
        assert baseline.user_id == "single_hour_user"
        assert baseline.model_data is not None
        assert len(baseline.model_data) > 0
        
        # Verify model is valid
        model_dict = baseline.deserialize_model()
        assert 'isolation_forest' in model_dict
        
        # Verify no NaN in feature distributions
        for feature_name, distribution in baseline.feature_distributions.items():
            assert not np.isnan(distribution['mean']), f"Feature {feature_name} should not have NaN mean"
    
    def test_single_resource_baseline_establishment(self, baseline_modeler):
        """
        Test: User accessing single resource should successfully establish baseline.
        
        Expected on UNFIXED code: FAILS with "Input X contains NaN"
        Expected on FIXED code: PASSES - baseline established successfully
        
        Validates: Requirements 2.1, 2.2, 2.3
        """
        activities = generate_single_resource_user()
        
        baseline = baseline_modeler.establish_baseline("single_resource_user", activities)
        
        assert baseline is not None
        assert baseline.user_id == "single_resource_user"
        assert baseline.model_data is not None
        assert len(baseline.model_data) > 0
        
        # Verify no NaN in feature distributions
        for feature_name, distribution in baseline.feature_distributions.items():
            assert not np.isnan(distribution['mean']), f"Feature {feature_name} should not have NaN mean"
            assert not np.isnan(distribution['std']), f"Feature {feature_name} should not have NaN std"
    
    def test_no_business_hours_baseline_establishment(self, baseline_modeler):
        """
        Test: User with no business hours activity should successfully establish baseline.
        
        Expected on UNFIXED code: FAILS with "Input X contains NaN"
        Expected on FIXED code: PASSES - baseline established successfully
        
        Validates: Requirements 2.1, 2.2, 2.3
        """
        activities = generate_no_business_hours_user()
        
        baseline = baseline_modeler.establish_baseline("no_business_hours_user", activities)
        
        assert baseline is not None
        assert baseline.user_id == "no_business_hours_user"
        assert baseline.model_data is not None
        assert len(baseline.model_data) > 0
        
        # Verify no NaN in feature distributions
        for feature_name, distribution in baseline.feature_distributions.items():
            assert not np.isnan(distribution['mean']), f"Feature {feature_name} should not have NaN mean"
    
    def test_seven_day_gap_baseline_establishment(self, baseline_modeler):
        """
        Test: User with 7-day gaps should successfully establish baseline.
        
        Expected on UNFIXED code: FAILS with "Input X contains NaN"
        Expected on FIXED code: PASSES - baseline established successfully
        
        Validates: Requirements 2.1, 2.2, 2.3
        """
        activities = generate_seven_day_gap_user()
        
        baseline = baseline_modeler.establish_baseline("seven_day_gap_user", activities)
        
        assert baseline is not None
        assert baseline.user_id == "seven_day_gap_user"
        assert baseline.model_data is not None
        assert len(baseline.model_data) > 0
        
        # Verify no NaN in feature distributions
        for feature_name, distribution in baseline.feature_distributions.items():
            assert not np.isnan(distribution['mean']), f"Feature {feature_name} should not have NaN mean"
    
    def test_all_synthetic_users_combined(self, baseline_modeler):
        """
        Test: All synthetic users with NaN-producing patterns should successfully establish baselines.
        
        This is a comprehensive test that validates all bug conditions together.
        
        Expected on UNFIXED code: FAILS with "Input X contains NaN" for multiple users
        Expected on FIXED code: PASSES - all baselines established successfully
        
        Validates: Requirements 2.1, 2.2, 2.3
        """
        test_cases = [
            ("sparse_user", generate_sparse_activity_user()),
            ("single_hour_user", generate_single_hour_activity_user()),
            ("single_resource_user", generate_single_resource_user()),
            ("no_business_hours_user", generate_no_business_hours_user()),
            ("seven_day_gap_user", generate_seven_day_gap_user()),
        ]
        
        baselines = []
        errors = []
        
        for user_id, activities in test_cases:
            try:
                baseline = baseline_modeler.establish_baseline(user_id, activities)
                baselines.append(baseline)
                
                # Verify baseline is valid
                assert baseline is not None
                assert baseline.model_data is not None
                assert len(baseline.model_data) > 0
                
                # Verify no NaN in feature distributions
                for feature_name, distribution in baseline.feature_distributions.items():
                    if np.isnan(distribution['mean']):
                        errors.append(f"{user_id}: Feature {feature_name} has NaN mean")
                    if np.isnan(distribution['std']):
                        errors.append(f"{user_id}: Feature {feature_name} has NaN std")
                
            except Exception as e:
                errors.append(f"{user_id}: {str(e)}")
        
        # All users should successfully establish baselines
        assert len(baselines) == len(test_cases), f"Expected {len(test_cases)} baselines, got {len(baselines)}"
        
        # No errors should occur
        if errors:
            error_msg = "\n".join(errors)
            pytest.fail(f"Errors occurred during baseline establishment:\n{error_msg}")
    
    def test_baseline_can_predict_anomaly_scores(self, baseline_modeler):
        """
        Test: Baselines established from sparse data should be able to predict anomaly scores.
        
        This validates that the baseline model is not just created, but is actually functional.
        
        Expected on UNFIXED code: FAILS (baseline not created due to NaN)
        Expected on FIXED code: PASSES - predictions work correctly
        
        Validates: Requirements 2.2, 2.3
        """
        activities = generate_sparse_activity_user()
        baseline = baseline_modeler.establish_baseline("sparse_user", activities)
        
        # Create new activities for prediction
        new_activities = [
            UserActivity(
                user_id="sparse_user",
                timestamp=datetime(2024, 2, 1, 10, 0, 0),
                action="read",
                resource_id="doc_new",
                resource_type="documents",
                metadata={}
            )
        ]
        
        # Predict anomaly score
        anomaly_score = baseline_modeler.predict_anomaly_score(baseline, new_activities)
        
        # Verify score is valid
        assert not np.isnan(anomaly_score), "Anomaly score should not be NaN"
        assert not np.isinf(anomaly_score), "Anomaly score should not be inf"
        assert 0.0 <= anomaly_score <= 1.0, f"Anomaly score should be in [0, 1], got {anomaly_score}"
