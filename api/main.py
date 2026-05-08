"""
Drishti FastAPI Backend
Exposes ML pipeline via REST API for React frontend
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from src.analysis_pipeline import AnalysisPipeline
from src.database.database import Database
from src.models.configuration import Configuration

# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Drishti API",
    description="AI-Powered Insider Threat Detection",
    version="1.0.0"
)

# CORS - Allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DEPENDENCIES (Singleton pattern)
# ============================================================================

_config = None
_db = None
_pipeline = None

def get_config():
    global _config
    if _config is None:
        _config = Configuration.default()
    return _config

def get_db():
    global _db
    if _db is None:
        _db = Database("intent_drift_ai.db", encryption_enabled=True)
    return _db

def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = AnalysisPipeline(get_config(), get_db())
    return _pipeline

# ============================================================================
# PYDANTIC MODELS (Request/Response schemas)
# ============================================================================

class MetricsResponse(BaseModel):
    total_users: int
    active_alerts: int
    critical_alerts: int
    avg_risk_score: float

class UserListItem(BaseModel):
    user_id: str
    risk_score: float
    risk_level: str
    last_analyzed: Optional[str]

class RiskScoreData(BaseModel):
    score: float
    level: str
    confidence: float

class DriftAnalysisData(BaseModel):
    is_drifting: bool
    drift_type: str
    duration_days: int
    magnitude: float
    top_features: List[tuple]

class AlertData(BaseModel):
    alert_id: str
    summary: str
    risk_factors: List[str]
    behavioral_changes: List[str]
    top_contributing_features: List[tuple]
    status: str

class UserAnalysisResponse(BaseModel):
    user_id: str
    risk_score: RiskScoreData
    drift_analysis: DriftAnalysisData
    alert: Optional[AlertData]

class TimelinePoint(BaseModel):
    timestamp: str
    score: float
    is_alert: bool = False

class AlertUpdateRequest(BaseModel):
    status: str
    analyst_id: str

class ConfigUpdateRequest(BaseModel):
    drift_threshold: Optional[float] = None
    temporal_window_days: Optional[int] = None
    baseline_minimum_days: Optional[int] = None
    resource_sensitivity_weights: Optional[dict] = None

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "Drishti API",
        "status": "operational",
        "version": "1.0.0"
    }

# ----------------------------------------------------------------------------
# ENDPOINT 1: Dashboard Metrics
# ----------------------------------------------------------------------------

@app.get("/api/metrics", response_model=MetricsResponse)
async def get_metrics(db: Database = Depends(get_db)):
    """Get dashboard metrics"""
    user_ids = db.get_all_user_ids()
    all_alerts = db.fetch_alerts(status=None, limit=10000)
    active_alerts = [a for a in all_alerts if a["status"] == "new"]
    critical_alerts = [a for a in all_alerts if a["risk_score"] >= 80]
    
    avg_risk = (
        sum(a["risk_score"] for a in active_alerts) / len(active_alerts)
        if active_alerts else 0.0
    )
    
    return MetricsResponse(
        total_users=len(user_ids),
        active_alerts=len(active_alerts),
        critical_alerts=len(critical_alerts),
        avg_risk_score=round(avg_risk, 1)
    )

# ----------------------------------------------------------------------------
# ENDPOINT 2: User List
# ----------------------------------------------------------------------------

@app.get("/api/users", response_model=List[UserListItem])
async def get_users(db: Database = Depends(get_db)):
    """Get list of all users with their latest risk scores"""
    user_ids = db.get_all_user_ids()
    alerts = db.fetch_alerts(status=None, limit=10000)
    
    # Map users to their latest alerts
    user_map = {}
    for alert in alerts:
        uid = alert["user_id"]
        if uid not in user_map or alert["timestamp"] > user_map[uid]["timestamp"]:
            user_map[uid] = alert
    
    result = []
    for uid in user_ids:
        if uid in user_map:
            alert = user_map[uid]
            result.append(UserListItem(
                user_id=uid,
                risk_score=alert["risk_score"],
                risk_level=_score_to_level(alert["risk_score"]),
                last_analyzed=alert["timestamp"]
            ))
        else:
            result.append(UserListItem(
                user_id=uid,
                risk_score=0.0,
                risk_level="low",
                last_analyzed=None
            ))
    
    # Sort by risk score descending
    result.sort(key=lambda x: x.risk_score, reverse=True)
    return result

# ----------------------------------------------------------------------------
# ENDPOINT 3: User Analysis
# ----------------------------------------------------------------------------

@app.get("/api/users/{user_id}/analysis", response_model=UserAnalysisResponse)
async def analyze_user(user_id: str, pipeline: AnalysisPipeline = Depends(get_pipeline)):
    """Perform full analysis for a user"""
    try:
        result = pipeline.analyze_user(user_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        risk_score = result["risk_score"]
        drift = result["drift_analysis"]
        alert = result.get("alert")
        
        return UserAnalysisResponse(
            user_id=user_id,
            risk_score=RiskScoreData(
                score=risk_score.score,
                level=risk_score.risk_level,
                confidence=risk_score.confidence
            ),
            drift_analysis=DriftAnalysisData(
                is_drifting=drift.is_drifting,
                drift_type=drift.drift_type,
                duration_days=drift.drift_duration_days,
                magnitude=drift.drift_magnitude,
                top_features=drift.top_deviating_features[:5]
            ),
            alert=AlertData(
                alert_id=alert.alert_id,
                summary=alert.explanation.summary,
                risk_factors=alert.explanation.risk_factors,
                behavioral_changes=alert.explanation.behavioral_changes,
                top_contributing_features=alert.explanation.top_contributing_features,
                status=alert.status
            ) if alert else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------------------
# ENDPOINT 4: Risk Timeline
# ----------------------------------------------------------------------------

@app.get("/api/users/{user_id}/timeline", response_model=List[TimelinePoint])
async def get_risk_timeline(
    user_id: str,
    days: int = 60,
    db: Database = Depends(get_db)
):
    """Get risk score timeline for a user"""
    scores = db.fetch_risk_scores(user_id, days=days)
    
    return [
        TimelinePoint(
            timestamp=rs.timestamp.isoformat(),
            score=rs.score,
            is_alert=(rs.score >= 70)
        )
        for rs in scores
    ]

# ----------------------------------------------------------------------------
# ENDPOINT 5: Alerts List
# ----------------------------------------------------------------------------

@app.get("/api/alerts")
async def get_alerts(
    status: Optional[str] = None,
    limit: int = 100,
    db: Database = Depends(get_db)
):
    """Get alerts with optional filtering"""
    alerts = db.fetch_alerts(status=status, limit=limit)
    return alerts

# ----------------------------------------------------------------------------
# ENDPOINT 6: Update Alert Status
# ----------------------------------------------------------------------------

@app.post("/api/alerts/{alert_id}/status")
async def update_alert_status(
    alert_id: str,
    request: AlertUpdateRequest,
    db: Database = Depends(get_db)
):
    """Update alert status"""
    try:
        db.update_alert_status(alert_id, request.status, request.analyst_id)
        return {
            "success": True,
            "alert_id": alert_id,
            "new_status": request.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------------------
# ENDPOINT 7: Heatmap Data
# ----------------------------------------------------------------------------

@app.get("/api/heatmap")
async def get_heatmap_data(db: Database = Depends(get_db)):
    """Get risk heatmap data for all users"""
    user_ids = db.get_all_user_ids()
    data = {}
    
    for uid in user_ids:
        scores = db.fetch_risk_scores(uid, days=30)
        data[uid] = [
            {
                "timestamp": rs.timestamp.isoformat(),
                "score": rs.score
            }
            for rs in scores
        ]
    
    return data

# ----------------------------------------------------------------------------
# ENDPOINT 8: Run Analysis
# ----------------------------------------------------------------------------

@app.post("/api/analysis/run")
async def run_analysis(pipeline: AnalysisPipeline = Depends(get_pipeline)):
    """Trigger daily analysis for all users"""
    try:
        results = pipeline.run_daily_analysis()
        alerts_generated = sum(1 for r in results if r.get("alert"))
        
        return {
            "success": True,
            "analyzed": len(results),
            "alerts_generated": alerts_generated
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------------------
# ENDPOINT 9: Establish Baselines
# ----------------------------------------------------------------------------

@app.post("/api/baselines/establish")
async def establish_baselines(pipeline: AnalysisPipeline = Depends(get_pipeline)):
    """Establish baselines for all users"""
    try:
        pipeline.establish_baselines_for_all_users()
        return {
            "success": True,
            "message": "Baselines established for all users"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------------------
# ENDPOINT 10: Get Configuration
# ----------------------------------------------------------------------------

@app.get("/api/config")
async def get_configuration(config: Configuration = Depends(get_config)):
    """Get current system configuration"""
    return config.to_dict()

# ----------------------------------------------------------------------------
# ENDPOINT 11: Update Configuration
# ----------------------------------------------------------------------------

@app.put("/api/config")
async def update_configuration(
    request: ConfigUpdateRequest,
    config: Configuration = Depends(get_config)
):
    """Update system configuration"""
    updated_fields = []
    
    if request.drift_threshold is not None:
        config.drift_threshold = request.drift_threshold
        updated_fields.append("drift_threshold")
    
    if request.temporal_window_days is not None:
        config.temporal_window_days = request.temporal_window_days
        updated_fields.append("temporal_window_days")
    
    if request.baseline_minimum_days is not None:
        config.baseline_minimum_days = request.baseline_minimum_days
        updated_fields.append("baseline_minimum_days")
    
    if request.resource_sensitivity_weights is not None:
        config.resource_sensitivity_weights.update(request.resource_sensitivity_weights)
        updated_fields.append("resource_sensitivity_weights")
    
    return {
        "success": True,
        "updated_fields": updated_fields
    }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _score_to_level(score: float) -> str:
    """Convert risk score to level"""
    if score >= 80:
        return "critical"
    elif score >= 60:
        return "high"
    elif score >= 30:
        return "medium"
    else:
        return "low"

# ============================================================================
# STARTUP EVENT
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    print("[*] Drishti API starting...")
    print("[DB] Initializing database...")
    get_db()
    print("[ML] Initializing ML pipeline...")
    get_pipeline()
    print("[OK] Drishti API ready!")
    print("[->] API docs: http://localhost:8000/docs")
