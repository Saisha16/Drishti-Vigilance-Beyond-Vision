"""
Behavior Analyzer - Orchestrates all ML components
Main entry point for behavioral analysis
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from src.models.data_models import UserActivity, BehavioralBaseline, RiskScore, DriftAnalysis, Alert
from src.models.configuration import Configuration
from src.database.database import Database
from src.ml.feature_extractor import FeatureExtractor
from src.ml.baseline_modeler import BaselineModeler
from src.ml.drift_detector import DriftDetector
from src.ml.risk_scorer import RiskScorer
from src.ml.alert_generator import AlertGenerator


class BehaviorAnalyzer:
    """Orchestrates behavioral analysis pipeline"""
    
    def __init__(self, config: Configuration, database: Database):
        self.config = config
        self.db = database
        
        # Initialize ML components
        self.feature_extractor = FeatureExtractor(config)
        self.baseline_modeler = BaselineModeler(config)
        self.drift_detector = DriftDetector(config)
        self.risk_scorer = RiskScorer(config)
        self.alert_generator = AlertGenerator(config)
    
    def establish_baseline(self, user_id: str) -> BehavioralBaseline:
        """
        Establish behavioral baseline for a user
        
        Args:
            user_id: User identifier
        
        Returns:
            BehavioralBaseline object
        """
        # Fetch historical activities (fetch 60 days to ensure we have enough baseline data)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)
        
        activities = self.db.fetch_user_activities(user_id, start_date, end_date)
        
        if not activities:
            raise ValueError(f"No activities found for user {user_id}")
        
        # Establish baseline
        baseline = self.baseline_modeler.establish_baseline(user_id, activities)
        
        # Save to database
        self.db.save_baseline(baseline)
        
        return baseline
    
    def analyze_user(self, user_id: str, analysis_window_days: int = None) -> Dict:
        """
        Perform complete behavioral analysis for a user
        
        Args:
            user_id: User identifier
            analysis_window_days: Days of recent activity to analyze (default: config value)
        
        Returns:
            Dictionary with analysis results including risk score, drift analysis, and alert
        """
        if analysis_window_days is None:
            analysis_window_days = self.config.temporal_window_days
        
        # Fetch baseline
        baseline = self.db.fetch_baseline(user_id)
        if not baseline:
            return {
                "error": f"No baseline found for user {user_id}. Please establish baseline first."
            }
        
        # Fetch recent activities
        end_date = datetime.now()
        start_date = end_date - timedelta(days=analysis_window_days)
        recent_activities = self.db.fetch_user_activities(user_id, start_date, end_date)
        
        if not recent_activities:
            return {
                "error": f"No recent activities found for user {user_id}"
            }
        
        # Step 1: Calculate anomaly score
        anomaly_score = self.baseline_modeler.predict_anomaly_score(baseline, recent_activities)
        
        # Step 2: Detect behavioral drift
        drift_analysis = self.drift_detector.detect_drift(user_id, baseline, recent_activities)
        
        # Step 3: Calculate risk score
        risk_score = self.risk_scorer.calculate_risk_score(
            user_id, anomaly_score, drift_analysis, recent_activities, baseline
        )
        
        # Save risk score
        self.db.save_risk_score(risk_score)
        
        # Step 4: Generate alert if necessary
        alert = self.alert_generator.generate_alert(
            user_id, risk_score, drift_analysis, recent_activities
        )
        
        if alert:
            self.db.save_alert(alert)
        
        return {
            "user_id": user_id,
            "anomaly_score": anomaly_score,
            "risk_score": risk_score,
            "drift_analysis": drift_analysis,
            "alert": alert,
            "analyzed_activities": len(recent_activities),
            "analysis_period_days": analysis_window_days
        }
    
    def analyze_all_users(self) -> List[Dict]:
        """
        Analyze all users with established baselines
        
        Returns:
            List of analysis results for each user
        """
        user_ids = self.db.get_all_user_ids()
        results = []
        
        for user_id in user_ids:
            try:
                result = self.analyze_user(user_id)
                results.append(result)
            except Exception as e:
                results.append({
                    "user_id": user_id,
                    "error": str(e)
                })
        
        return results
