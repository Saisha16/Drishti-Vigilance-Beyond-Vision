"""
Behavioral Drift Detection Engine
Detects gradual, sudden, and oscillating behavioral changes using Mann-Kendall test
"""
import numpy as np
from scipy import stats
from datetime import datetime, timedelta
from typing import List, Tuple, Dict

from src.models.data_models import UserActivity, BehavioralBaseline, DriftAnalysis
from src.models.configuration import Configuration
from src.ml.feature_extractor import FeatureExtractor


class DriftDetector:
    """Detects behavioral drift using statistical tests"""
    
    def __init__(self, config: Configuration):
        self.config = config
        self.feature_extractor = FeatureExtractor(config)
    
    def detect_drift(self, user_id: str, baseline: BehavioralBaseline, 
                    recent_activities: List[UserActivity]) -> DriftAnalysis:
        """
        Detect behavioral drift by comparing recent activities to baseline
        
        Args:
            user_id: User identifier
            baseline: Established behavioral baseline
            recent_activities: Recent activities to analyze
        
        Returns:
            DriftAnalysis object with drift detection results
        """
        if not recent_activities:
            return DriftAnalysis(
                user_id=user_id,
                is_drifting=False,
                drift_type="none",
                drift_magnitude=0.0,
                drift_duration_days=0
            )
        
        # Extract features from recent activities in time windows
        window_features = self._extract_temporal_windows(recent_activities)
        
        if len(window_features) < 3:
            # Not enough data points for drift detection
            return DriftAnalysis(
                user_id=user_id,
                is_drifting=False,
                drift_type="none",
                drift_magnitude=0.0,
                drift_duration_days=0
            )
        
        # Calculate feature deviations from baseline
        feature_deviations = self._calculate_feature_deviations(window_features, baseline)
        
        # Perform Mann-Kendall trend test on each feature
        drift_signals = self._mann_kendall_test(feature_deviations)
        
        # Determine drift type and magnitude
        drift_type, drift_magnitude = self._classify_drift(drift_signals, feature_deviations)
        
        # Calculate drift duration
        drift_duration_days = (recent_activities[-1].timestamp - recent_activities[0].timestamp).days
        
        # Identify top deviating features
        top_features = self._identify_top_deviating_features(feature_deviations, baseline)
        
        # Calculate statistical significance
        significance = self._calculate_significance(drift_signals)
        
        is_drifting = drift_magnitude >= self.config.drift_threshold
        
        return DriftAnalysis(
            user_id=user_id,
            is_drifting=is_drifting,
            drift_type=drift_type,
            drift_magnitude=drift_magnitude,
            drift_duration_days=drift_duration_days,
            top_deviating_features=top_features,
            statistical_significance=significance
        )
    
    def _extract_temporal_windows(self, activities: List[UserActivity], 
                                  window_days: int = 7) -> List[Dict[str, float]]:
        """Extract features from sliding time windows"""
        if not activities:
            return []
        
        activities = sorted(activities, key=lambda x: x.timestamp)
        start_date = activities[0].timestamp
        end_date = activities[-1].timestamp
        
        window_features = []
        current_date = start_date
        
        while current_date <= end_date:
            window_end = current_date + timedelta(days=window_days)
            
            # Get activities in window
            window_activities = [
                a for a in activities 
                if current_date <= a.timestamp < window_end
            ]
            
            if len(window_activities) >= 3:
                features = self.feature_extractor.extract_features(window_activities, window_end)
                features['window_start'] = current_date
                window_features.append(features)
            
            # Move window forward
            current_date += timedelta(days=window_days)
        
        return window_features
    
    def _calculate_feature_deviations(self, window_features: List[Dict[str, float]], 
                                     baseline: BehavioralBaseline) -> Dict[str, List[float]]:
        """Calculate how much each feature deviates from baseline"""
        feature_deviations = {}
        
        for window in window_features:
            for feature_name, value in window.items():
                if feature_name == 'window_start':
                    continue
                
                if feature_name not in baseline.feature_distributions:
                    continue
                
                baseline_dist = baseline.feature_distributions[feature_name]
                baseline_mean = baseline_dist['mean']
                baseline_std = baseline_dist['std']
                
                # Calculate z-score (standardized deviation)
                if baseline_std > 0:
                    z_score = (value - baseline_mean) / baseline_std
                else:
                    z_score = 0
                
                if feature_name not in feature_deviations:
                    feature_deviations[feature_name] = []
                
                feature_deviations[feature_name].append(z_score)
        
        return feature_deviations
    
    def _mann_kendall_test(self, feature_deviations: Dict[str, List[float]]) -> Dict[str, Dict]:
        """
        Perform Mann-Kendall trend test on each feature
        
        Returns:
            Dictionary with trend statistics for each feature
        """
        drift_signals = {}
        
        for feature_name, deviations in feature_deviations.items():
            if len(deviations) < 3:
                continue
            
            # Mann-Kendall test
            n = len(deviations)
            s = 0
            
            for i in range(n - 1):
                for j in range(i + 1, n):
                    s += np.sign(deviations[j] - deviations[i])
            
            # Calculate variance
            var_s = n * (n - 1) * (2 * n + 5) / 18
            
            # Calculate z-score
            if s > 0:
                z = (s - 1) / np.sqrt(var_s)
            elif s < 0:
                z = (s + 1) / np.sqrt(var_s)
            else:
                z = 0
            
            # Calculate p-value
            p_value = 2 * (1 - stats.norm.cdf(abs(z)))
            
            # Determine trend direction
            if p_value < 0.05:
                if s > 0:
                    trend = "increasing"
                else:
                    trend = "decreasing"
            else:
                trend = "no_trend"
            
            drift_signals[feature_name] = {
                'trend': trend,
                'z_score': z,
                'p_value': p_value,
                'magnitude': np.mean(np.abs(deviations))
            }
        
        return drift_signals
    
    def _classify_drift(self, drift_signals: Dict[str, Dict], 
                       feature_deviations: Dict[str, List[float]]) -> Tuple[str, float]:
        """
        Classify drift type and calculate overall magnitude
        
        Returns:
            Tuple of (drift_type, drift_magnitude)
        """
        if not drift_signals:
            return "none", 0.0
        
        # Count significant trends
        increasing_count = sum(1 for s in drift_signals.values() if s['trend'] == 'increasing')
        decreasing_count = sum(1 for s in drift_signals.values() if s['trend'] == 'decreasing')
        total_features = len(drift_signals)
        
        # Calculate overall magnitude (average of absolute z-scores)
        magnitudes = [s['magnitude'] for s in drift_signals.values()]
        overall_magnitude = np.mean(magnitudes) if magnitudes else 0.0
        
        # Classify drift type
        if increasing_count + decreasing_count < total_features * 0.2:
            drift_type = "none"
        elif increasing_count > total_features * 0.3 or decreasing_count > total_features * 0.3:
            # Check if drift is sudden or gradual
            drift_type = self._detect_sudden_vs_gradual(feature_deviations)
        else:
            # Check for oscillating pattern
            if self._detect_oscillation(feature_deviations):
                drift_type = "oscillating"
            else:
                drift_type = "gradual"
        
        return drift_type, float(np.clip(overall_magnitude, 0, 1))
    
    def _detect_sudden_vs_gradual(self, feature_deviations: Dict[str, List[float]]) -> str:
        """Detect if drift is sudden or gradual"""
        # Calculate rate of change for each feature
        rates_of_change = []
        
        for deviations in feature_deviations.values():
            if len(deviations) < 2:
                continue
            
            # Calculate differences between consecutive windows
            diffs = np.diff(deviations)
            avg_rate = np.mean(np.abs(diffs))
            rates_of_change.append(avg_rate)
        
        if not rates_of_change:
            return "gradual"
        
        avg_rate = np.mean(rates_of_change)
        
        # If rate of change is high, it's sudden drift
        if avg_rate > 0.5:
            return "sudden"
        else:
            return "gradual"
    
    def _detect_oscillation(self, feature_deviations: Dict[str, List[float]]) -> bool:
        """Detect oscillating pattern in deviations"""
        oscillation_count = 0
        
        for deviations in feature_deviations.values():
            if len(deviations) < 4:
                continue
            
            # Count sign changes
            sign_changes = 0
            for i in range(len(deviations) - 1):
                if np.sign(deviations[i]) != np.sign(deviations[i + 1]):
                    sign_changes += 1
            
            # If more than 50% sign changes, it's oscillating
            if sign_changes > len(deviations) * 0.5:
                oscillation_count += 1
        
        # If more than 30% of features oscillate, overall pattern is oscillating
        return oscillation_count > len(feature_deviations) * 0.3
    
    def _identify_top_deviating_features(self, feature_deviations: Dict[str, List[float]], 
                                        baseline: BehavioralBaseline, top_n: int = 5) -> List[Tuple[str, float]]:
        """Identify features with highest deviation from baseline"""
        feature_scores = []
        
        for feature_name, deviations in feature_deviations.items():
            avg_deviation = np.mean(np.abs(deviations))
            feature_scores.append((feature_name, float(avg_deviation)))
        
        # Sort by deviation magnitude
        feature_scores.sort(key=lambda x: x[1], reverse=True)
        
        return feature_scores[:top_n]
    
    def _calculate_significance(self, drift_signals: Dict[str, Dict]) -> float:
        """Calculate overall statistical significance of drift"""
        if not drift_signals:
            return 0.0
        
        # Average p-value across all features
        p_values = [s['p_value'] for s in drift_signals.values()]
        avg_p_value = np.mean(p_values)
        
        # Convert to significance score (0-1, higher = more significant)
        significance = 1 - avg_p_value
        
        return float(np.clip(significance, 0, 1))
