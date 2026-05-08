"""
Analysis Pipeline - Main orchestration layer
Coordinates data ingestion, baseline establishment, and daily analysis
"""
from datetime import datetime, timedelta
from typing import List, Dict
import logging

from src.models.configuration import Configuration
from src.database.database import Database
from src.ml.behavior_analyzer import BehaviorAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AnalysisPipeline:
    """Main analysis pipeline orchestrator"""
    
    def __init__(self, config: Configuration, database: Database):
        self.config = config
        self.db = database
        self.analyzer = BehaviorAnalyzer(config, database)
    
    def ingest_activities(self, activities: List) -> Dict:
        """
        Ingest user activities into database
        
        Args:
            activities: List of UserActivity objects
        
        Returns:
            Dictionary with ingestion statistics
        """
        logger.info(f"Ingesting {len(activities)} activities...")
        
        start_time = datetime.now()
        self.db.insert_activities_batch(activities)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Ingestion complete in {duration:.2f} seconds")
        
        return {
            "activities_ingested": len(activities),
            "duration_seconds": duration,
            "rate_per_second": len(activities) / duration if duration > 0 else 0
        }
    
    def establish_baselines_for_all_users(self) -> Dict:
        """
        Establish baselines for all users in database
        
        Returns:
            Dictionary with baseline establishment statistics
        """
        user_ids = self.db.get_all_user_ids()
        logger.info(f"Establishing baselines for {len(user_ids)} users...")
        
        successful = 0
        failed = 0
        errors = []
        
        for user_id in user_ids:
            try:
                self.analyzer.establish_baseline(user_id)
                successful += 1
                logger.info(f"✓ Baseline established for {user_id}")
            except Exception as e:
                failed += 1
                error_msg = f"✗ Failed to establish baseline for {user_id}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        logger.info(f"Baseline establishment complete: {successful} successful, {failed} failed")
        
        return {
            "total_users": len(user_ids),
            "successful": successful,
            "failed": failed,
            "errors": errors
        }
    
    def analyze_user(self, user_id: str) -> Dict:
        """
        Analyze a specific user
        
        Args:
            user_id: User identifier
        
        Returns:
            Analysis results
        """
        logger.info(f"Analyzing user: {user_id}")
        
        try:
            result = self.analyzer.analyze_user(user_id)
            
            if "error" in result:
                logger.warning(f"Analysis warning for {user_id}: {result['error']}")
            else:
                risk_score = result['risk_score'].score
                logger.info(f"Analysis complete for {user_id}: Risk Score = {risk_score:.1f}")
                
                if result.get('alert'):
                    logger.warning(f"⚠️  ALERT generated for {user_id}")
            
            return result
        except Exception as e:
            logger.error(f"Analysis failed for {user_id}: {str(e)}")
            return {
                "user_id": user_id,
                "error": str(e)
            }
    
    def run_daily_analysis(self) -> List[Dict]:
        """
        Run daily analysis for all users
        
        Returns:
            List of analysis results
        """
        logger.info("=" * 60)
        logger.info("Starting daily analysis run")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        results = self.analyzer.analyze_all_users()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Calculate statistics
        total_users = len(results)
        successful = sum(1 for r in results if "error" not in r)
        failed = sum(1 for r in results if "error" in r)
        alerts_generated = sum(1 for r in results if r.get("alert"))
        
        logger.info("=" * 60)
        logger.info(f"Daily analysis complete in {duration:.2f} seconds")
        logger.info(f"Users analyzed: {successful}/{total_users}")
        logger.info(f"Alerts generated: {alerts_generated}")
        logger.info(f"Failed analyses: {failed}")
        logger.info("=" * 60)
        
        return results
