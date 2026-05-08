"""
Baseline Modeling Engine
Learns normal behavioral patterns using Isolation Forest
"""
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from src.models.data_models import UserActivity, BehavioralBaseline
from src.models.configuration import Configuration
from src.ml.feature_extractor import FeatureExtractor


class BaselineModeler:
    """Learns and stores behavioral baselines for users"""
    
    def __init__(self, config: Configuration):
        self.config = config
        self.feature_extractor = FeatureExtractor(config)
    
    def establish_baseline(self, user_id: str, activities: List[UserActivity]) -> BehavioralBaseline:
        """
        Establish behavioral baseline from historical activities
        
        Args:
            user_id: User identifier
            activities: Historical activities (minimum 30 days recommended)
        
        Returns:
            BehavioralBaseline object with trained model
        """
        if not activities:
            raise ValueError(f"No activities provided for user {user_id}")
        
        # Sort activities by timestamp
        activities = sorted(activities, key=lambda x: x.timestamp)
        
        # Use only the first 30 days for baseline (to avoid including threat behavior)
        baseline_start = activities[0].timestamp
        baseline_cutoff = baseline_start + timedelta(days=30)
        baseline_activities = [a for a in activities if a.timestamp <= baseline_cutoff]
        
        if not baseline_activities:
            raise ValueError(f"No activities in baseline period for user {user_id}")
        
        baseline_end = baseline_activities[-1].timestamp
        
        # Check if we have enough data
        baseline_days = (baseline_end - baseline_start).days
        if baseline_days < self.config.baseline_minimum_days:
            raise ValueError(f"Insufficient baseline period: {baseline_days} days (minimum {self.config.baseline_minimum_days})")
        
        # Extract features from sliding windows
        feature_vectors, feature_names = self._extract_windowed_features(baseline_activities)
        
        if len(feature_vectors) < 10:
            raise ValueError(f"Insufficient feature vectors: {len(feature_vectors)} (minimum 10)")
        
        # Train Isolation Forest model
        model = IsolationForest(
            contamination=0.1,  # Assume 10% of baseline data might be anomalous
            random_state=42,
            n_estimators=100
        )
        
        # Fit model on feature vectors
        X = np.array(feature_vectors)
        model.fit(X)
        
        # Calculate feature distributions
        feature_distributions = self._calculate_feature_distributions(feature_vectors, feature_names)
        
        # Calculate activity patterns
        activity_patterns = self._calculate_activity_patterns(baseline_activities)
        
        # Create baseline object
        baseline = BehavioralBaseline(
            user_id=user_id,
            baseline_start=baseline_start,
            baseline_end=baseline_end,
            model_data=b'',  # Will be set below
            feature_distributions=feature_distributions,
            activity_patterns=activity_patterns
        )
        
        # Serialize model
        baseline.model_data = baseline.serialize_model({
            'isolation_forest': model,
            'scaler': StandardScaler().fit(X),
            'feature_names': feature_names
        })
        
        return baseline
    
    def _extract_windowed_features(self, activities: List[UserActivity], 
                                   window_days: int = 7) -> Tuple[List[List[float]], List[str]]:
        """
        Extract features from sliding time windows
        
        Returns:
            Tuple of (feature_vectors, feature_names)
        """
        if not activities:
            return [], []
        
        activities = sorted(activities, key=lambda x: x.timestamp)
        start_date = activities[0].timestamp
        end_date = activities[-1].timestamp
        
        feature_vectors = []
        feature_names = None
        
        # Slide window across time period
        current_date = start_date
        while current_date <= end_date:
            window_end = current_date + timedelta(days=window_days)
            
            # Get activities in window
            window_activities = [
                a for a in activities 
                if current_date <= a.timestamp < window_end
            ]
            
            if len(window_activities) >= 5:  # Minimum activities per window
                features = self.feature_extractor.extract_features(window_activities, window_end)
                
                if feature_names is None:
                    feature_names = sorted(features.keys())
                
                # Convert to vector
                vector = [features[name] for name in feature_names]
                feature_vectors.append(vector)
            
            # Move window forward by 1 day
            current_date += timedelta(days=1)
        
        return feature_vectors, feature_names
    
    def _calculate_feature_distributions(self, feature_vectors: List[List[float]], 
                                        feature_names: List[str]) -> Dict[str, Dict]:
        """Calculate statistical distributions for each feature"""
        if not feature_vectors or not feature_names:
            return {}
        
        X = np.array(feature_vectors)
        distributions = {}
        
        for i, name in enumerate(feature_names):
            values = X[:, i]
            distributions[name] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'median': float(np.median(values)),
                'q25': float(np.percentile(values, 25)),
                'q75': float(np.percentile(values, 75))
            }
        
        return distributions
    
    def _calculate_activity_patterns(self, activities: List[UserActivity]) -> Dict[str, float]:
        """Calculate high-level activity patterns"""
        if not activities:
            return {}
        
        total = len(activities)
        
        # Action distribution
        action_counts = {}
        for activity in activities:
            action_counts[activity.action] = action_counts.get(activity.action, 0) + 1
        
        action_distribution = {
            action: count / total 
            for action, count in action_counts.items()
        }
        
        # Resource type distribution
        resource_type_counts = {}
        for activity in activities:
            resource_type_counts[activity.resource_type] = resource_type_counts.get(activity.resource_type, 0) + 1
        
        resource_type_distribution = {
            rtype: count / total 
            for rtype, count in resource_type_counts.items()
        }
        
        # Time patterns
        hour_counts = {}
        for activity in activities:
            hour = activity.timestamp.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Peak hours
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'total_activities': total,
            'action_distribution': action_distribution,
            'resource_type_distribution': resource_type_distribution,
            'peak_hours': [h for h, _ in peak_hours],
            'avg_daily_activities': total / max(1, (activities[-1].timestamp - activities[0].timestamp).days)
        }
    
    def predict_anomaly_score(self, baseline: BehavioralBaseline, 
                             current_activities: List[UserActivity]) -> float:
        """
        Predict anomaly score for current activities using baseline model
        
        Returns:
            Anomaly score (0-1, higher = more anomalous)
        """
        if not current_activities:
            return 0.0
        
        # Deserialize model
        model_dict = baseline.deserialize_model()
        isolation_forest = model_dict['isolation_forest']
        scaler = model_dict['scaler']
        feature_names = model_dict['feature_names']
        
        # Extract features from current activities
        features = self.feature_extractor.extract_features(current_activities)
        
        # Convert to vector in same order as training
        vector = np.array([[features.get(name, 0) for name in feature_names]])
        
        # Scale features
        vector_scaled = scaler.transform(vector)
        
        # Get anomaly score from Isolation Forest
        # Score is in range [-1, 1], where -1 is most anomalous
        # We convert to [0, 1] where 1 is most anomalous
        score = isolation_forest.score_samples(vector_scaled)[0]
        anomaly_score = (1 - score) / 2  # Convert [-1, 1] to [0, 1]
        
        return float(np.clip(anomaly_score, 0, 1))
