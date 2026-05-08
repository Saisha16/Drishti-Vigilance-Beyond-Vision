"""
Core Data Models for Drishti
Defines the structure of activities, baselines, risk scores, and alerts
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import pickle
import base64


@dataclass
class UserActivity:
    """Represents a single user activity event"""
    user_id: str
    timestamp: datetime
    action: str
    resource_id: str
    resource_type: str
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "metadata": self.metadata
        }


@dataclass
class BehavioralBaseline:
    """Stores learned behavioral baseline for a user"""
    user_id: str
    baseline_start: datetime
    baseline_end: datetime
    model_data: bytes  # Serialized sklearn model
    feature_distributions: Dict[str, Dict]  # mean, std, min, max for each feature
    activity_patterns: Dict[str, float]  # Typical patterns
    created_at: datetime = field(default_factory=datetime.now)
    
    def serialize_model(self, model) -> bytes:
        """Serialize sklearn model to bytes"""
        return pickle.dumps(model)
    
    def deserialize_model(self):
        """Deserialize sklearn model from bytes"""
        return pickle.loads(self.model_data)
    
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "baseline_start": self.baseline_start.isoformat(),
            "baseline_end": self.baseline_end.isoformat(),
            "model_data": base64.b64encode(self.model_data).decode('utf-8'),
            "feature_distributions": self.feature_distributions,
            "activity_patterns": self.activity_patterns,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class RiskScore:
    """Risk score for a user at a specific time"""
    user_id: str
    timestamp: datetime
    score: float  # 0-100
    risk_level: str  # low, medium, high, critical
    confidence: float  # 0-1
    contributing_factors: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "score": self.score,
            "risk_level": self.risk_level,
            "confidence": self.confidence,
            "contributing_factors": self.contributing_factors
        }


@dataclass
class DriftAnalysis:
    """Results of behavioral drift detection"""
    user_id: str
    is_drifting: bool
    drift_type: str  # "none", "gradual", "sudden", "oscillating"
    drift_magnitude: float  # 0-1
    drift_duration_days: int
    top_deviating_features: List[Tuple[str, float]] = field(default_factory=list)
    statistical_significance: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "is_drifting": self.is_drifting,
            "drift_type": self.drift_type,
            "drift_magnitude": self.drift_magnitude,
            "drift_duration_days": self.drift_duration_days,
            "top_deviating_features": self.top_deviating_features,
            "statistical_significance": self.statistical_significance
        }


@dataclass
class AlertExplanation:
    """Explainable AI output for an alert"""
    summary: str
    risk_factors: List[str]
    behavioral_changes: List[str]
    top_contributing_features: List[Tuple[str, float]]
    recommended_actions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "summary": self.summary,
            "risk_factors": self.risk_factors,
            "behavioral_changes": self.behavioral_changes,
            "top_contributing_features": self.top_contributing_features,
            "recommended_actions": self.recommended_actions
        }


@dataclass
class Alert:
    """Security alert for suspicious behavior"""
    alert_id: str
    user_id: str
    timestamp: datetime
    risk_score: float
    severity: str  # low, medium, high, critical
    explanation: AlertExplanation
    status: str = "new"  # new, acknowledged, investigating, resolved, false_positive
    assigned_to: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "alert_id": self.alert_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "risk_score": self.risk_score,
            "severity": self.severity,
            "explanation": self.explanation.to_dict(),
            "status": self.status,
            "assigned_to": self.assigned_to
        }
