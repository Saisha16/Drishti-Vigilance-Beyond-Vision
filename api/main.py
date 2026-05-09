"""
Drishti FastAPI Backend
Exposes ML pipeline via REST API for React frontend
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import json as json_module

from src.analysis_pipeline import AnalysisPipeline
from src.database.database import Database
from src.models.configuration import Configuration
from src.security.blockchain_audit import BlockchainAuditTrail
from src.security.brute_force_detector import BruteForceDetector, AuthEvent
from src.ml.bandwidth_analyzer import BandwidthAnalyzer, NetworkMetric
from src.models.data_models import Alert, AlertExplanation, RiskScore

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
    allow_origins=["*"],
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
_blockchain = None
_brute_force = None
_bandwidth = None

def get_config():
    global _config
    if _config is None:
        _config = Configuration.default()
    return _config

def get_db():
    global _db
    if _db is None:
        import os
        db_path = os.environ.get("DATABASE_PATH", "intent_drift_ai.db")
        # Ensure directory exists for persistent disks
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        _db = Database(db_path, encryption_enabled=True)
    return _db

def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = AnalysisPipeline(get_config(), get_db())
    return _pipeline

def get_blockchain():
    global _blockchain
    if _blockchain is None:
        _blockchain = BlockchainAuditTrail(db=get_db())
    return _blockchain

def get_brute_force():
    global _brute_force
    if _brute_force is None:
        _brute_force = BruteForceDetector(db=get_db())
    return _brute_force

def get_bandwidth():
    global _bandwidth
    if _bandwidth is None:
        _bandwidth = BandwidthAnalyzer(db=get_db())
    return _bandwidth

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
    note: Optional[str] = None

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
            timestamp=rs.timestamp.isoformat() + ("Z" if not rs.timestamp.isoformat().endswith("Z") else ""),
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


@app.get("/api/alerts/stream")
async def alerts_stream(db: Database = Depends(get_db)):
    """
    Server-Sent Events (SSE) endpoint for real-time alert updates.
    Streams new alerts as they are generated and sends periodic heartbeats
    with the current alert count so clients know when data has changed.
    """
    async def event_generator():
        last_seen_version = 0
        last_known_count = 0
        sent_ids = set()

        while True:
            try:
                global _alert_count_version
                # Check for new alerts in the queue
                new_alerts = []
                while _new_alert_queue:
                    try:
                        alert_data = _new_alert_queue.popleft()
                        aid = alert_data.get("alert_id", "")
                        if aid not in sent_ids:
                            new_alerts.append(alert_data)
                            sent_ids.add(aid)
                    except IndexError:
                        break

                if new_alerts:
                    for alert_data in new_alerts:
                        yield f"event: new_alert\ndata: {json_module.dumps(alert_data)}\n\n"

                # Periodic heartbeat with current total count
                current_alerts = db.fetch_alerts(status=None, limit=1)
                current_count_row = len(db.fetch_alerts(status=None, limit=10000))
                if current_count_row != last_known_count or _alert_count_version != last_seen_version:
                    last_known_count = current_count_row
                    last_seen_version = _alert_count_version
                    yield f"event: alert_count\ndata: {json_module.dumps({'count': current_count_row, 'version': _alert_count_version})}\n\n"
                else:
                    yield f"event: heartbeat\ndata: {json_module.dumps({'ts': datetime.utcnow().isoformat() + 'Z'})}\n\n"

            except Exception as e:
                yield f"event: error\ndata: {json_module.dumps({'error': str(e)})}\n\n"

            await asyncio.sleep(2)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


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
        db.update_alert_status(alert_id, request.status, request.analyst_id, request.note)
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
                "timestamp": rs.timestamp.isoformat() + ("Z" if not rs.timestamp.isoformat().endswith("Z") else ""),
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
        result = pipeline.establish_baselines_for_all_users()
        return {
            "success": True,
            "message": "Baselines established for all users",
            "statistics": {
                "total_users": result["total_users"],
                "successful": result["successful"],
                "failed": result["failed"],
                "nan_handling_stats": {
                    "users_with_nan_values": result.get("users_with_nan_values", 0),
                    "total_nan_values_imputed": result.get("total_nan_values_imputed", 0),
                    "nan_affected_features": result.get("nan_affected_features", {}),
                    "nan_handling_applied": result.get("nan_handling_applied", False)
                }
            },
            "errors": result.get("errors", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------------------
# ENDPOINT 10: Get NaN Report
# ----------------------------------------------------------------------------

@app.get("/api/baselines/nan-report")
async def get_nan_report(db: Database = Depends(get_db)):
    """Get detailed NaN handling report for all baselines"""
    user_ids = db.get_all_user_ids()
    report = []
    
    for user_id in user_ids:
        baseline = db.fetch_baseline(user_id)
        if baseline and baseline.had_nan_values:
            report.append({
                "user_id": baseline.user_id,
                "nan_features_imputed": baseline.nan_features_imputed,
                "nan_imputation_count": baseline.nan_imputation_count,
                "baseline_start": baseline.baseline_start.isoformat(),
                "baseline_end": baseline.baseline_end.isoformat()
            })
    
    return {
        "total_users_with_nan": len(report),
        "details": report
    }

# ----------------------------------------------------------------------------
# ENDPOINT 11: Get Configuration
# ----------------------------------------------------------------------------

@app.get("/api/config")
async def get_configuration(config: Configuration = Depends(get_config)):
    """Get current system configuration"""
    return config.to_dict()

# ----------------------------------------------------------------------------
# ENDPOINT 12: Update Configuration
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
# BLOCKCHAIN AUDIT ENDPOINTS
# ============================================================================

@app.get("/api/audit/verify")
async def verify_blockchain(blockchain: BlockchainAuditTrail = Depends(get_blockchain)):
    """Verify integrity of the entire blockchain audit trail"""
    is_valid, issues = blockchain.verify_chain()
    return {
        "is_valid": is_valid,
        "total_blocks": len(blockchain.chain),
        "integrity_issues": len(issues),
        "issues": issues[:20],
        "verified_at": datetime.utcnow().isoformat() + "Z",
    }

@app.get("/api/audit/chain")
async def get_audit_chain(
    count: int = 50,
    blockchain: BlockchainAuditTrail = Depends(get_blockchain)
):
    """Get recent blockchain audit blocks"""
    return {
        "blocks": blockchain.get_recent_blocks(count),
        "summary": blockchain.get_chain_summary(),
    }

@app.post("/api/audit/event")
async def add_audit_event(
    action: str,
    user_id: str,
    details: dict = {},
    blockchain: BlockchainAuditTrail = Depends(get_blockchain)
):
    """Add a new event to the blockchain audit trail"""
    block = blockchain.add_event(action, user_id, details)
    return {"success": True, "block": block.to_dict()}

# ============================================================================
# AUTH SECURITY / BRUTE FORCE ENDPOINTS
# ============================================================================

@app.get("/api/security/auth-threats")
async def get_auth_threats(db: Database = Depends(get_db)):
    """Get authentication threat data — recent events and statistics"""
    stats = db.get_auth_stats(hours=24)
    recent_events = db.fetch_auth_events(hours=6)
    
    # Group failures by IP
    ip_counts = {}
    for e in recent_events:
        if not e["success"]:
            ip = e["ip_address"]
            ip_counts[ip] = ip_counts.get(ip, 0) + 1
    
    top_attackers = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "stats": stats,
        "recent_events": recent_events[:100],
        "top_attacking_ips": [{"ip": ip, "attempts": count} for ip, count in top_attackers],
    }

@app.get("/api/security/brute-force-status")
async def get_brute_force_status(detector: BruteForceDetector = Depends(get_brute_force)):
    """Get current brute force detection engine status"""
    return detector.get_status()

# ============================================================================
# NETWORK SECURITY / BANDWIDTH ENDPOINTS
# ============================================================================

@app.get("/api/network/metrics")
async def get_network_metrics(
    minutes: int = 60,
    analyzer: BandwidthAnalyzer = Depends(get_bandwidth),
    db: Database = Depends(get_db)
):
    """Get recent network traffic metrics"""
    return {
        "metrics": db.fetch_network_metrics(minutes=minutes),
        "baseline": analyzer.get_baseline(),
    }

@app.get("/api/network/baseline")
async def get_network_baseline(analyzer: BandwidthAnalyzer = Depends(get_bandwidth)):
    """Get current network traffic baseline"""
    return analyzer.get_baseline()

# ============================================================================
# ENHANCED METRICS (unified dashboard data)
# ============================================================================

@app.get("/api/dashboard/full")
async def get_full_dashboard(
    db: Database = Depends(get_db),
    blockchain: BlockchainAuditTrail = Depends(get_blockchain),
):
    """Get all dashboard data in a single call — reduces frontend API calls"""
    # Core metrics
    user_ids = db.get_all_user_ids()
    all_alerts = db.fetch_alerts(status=None, limit=10000)
    active_alerts = [a for a in all_alerts if a["status"] == "new"]
    critical_alerts = [a for a in all_alerts if a["risk_score"] >= 80]
    
    avg_risk = (
        sum(a["risk_score"] for a in active_alerts) / len(active_alerts)
        if active_alerts else 0.0
    )
    
    # Auth stats
    auth_stats = db.get_auth_stats(hours=24)
    
    # Blockchain status
    chain_summary = blockchain.get_chain_summary()
    
    # Network baseline
    network_metrics = db.fetch_network_metrics(minutes=60)
    
    # Threat distribution from real alerts
    threat_types = {}
    for alert in all_alerts:
        try:
            explanation = alert.get("explanation", {})
            if isinstance(explanation, str):
                import json
                explanation = json.loads(explanation)
            summary = explanation.get("summary", "Unknown")
            # Extract threat category from summary
            if "exfiltration" in summary.lower() or "download" in summary.lower():
                cat = "Data Exfiltration"
            elif "access" in summary.lower() or "unauthorized" in summary.lower():
                cat = "Unauthorized Access"
            elif "drift" in summary.lower() or "behavior" in summary.lower():
                cat = "Behavioral Anomaly"
            elif "escalation" in summary.lower() or "privilege" in summary.lower():
                cat = "Privilege Escalation"
            else:
                cat = "Policy Violation"
            threat_types[cat] = threat_types.get(cat, 0) + 1
        except Exception:
            threat_types["Unknown"] = threat_types.get("Unknown", 0) + 1
    
    total_threats = sum(threat_types.values()) or 1
    threat_distribution = [
        {"name": name, "value": round(count / total_threats * 100, 1), "count": count}
        for name, count in sorted(threat_types.items(), key=lambda x: x[1], reverse=True)
    ]
    
    # Risk timeline from real risk scores
    risk_timeline = []
    for uid in user_ids[:10]:  # Top 10 users for timeline
        scores = db.fetch_risk_scores(uid, days=30)
        for s in scores:
            risk_timeline.append({
                "timestamp": s.timestamp.isoformat() + ("Z" if not s.timestamp.isoformat().endswith("Z") else ""),
                "score": s.score,
                "user_id": s.user_id,
            })
    # Sort and take last 50
    risk_timeline.sort(key=lambda x: x["timestamp"])
    risk_timeline = risk_timeline[-50:]
    
    return {
        "metrics": {
            "total_users": len(user_ids),
            "active_alerts": len(active_alerts),
            "critical_alerts": len(critical_alerts),
            "avg_risk_score": round(avg_risk, 1),
        },
        "auth_stats": auth_stats,
        "blockchain": {
            "total_blocks": chain_summary["total_blocks"],
            "is_valid": chain_summary["is_valid"],
            "integrity_issues": chain_summary["integrity_issues"],
        },
        "network_status": {
            "data_points": len(network_metrics),
            "latest": network_metrics[-1] if network_metrics else None,
        },
        "threat_distribution": threat_distribution,
        "risk_timeline": risk_timeline,
        "recent_alerts": all_alerts[:10],
    }

# ============================================================================
# LIVE DEMO SIMULATOR
# ============================================================================

import random
import asyncio
from collections import deque

# In-memory feed — last 100 demo results
_demo_feed: deque = deque(maxlen=100)
_baseline_seeded = False

# Track new alert IDs for SSE streaming
_new_alert_queue: deque = deque(maxlen=500)
_alert_count_version: int = 0

def _ensure_demo_baseline(analyzer: BandwidthAnalyzer):
    """Seed the bandwidth analyzer with 15 normal data points so z-score detection works."""
    global _baseline_seeded
    if _baseline_seeded:
        return
    try:
        # Directly populate _metrics_history to bypass DB writes in record_metric
        base_ts = datetime.utcnow() - timedelta(minutes=20)
        for i in range(15):
            m = NetworkMetric(
                timestamp=base_ts + timedelta(minutes=i),
                bytes_in=random.randint(400_000, 600_000),
                bytes_out=random.randint(150_000, 250_000),
                packets_in=random.randint(800, 1200),
                packets_out=random.randint(400, 600),
                connections=random.randint(30, 70),
                protocol_dist={"tcp": 0.82, "udp": 0.15, "icmp": 0.03},
            )
            analyzer._metrics_history.append(m)
    except Exception as e:
        print(f"[DEMO] Baseline seeding error: {e}")
    _baseline_seeded = True

class DemoSimulateRequest(BaseModel):
    scenario: str  # brute_force | password_spray | impossible_travel | ddos | exfiltration | normal_login | normal_browse | credential_stuffing
    user_id: str = "demo_user"
    ip_address: str = "203.0.113.42"
    geo_location: str = "Mumbai"
    repeat: int = 1  # number of times to fire the event (for animation support)

@app.post("/api/demo/simulate")
async def demo_simulate(
    req: DemoSimulateRequest,
    detector: BruteForceDetector = Depends(get_brute_force),
    analyzer: BandwidthAnalyzer = Depends(get_bandwidth),
    blockchain: BlockchainAuditTrail = Depends(get_blockchain),
    db: Database = Depends(get_db),
):
    """
    Fire a simulated security event through the real detection engines.
    Returns detections immediately. All events tagged source=demo.
    """
    results = []
    scenario = req.scenario
    ts = datetime.utcnow()
    # BandwidthAnalyzer uses datetime.utcnow() (local time) internally for baseline/cleanup
    now_ts = datetime.utcnow()

    # ------------------------------------------------------------------
    # NORMAL LOGIN — one successful auth event, no alert expected
    # ------------------------------------------------------------------
    if scenario == "normal_login":
        event = AuthEvent(
            timestamp=ts,
            user_id=req.user_id,
            ip_address=req.ip_address,
            success=True,
            geo_location=req.geo_location,
            device_fingerprint="demo-device-001",
            user_agent="Mozilla/5.0 (Demo)",
        )
        alerts = detector.process_event(event)
        entry = _make_feed_entry("normal_login", event.to_dict(), alerts, [], None)
        _demo_feed.appendleft(entry)
        results.append(entry)

    # ------------------------------------------------------------------
    # NORMAL BROWSE — baseline-level network metric, no anomaly expected
    # ------------------------------------------------------------------
    elif scenario == "normal_browse":
        baseline = analyzer.get_baseline()
        mean_in  = baseline.get("bytes_in",  {}).get("mean", 500_000) if isinstance(baseline.get("bytes_in"), dict) else 500_000
        mean_out = baseline.get("bytes_out", {}).get("mean", 200_000) if isinstance(baseline.get("bytes_out"), dict) else 200_000
        mean_pkt = baseline.get("packets",   {}).get("mean", 1_000)   if isinstance(baseline.get("packets"),   dict) else 1_000
        mean_con = baseline.get("connections",{}).get("mean", 50)     if isinstance(baseline.get("connections"),dict) else 50

        metric = NetworkMetric(
            timestamp=now_ts,
            bytes_in=int(mean_in  * random.uniform(0.8, 1.2)),
            bytes_out=int(mean_out * random.uniform(0.8, 1.2)),
            packets_in=int(mean_pkt * 0.6 * random.uniform(0.8, 1.2)),
            packets_out=int(mean_pkt * 0.4 * random.uniform(0.8, 1.2)),
            connections=int(mean_con * random.uniform(0.8, 1.2)),
            protocol_dist={"tcp": 0.85, "udp": 0.12, "icmp": 0.03},
        )
        anomalies = analyzer.record_metric(metric)
        entry = _make_feed_entry("normal_browse", metric.to_dict(), [], anomalies, None)
        _demo_feed.appendleft(entry)
        results.append(entry)

    # ------------------------------------------------------------------
    # BRUTE FORCE — fire req.repeat failed auth events (same IP, same user)
    # For animation: frontend calls with repeat=1 multiple times
    # ------------------------------------------------------------------
    elif scenario == "brute_force":
        for i in range(max(1, req.repeat)):
            event = AuthEvent(
                timestamp=datetime.utcnow(),
                user_id=req.user_id,
                ip_address=req.ip_address,
                success=False,
                failure_reason="invalid_password",
                geo_location=req.geo_location,
                device_fingerprint=f"demo-attacker-{i}",
                user_agent="python-requests/2.28",
            )
            alerts = detector.process_event(event)
            entry = _make_feed_entry("brute_force", event.to_dict(), alerts, [], None)
            _demo_feed.appendleft(entry)
            results.append(entry)

    # ------------------------------------------------------------------
    # PASSWORD SPRAY — one failure each against many different accounts
    # ------------------------------------------------------------------
    elif scenario == "password_spray":
        targets = [f"user_{chr(65+i)}" for i in range(max(1, req.repeat))]
        for target in targets:
            event = AuthEvent(
                timestamp=datetime.utcnow(),
                user_id=target,
                ip_address=req.ip_address,
                success=False,
                failure_reason="invalid_password",
                geo_location=req.geo_location,
                device_fingerprint="demo-spray-bot",
                user_agent="curl/7.88",
            )
            alerts = detector.process_event(event)
            entry = _make_feed_entry("password_spray", event.to_dict(), alerts, [], None)
            _demo_feed.appendleft(entry)
            results.append(entry)

    # ------------------------------------------------------------------
    # IMPOSSIBLE TRAVEL — success from Mumbai, then success from New York
    # ------------------------------------------------------------------
    elif scenario == "impossible_travel":
        # Use a unique user to avoid collisions
        travel_user = f"{req.user_id}_travel_{int(ts.timestamp())}"
        event1 = AuthEvent(
            timestamp=ts - timedelta(seconds=30),
            user_id=travel_user,
            ip_address="103.21.244.10",
            success=True,
            geo_location="Mumbai",
            device_fingerprint="demo-device-india",
        )
        # Seed the first event into the detector's memory directly
        detector._last_success_by_user[travel_user] = event1

        # Second login from far away immediately after
        event2 = AuthEvent(
            timestamp=ts,
            user_id=travel_user,
            ip_address="198.51.100.25",
            success=True,
            geo_location="New York",
            device_fingerprint="demo-device-usa",
        )
        # Call _check_impossible_travel BEFORE _index_event overwrites _last_success_by_user
        alerts_from_travel = detector._check_impossible_travel(event2)
        # Now index it for bookkeeping
        detector._index_event(event2)

        # Convert BruteForceAlert objects to the format _make_feed_entry expects
        entry = _make_feed_entry("impossible_travel", event2.to_dict(), alerts_from_travel, [], None)
        _demo_feed.appendleft(entry)
        results.append(entry)

    # ------------------------------------------------------------------
    # DDOS — massive inbound traffic spike
    # ------------------------------------------------------------------
    elif scenario == "ddos":
        _ensure_demo_baseline(analyzer)
        baseline = analyzer.get_baseline()
        mean_in  = baseline.get("bytes_in",  {}).get("mean", 500_000) if isinstance(baseline.get("bytes_in"), dict) else 500_000
        std_in   = baseline.get("bytes_in",  {}).get("std",  50_000)  if isinstance(baseline.get("bytes_in"), dict) else 50_000
        mean_pkt = baseline.get("packets",   {}).get("mean", 1_000)   if isinstance(baseline.get("packets"),   dict) else 1_000
        std_pkt  = baseline.get("packets",   {}).get("std",  100)     if isinstance(baseline.get("packets"),   dict) else 100

        spike_factor = 25
        metric = NetworkMetric(
            timestamp=now_ts,
            bytes_in=int(mean_in  + std_in  * spike_factor),
            bytes_out=200_000,
            packets_in=int(mean_pkt + std_pkt * spike_factor),
            packets_out=5_000,
            connections=8_000,
            protocol_dist={"tcp": 0.05, "udp": 0.90, "icmp": 0.05},
        )
        anomalies = analyzer.record_metric(metric)
        entry = _make_feed_entry("ddos", metric.to_dict(), [], anomalies, None)
        _demo_feed.appendleft(entry)
        results.append(entry)

    # ------------------------------------------------------------------
    # DATA EXFILTRATION — massive outbound traffic spike
    # ------------------------------------------------------------------
    elif scenario == "exfiltration":
        _ensure_demo_baseline(analyzer)
        baseline = analyzer.get_baseline()
        mean_out = baseline.get("bytes_out", {}).get("mean", 200_000) if isinstance(baseline.get("bytes_out"), dict) else 200_000
        std_out  = baseline.get("bytes_out", {}).get("std",  20_000)  if isinstance(baseline.get("bytes_out"), dict) else 20_000

        spike_factor = 20
        metric = NetworkMetric(
            timestamp=now_ts,
            bytes_in=300_000,
            bytes_out=int(mean_out + std_out * spike_factor),
            packets_in=1_000,
            packets_out=80_000,
            connections=200,
            protocol_dist={"tcp": 0.95, "udp": 0.04, "icmp": 0.01},
        )
        anomalies = analyzer.record_metric(metric)
        entry = _make_feed_entry("exfiltration", metric.to_dict(), [], anomalies, None)
        _demo_feed.appendleft(entry)
        results.append(entry)

    # ------------------------------------------------------------------
    # CREDENTIAL STUFFING — many known-breach pairs from rotating IPs
    # ------------------------------------------------------------------
    elif scenario == "credential_stuffing":
        ips = [f"10.0.{random.randint(0,255)}.{random.randint(1,254)}" for _ in range(max(1, req.repeat))]
        for i, ip in enumerate(ips):
            event = AuthEvent(
                timestamp=datetime.utcnow(),
                user_id=f"victim_{i % 5}",
                ip_address=ip,
                success=False,
                failure_reason="credential_stuffing",
                geo_location="Unknown",
                device_fingerprint=f"bot-{i}",
                user_agent="Go-http-client/1.1",
            )
            alerts = detector.process_event(event)
            entry = _make_feed_entry("credential_stuffing", event.to_dict(), alerts, [], None)
            _demo_feed.appendleft(entry)
            results.append(entry)

    else:
        raise HTTPException(status_code=400, detail=f"Unknown scenario: {scenario}")

    # Log to blockchain audit
    blockchain.add_event(
        action=f"DEMO_{scenario.upper()}",
        user_id=req.user_id,
        details={"source": "demo", "scenario": scenario, "events_fired": len(results)},
    )

    # ------------------------------------------------------------------
    # PERSIST DEMO DATA TO MAIN DATABASE so it shows on the Dashboard
    # ------------------------------------------------------------------
    _persist_demo_to_db(db, scenario, req, results)

    return {
        "scenario": scenario,
        "events_fired": len(results),
        "results": results,
    }


@app.get("/api/demo/feed")
async def get_demo_feed(limit: int = 50):
    """Get the latest demo detection events for live feed polling."""
    return {"feed": list(_demo_feed)[:limit]}


@app.get("/api/demo/incidents")
async def get_demo_incidents(db: Database = Depends(get_db)):
    """
    Get demo-generated incidents from the main database.
    Returns alerts, auth events, and network metrics triggered by demo simulations,
    presented as real-world security incidents.
    """
    # Fetch all demo-generated alerts (prefixed with DEMO-)
    all_alerts = db.fetch_alerts(status=None, limit=10000)
    demo_alerts = [a for a in all_alerts if a.get("alert_id", "").startswith("DEMO-")]

    # Fetch recent auth events (last 24 hours for demo context)
    auth_events = db.fetch_auth_events(hours=24)

    # Fetch recent network metrics
    network_metrics = db.fetch_network_metrics(minutes=1440)  # last 24h

    # Build incident summary stats
    severity_counts = {}
    scenario_counts = {}
    for alert in demo_alerts:
        sev = alert.get("severity", "medium")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        # Extract scenario from alert_id: DEMO-BRUTE_FORCE-xxxx -> brute_force
        parts = alert.get("alert_id", "").split("-")
        if len(parts) >= 2:
            scenario = parts[1].lower()
            scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1

    return {
        "incidents": demo_alerts,
        "total_incidents": len(demo_alerts),
        "severity_breakdown": severity_counts,
        "scenario_breakdown": scenario_counts,
        "auth_context": {
            "total_events": len(auth_events),
            "failed": sum(1 for e in auth_events if not e["success"]),
            "recent": auth_events[:20],
        },
        "network_context": {
            "total_metrics": len(network_metrics),
            "recent": network_metrics[-10:] if network_metrics else [],
        },
    }



@app.delete("/api/demo/feed")
async def clear_demo_feed():
    """Clear the demo feed."""
    _demo_feed.clear()
    return {"cleared": True}


def _make_feed_entry(scenario: str, event_data: dict, bf_alerts: list, net_anomalies: list, extra):
    """Build a unified feed entry from detection results."""
    detections = []
    for a in bf_alerts:
        d = a.to_dict() if hasattr(a, "to_dict") else a
        detections.append({
            "engine": "brute_force",
            "type": d.get("alert_type", "unknown"),
            "severity": d.get("severity", "medium"),
            "confidence": d.get("confidence", 0.0),
            "description": d.get("details", {}).get("description", "Security alert detected"),
        })
    for a in net_anomalies:
        d = a.to_dict() if hasattr(a, "to_dict") else a
        detections.append({
            "engine": "network",
            "type": d.get("anomaly_type", "unknown"),
            "severity": d.get("severity", "medium"),
            "confidence": d.get("confidence", 0.0),
            "description": d.get("details", {}).get("description", "Network anomaly detected"),
        })
    return {
        "id": f"demo-{datetime.utcnow().timestamp()}",
        "timestamp": datetime.utcnow().isoformat(),
        "scenario": scenario,
        "source": "demo",
        "detected": len(detections) > 0,
        "detections": detections,
        "event_data": event_data,
    }


def _persist_demo_to_db(db: Database, scenario: str, req, results: list):
    """
    Persist demo simulation data to the main database so it appears
    on the Dashboard, Alerts page, and all other views.
    """
    now = datetime.utcnow()

    # --- 1. Persist auth events (brute_force, password_spray, normal_login, impossible_travel, credential_stuffing) ---
    auth_scenarios = {"brute_force", "password_spray", "normal_login", "impossible_travel", "credential_stuffing"}
    if scenario in auth_scenarios:
        for entry in results:
            ev = entry.get("event_data", {})
            if not ev:
                continue
            try:
                event = AuthEvent(
                    timestamp=datetime.fromisoformat(ev["timestamp"].replace("Z", "+00:00")) if isinstance(ev.get("timestamp"), str) else now,
                    user_id=ev.get("user_id", req.user_id),
                    ip_address=ev.get("ip_address", req.ip_address),
                    success=ev.get("success", False),
                    failure_reason=ev.get("failure_reason"),
                    geo_location=ev.get("geo_location", req.geo_location),
                    device_fingerprint=ev.get("device_fingerprint"),
                    user_agent=ev.get("user_agent"),
                )
                db.save_auth_event(event)
            except Exception as e:
                print(f"[DEMO-DB] Failed to persist auth event: {e}")

    # --- 2. Persist network metrics (ddos, exfiltration, normal_browse) ---
    network_scenarios = {"ddos", "exfiltration", "normal_browse"}
    if scenario in network_scenarios:
        for entry in results:
            ev = entry.get("event_data", {})
            if not ev:
                continue
            try:
                metric = NetworkMetric(
                    timestamp=datetime.fromisoformat(ev["timestamp"].replace("Z", "+00:00")) if isinstance(ev.get("timestamp"), str) else now,
                    bytes_in=ev.get("bytes_in", 0),
                    bytes_out=ev.get("bytes_out", 0),
                    packets_in=ev.get("packets_in", 0),
                    packets_out=ev.get("packets_out", 0),
                    connections=ev.get("connections", 0),
                    protocol_dist=ev.get("protocol_dist", {}),
                )
                db.save_network_metric(metric)
            except Exception as e:
                print(f"[DEMO-DB] Failed to persist network metric: {e}")

    # --- 3. Create an Alert + RiskScore for every detection ---
    # Map scenarios to human-readable threat summaries
    _scenario_summaries = {
        "brute_force": "[BOT DETECTED] Brute force attack detected — repeated failed login attempts from single IP",
        "password_spray": "[BOT DETECTED] Password spray attack detected — single IP targeting multiple accounts",
        "impossible_travel": "Impossible travel anomaly — user authenticated from two distant locations",
        "ddos": "[BOT DETECTED] DDoS attack detected — massive inbound traffic spike overwhelming network",
        "exfiltration": "Data exfiltration suspected — abnormal outbound data transfer volume",
        "credential_stuffing": "[BOT DETECTED] Credential stuffing attack — automated login attempts using breached credentials",
        "normal_login": "Normal user authentication",
        "normal_browse": "Normal network browsing activity",
    }

    for entry in results:
        detections = entry.get("detections", [])
        if not detections:
            continue  # No alert needed for clean events

        # Determine severity & risk score from the detection
        max_severity = "medium"
        max_confidence = 0.5
        descriptions = []
        for det in detections:
            sev = det.get("severity", "medium")
            if sev == "critical" or (sev == "high" and max_severity not in ["critical"]):
                max_severity = sev
            elif sev == "high" and max_severity == "medium":
                max_severity = sev
            conf = det.get("confidence", 0.5)
            if conf > max_confidence:
                max_confidence = conf
            descriptions.append(det.get("description", "Security event"))

        risk_score_val = {
            "critical": random.uniform(85, 98),
            "high": random.uniform(65, 84),
            "medium": random.uniform(40, 64),
            "low": random.uniform(10, 39),
        }.get(max_severity, 50.0)

        # Build and save the Alert
        alert_id = f"DEMO-{scenario.upper()}-{uuid.uuid4().hex[:8]}"
        explanation = AlertExplanation(
            summary=_scenario_summaries.get(scenario, f"Demo {scenario} event"),
            risk_factors=[f"Demo scenario: {scenario}", f"Detections: {len(detections)}"],
            behavioral_changes=descriptions[:5],
            top_contributing_features=[(scenario, round(risk_score_val, 1))],
            recommended_actions=["Review demo event in Live Demo page", "Investigate flagged user"],
        )
        alert = Alert(
            alert_id=alert_id,
            user_id=entry.get("event_data", {}).get("user_id", req.user_id),
            timestamp=now,
            risk_score=round(risk_score_val, 1),
            severity=max_severity,
            explanation=explanation,
            status="new",
        )
        try:
            db.save_alert(alert)
            # Push to SSE queue for real-time streaming
            global _alert_count_version
            _alert_count_version += 1
            _new_alert_queue.append({
                "alert_id": alert.alert_id,
                "user_id": alert.user_id,
                "timestamp": alert.timestamp.isoformat(),
                "risk_score": alert.risk_score,
                "severity": alert.severity,
                "explanation": alert.explanation.to_dict(),
                "status": alert.status,
                "assigned_to": alert.assigned_to,
            })
        except Exception as e:
            print(f"[DEMO-DB] Failed to persist alert: {e}")

        # Build and save a RiskScore so the timeline chart updates
        risk_score_obj = RiskScore(
            user_id=entry.get("event_data", {}).get("user_id", req.user_id),
            timestamp=now,
            score=round(risk_score_val, 1),
            risk_level=_score_to_level(risk_score_val),
            confidence=round(max_confidence, 2),
            contributing_factors={scenario: round(risk_score_val, 1)},
        )
        try:
            db.save_risk_score(risk_score_obj)
        except Exception as e:
            print(f"[DEMO-DB] Failed to persist risk score: {e}")


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
# BACKGROUND TASKS
# ============================================================================

async def background_network_generator():
    """Continuously generate normal network background noise so dashboard is never empty"""
    import random
    import asyncio
    from src.ml.bandwidth_analyzer import NetworkMetric
    analyzer = get_bandwidth()
    
    # Wait a bit before starting
    await asyncio.sleep(5)
    
    while True:
        try:
            now_ts = datetime.utcnow()
            metric = NetworkMetric(
                timestamp=now_ts,
                bytes_in=random.randint(400_000, 600_000),
                bytes_out=random.randint(150_000, 250_000),
                packets_in=random.randint(800, 1200),
                packets_out=random.randint(400, 600),
                connections=random.randint(30, 70),
                protocol_dist={"tcp": 0.82, "udp": 0.15, "icmp": 0.03},
            )
            analyzer.record_metric(metric)
        except Exception as e:
            print(f"[BG TASK] Error generating network metric: {e}")
            
        # Generate a new metric every 5 seconds for a lively dashboard
        await asyncio.sleep(5)

# ============================================================================
# STARTUP EVENT
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    import asyncio
    print("[*] Drishti API v2.0 starting...")
    print("[DB] Initializing database...")
    get_db()
    print("[ML] Initializing ML pipeline...")
    get_pipeline()
    print("[BC] Initializing blockchain audit trail...")
    get_blockchain()
    print("[BF] Initializing brute force detector...")
    get_brute_force()
    print("[BW] Initializing bandwidth analyzer...")
    get_bandwidth()
    
    # Start background network generator
    asyncio.create_task(background_network_generator())
    
    print("[OK] Drishti API v2.0 ready!")
    print("[->] API docs: http://localhost:8000/docs")
