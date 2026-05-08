"""
Configuration Management for Drishti
Handles system-wide configuration parameters
"""
from dataclasses import dataclass, field, asdict
from typing import Dict


@dataclass
class Configuration:
    """System configuration for insider threat detection"""
    
    # Drift Detection Parameters
    drift_threshold: float = 0.15
    temporal_window_days: int = 30
    baseline_minimum_days: int = 3  # 3 days minimum for demo
    
    # Risk Scoring Parameters
    anomaly_weight: float = 0.35
    drift_weight: float = 0.30
    velocity_weight: float = 0.20
    context_weight: float = 0.15
    
    # Alert Thresholds
    alert_threshold: float = 70.0
    critical_threshold: float = 80.0
    
    # Resource Sensitivity Weights
    resource_sensitivity_weights: Dict[str, float] = field(default_factory=lambda: {
        "classified_documents": 1.0,
        "source_code": 0.8,
        "customer_data": 0.9,
        "financial_records": 0.85,
        "hr_records": 0.7,
        "internal_communications": 0.6,
        "public_resources": 0.3
    })
    
    # Feature Engineering
    feature_categories: Dict[str, list] = field(default_factory=lambda: {
        "temporal": ["hour_of_day", "day_of_week", "is_weekend", "is_business_hours"],
        "volume": ["daily_activity_count", "hourly_activity_rate", "resource_access_frequency"],
        "behavioral": ["unique_resources_accessed", "action_diversity", "session_duration"],
        "contextual": ["resource_sensitivity_score", "unusual_time_access", "geographic_anomaly"]
    })
    
    @classmethod
    def default(cls):
        """Create default configuration"""
        return cls()
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create configuration from dictionary"""
        return cls(**data)
