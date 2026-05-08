"""
Risk Scoring Engine
Calculates multi-factor risk scores combining anomaly, drift, velocity, and context
"""
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict

from src.models.data_models import UserActivity, BehavioralBaseline, DriftAnalysis, RiskScore
from src.models.configuration import Configuration


class RiskScorer:
    """Calculates comprehensive risk scores"""
    
    def __init__(self, config: Configuration):
        self.config = config
    
    def calculate_risk_score(self, user_id: str, anomaly_score: float, 
                            drift_analysis: DriftAnalysis, 
                            recent_activities: List[UserActivity],
                            baseline: BehavioralBaseline) -> RiskScore:
        """
        Calculate comprehensive risk score
        
        Components:
        1. Anomaly Score (35%): How unusual is current behavior
        2. Drift Score (30%): Magnitude and type of behavioral drift
        3. Velocity Score (20%): Rate of behavioral change
        4. Context Score (15%): Sensitivity of accessed resources
        
        Returns:
            RiskScore object with score 0-100 and risk level
        """
        # Component 1: Anomaly Score (0-100)
        anomaly_component = anomaly_score * 100 * self.config.anomaly_weight
        
        # Component 2: Drift Score (0-100)
        drift_component = self._calculate_drift_score(drift_analysis) * self.config.drift_weight
        
        # Component 3: Velocity Score (0-100)
        velocity_component = self._calculate_velocity_score(recent_activities, baseline) * self.config.velocity_weight
        
        # Component 4: Context Score (0-100)
        context_component = self._calculate_context_score(recent_activities) * self.config.context_weight
        
        # Combine components
        total_score = anomaly_component + drift_component + velocity_component + context_component
        
        # Normalize to 0-100
        final_score = float(np.clip(total_score, 0, 100))
        
        # Determine risk level
        risk_level = self._determine_risk_level(final_score)
        
        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(recent_activities, drift_analysis)
        
        # Track contributing factors
        contributing_factors = {
            'anomaly_score': float(anomaly_component),
            'drift_score': float(drift_component),
            'velocity_score': float(velocity_component),
            'context_score': float(context_component)
        }
        
        return RiskScore(
            user_id=user_id,
            timestamp=datetime.now(),
            score=final_score,
            risk_level=risk_level,
            confidence=confidence,
            contributing_factors=contributing_factors
        )
    
    def _calculate_drift_score(self, drift_analysis: DriftAnalysis) -> float:
        """Calculate drift contribution to risk (0-100)"""
        if not drift_analysis.is_drifting:
            return 0.0
        
        base_score = drift_analysis.drift_magnitude * 100
        
        # Apply multipliers based on drift type
        drift_multipliers = {
            'sudden': 1.5,      # Sudden drift is most concerning
            'gradual': 1.0,     # Gradual drift is moderate concern
            'oscillating': 1.2, # Oscillating is concerning (evasion attempt?)
            'none': 0.0
        }
        
        multiplier = drift_multipliers.get(drift_analysis.drift_type, 1.0)
        
        # Apply significance boost
        significance_boost = drift_analysis.statistical_significance * 20
        
        drift_score = (base_score * multiplier) + significance_boost
        
        return float(np.clip(drift_score, 0, 100))
    
    def _calculate_velocity_score(self, recent_activities: List[UserActivity], 
                                  baseline: BehavioralBaseline) -> float:
        """Calculate velocity (rate of change) contribution to risk (0-100)"""
        if not recent_activities or not baseline.activity_patterns:
            return 0.0
        
        # Calculate current activity rate
        if len(recent_activities) < 2:
            return 0.0
        
        time_span_days = (recent_activities[-1].timestamp - recent_activities[0].timestamp).days
        if time_span_days == 0:
            time_span_days = 1
        
        current_daily_rate = len(recent_activities) / time_span_days
        
        # Get baseline activity rate
        baseline_daily_rate = baseline.activity_patterns.get('avg_daily_activities', 1)
        
        # Calculate rate change ratio
        if baseline_daily_rate > 0:
            rate_change_ratio = current_daily_rate / baseline_daily_rate
        else:
            rate_change_ratio = 1.0
        
        # Score based on deviation from baseline
        # Both significant increases and decreases are concerning
        if rate_change_ratio > 1.5:
            # Sudden increase in activity
            velocity_score = min((rate_change_ratio - 1) * 50, 100)
        elif rate_change_ratio < 0.5:
            # Sudden decrease in activity (data exfiltration complete?)
            velocity_score = min((1 - rate_change_ratio) * 50, 100)
        else:
            # Normal velocity
            velocity_score = 0.0
        
        return float(velocity_score)
    
    def _calculate_context_score(self, recent_activities: List[UserActivity]) -> float:
        """Calculate contextual risk based on resource sensitivity (0-100)"""
        if not recent_activities:
            return 0.0
        
        sensitivity_scores = []
        high_sensitivity_count = 0
        unusual_time_count = 0
        
        for activity in recent_activities:
            # Get resource sensitivity
            sensitivity = self.config.resource_sensitivity_weights.get(
                activity.resource_type, 0.5
            )
            sensitivity_scores.append(sensitivity)
            
            # Count high sensitivity accesses
            if sensitivity >= 0.8:
                high_sensitivity_count += 1
            
            # Count unusual time accesses (after hours)
            hour = activity.timestamp.hour
            if hour >= 22 or hour <= 6:
                if sensitivity >= 0.7:
                    unusual_time_count += 1
        
        # Calculate components
        avg_sensitivity = np.mean(sensitivity_scores)
        high_sensitivity_ratio = high_sensitivity_count / len(recent_activities)
        unusual_time_ratio = unusual_time_count / len(recent_activities)
        
        # Combine into context score
        context_score = (
            avg_sensitivity * 40 +           # Base sensitivity
            high_sensitivity_ratio * 40 +    # High sensitivity access frequency
            unusual_time_ratio * 20          # Unusual timing
        )
        
        return float(np.clip(context_score, 0, 100))
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level from score"""
        if score >= self.config.critical_threshold:
            return "critical"
        elif score >= self.config.alert_threshold:
            return "high"
        elif score >= 30:
            return "medium"
        else:
            return "low"
    
    def _calculate_confidence(self, recent_activities: List[UserActivity], 
                             drift_analysis: DriftAnalysis) -> float:
        """Calculate confidence in risk assessment (0-1)"""
        confidence_factors = []
        
        # Factor 1: Data volume (more data = higher confidence)
        if len(recent_activities) >= 50:
            confidence_factors.append(1.0)
        elif len(recent_activities) >= 20:
            confidence_factors.append(0.8)
        elif len(recent_activities) >= 10:
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.4)
        
        # Factor 2: Statistical significance of drift
        confidence_factors.append(drift_analysis.statistical_significance)
        
        # Factor 3: Time span (longer observation = higher confidence)
        if len(recent_activities) >= 2:
            time_span_days = (recent_activities[-1].timestamp - recent_activities[0].timestamp).days
            if time_span_days >= 30:
                confidence_factors.append(1.0)
            elif time_span_days >= 14:
                confidence_factors.append(0.8)
            elif time_span_days >= 7:
                confidence_factors.append(0.6)
            else:
                confidence_factors.append(0.4)
        else:
            confidence_factors.append(0.3)
        
        # Average confidence factors
        overall_confidence = np.mean(confidence_factors)
        
        return float(np.clip(overall_confidence, 0, 1))
