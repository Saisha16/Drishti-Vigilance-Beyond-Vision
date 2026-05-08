"""
Alert Generation Engine with Explainable AI
Generates human-readable alerts with detailed explanations
"""
import uuid
from datetime import datetime
from typing import List, Optional

from src.models.data_models import (
    UserActivity, RiskScore, DriftAnalysis, 
    Alert, AlertExplanation
)
from src.models.configuration import Configuration


class AlertGenerator:
    """Generates explainable security alerts"""
    
    def __init__(self, config: Configuration):
        self.config = config
    
    def generate_alert(self, user_id: str, risk_score: RiskScore, 
                      drift_analysis: DriftAnalysis,
                      recent_activities: List[UserActivity]) -> Optional[Alert]:
        """
        Generate alert if risk score exceeds threshold
        
        Returns:
            Alert object with explainable AI output, or None if below threshold
        """
        if risk_score.score < self.config.alert_threshold:
            return None
        
        # Generate unique alert ID
        alert_id = f"ALERT-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        
        # Generate explanation
        explanation = self._generate_explanation(
            user_id, risk_score, drift_analysis, recent_activities
        )
        
        # Determine severity
        severity = risk_score.risk_level
        
        return Alert(
            alert_id=alert_id,
            user_id=user_id,
            timestamp=datetime.now(),
            risk_score=risk_score.score,
            severity=severity,
            explanation=explanation,
            status="new"
        )
    
    def _generate_explanation(self, user_id: str, risk_score: RiskScore, 
                             drift_analysis: DriftAnalysis,
                             recent_activities: List[UserActivity]) -> AlertExplanation:
        """Generate human-readable explanation for alert"""
        
        # Generate summary
        summary = self._generate_summary(user_id, risk_score, drift_analysis)
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(risk_score, drift_analysis, recent_activities)
        
        # Describe behavioral changes
        behavioral_changes = self._describe_behavioral_changes(drift_analysis, recent_activities)
        
        # Get top contributing features
        top_features = drift_analysis.top_deviating_features[:5]
        
        # Generate recommended actions
        recommended_actions = self._generate_recommendations(risk_score, drift_analysis)
        
        return AlertExplanation(
            summary=summary,
            risk_factors=risk_factors,
            behavioral_changes=behavioral_changes,
            top_contributing_features=top_features,
            recommended_actions=recommended_actions
        )
    
    def _generate_summary(self, user_id: str, risk_score: RiskScore, 
                         drift_analysis: DriftAnalysis) -> str:
        """Generate one-sentence summary"""
        severity_descriptions = {
            'critical': 'CRITICAL insider threat detected',
            'high': 'High-risk anomalous behavior detected',
            'medium': 'Moderate risk behavioral anomaly detected',
            'low': 'Low-risk behavioral deviation detected'
        }
        
        base_summary = severity_descriptions.get(risk_score.risk_level, 'Anomalous behavior detected')
        
        if drift_analysis.is_drifting:
            drift_desc = f" with {drift_analysis.drift_type} behavioral drift"
        else:
            drift_desc = ""
        
        return f"{base_summary} for user {user_id}{drift_desc}. Risk score: {risk_score.score:.1f}/100."
    
    def _identify_risk_factors(self, risk_score: RiskScore, drift_analysis: DriftAnalysis,
                               recent_activities: List[UserActivity]) -> List[str]:
        """Identify specific risk factors"""
        factors = []
        
        # Anomaly factor
        anomaly_contribution = risk_score.contributing_factors.get('anomaly_score', 0)
        if anomaly_contribution > 20:
            factors.append(f"Behavior significantly deviates from established baseline (anomaly score: {anomaly_contribution:.1f})")
        
        # Drift factor
        if drift_analysis.is_drifting:
            drift_contribution = risk_score.contributing_factors.get('drift_score', 0)
            factors.append(
                f"{drift_analysis.drift_type.capitalize()} behavioral drift detected "
                f"over {drift_analysis.drift_duration_days} days (drift score: {drift_contribution:.1f})"
            )
        
        # Velocity factor
        velocity_contribution = risk_score.contributing_factors.get('velocity_score', 0)
        if velocity_contribution > 15:
            factors.append(f"Unusual activity rate change detected (velocity score: {velocity_contribution:.1f})")
        
        # Context factor
        context_contribution = risk_score.contributing_factors.get('context_score', 0)
        if context_contribution > 15:
            # Analyze what drove context score
            sensitive_count = sum(
                1 for a in recent_activities 
                if self.config.resource_sensitivity_weights.get(a.resource_type, 0) >= 0.8
            )
            
            if sensitive_count > 0:
                factors.append(
                    f"Accessed {sensitive_count} highly sensitive resources "
                    f"(context score: {context_contribution:.1f})"
                )
            
            # Check for after-hours access
            after_hours_count = sum(
                1 for a in recent_activities 
                if a.timestamp.hour >= 22 or a.timestamp.hour <= 6
            )
            
            if after_hours_count > len(recent_activities) * 0.3:
                factors.append(f"Significant after-hours activity ({after_hours_count} events)")
        
        return factors
    
    def _describe_behavioral_changes(self, drift_analysis: DriftAnalysis,
                                    recent_activities: List[UserActivity]) -> List[str]:
        """Describe specific behavioral changes"""
        changes = []
        
        if not drift_analysis.is_drifting:
            return ["No significant behavioral drift detected"]
        
        # Describe top deviating features
        for feature_name, deviation in drift_analysis.top_deviating_features[:3]:
            change_desc = self._feature_to_human_readable(feature_name, deviation)
            if change_desc:
                changes.append(change_desc)
        
        # Analyze action patterns
        action_counts = {}
        for activity in recent_activities:
            action_counts[activity.action] = action_counts.get(activity.action, 0) + 1
        
        total = len(recent_activities)
        
        # Check for unusual action distributions
        if action_counts.get('download', 0) / total > 0.3:
            changes.append(f"High frequency of download actions ({action_counts['download']} downloads)")
        
        if action_counts.get('delete', 0) / total > 0.2:
            changes.append(f"Elevated delete activity ({action_counts['delete']} deletions)")
        
        if action_counts.get('share', 0) / total > 0.15:
            changes.append(f"Increased sharing behavior ({action_counts['share']} shares)")
        
        return changes if changes else ["Behavioral pattern deviation detected"]
    
    def _feature_to_human_readable(self, feature_name: str, deviation: float) -> Optional[str]:
        """Convert feature name and deviation to human-readable description"""
        descriptions = {
            'after_hours_ratio': f"After-hours activity increased significantly (deviation: {deviation:.2f}σ)",
            'weekend_activity_ratio': f"Weekend activity pattern changed (deviation: {deviation:.2f}σ)",
            'unique_resources_accessed': f"Number of unique resources accessed changed (deviation: {deviation:.2f}σ)",
            'download_action_ratio': f"Download frequency changed significantly (deviation: {deviation:.2f}σ)",
            'delete_action_ratio': f"Delete activity pattern changed (deviation: {deviation:.2f}σ)",
            'share_action_ratio': f"Sharing behavior changed (deviation: {deviation:.2f}σ)",
            'avg_resource_sensitivity': f"Average sensitivity of accessed resources changed (deviation: {deviation:.2f}σ)",
            'unusual_time_sensitive_access': f"Unusual-time access to sensitive resources increased (deviation: {deviation:.2f}σ)",
            'activity_burst_score': f"Activity burst pattern changed (deviation: {deviation:.2f}σ)",
            'hourly_activity_rate': f"Activity rate changed significantly (deviation: {deviation:.2f}σ)"
        }
        
        return descriptions.get(feature_name)
    
    def _generate_recommendations(self, risk_score: RiskScore, 
                                 drift_analysis: DriftAnalysis) -> List[str]:
        """Generate recommended actions for analysts"""
        recommendations = []
        
        if risk_score.risk_level == 'critical':
            recommendations.append("IMMEDIATE ACTION REQUIRED: Review user access logs and consider temporary access suspension")
            recommendations.append("Initiate incident response protocol")
            recommendations.append("Contact user's manager and security team")
        elif risk_score.risk_level == 'high':
            recommendations.append("Prioritize investigation within 24 hours")
            recommendations.append("Review recent resource access patterns")
            recommendations.append("Interview user if patterns cannot be explained")
        else:
            recommendations.append("Monitor user activity for next 7 days")
            recommendations.append("Review if risk score continues to increase")
        
        # Drift-specific recommendations
        if drift_analysis.is_drifting:
            if drift_analysis.drift_type == 'sudden':
                recommendations.append("Investigate trigger event for sudden behavioral change")
            elif drift_analysis.drift_type == 'oscillating':
                recommendations.append("Possible evasion attempt - review for pattern manipulation")
        
        # Context-specific recommendations
        context_score = risk_score.contributing_factors.get('context_score', 0)
        if context_score > 20:
            recommendations.append("Audit access to sensitive resources")
            recommendations.append("Verify business justification for sensitive data access")
        
        return recommendations
