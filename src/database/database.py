"""
Database Layer with AES-256 Encryption
Handles all data persistence with security-first approach
"""
import sqlite3
import json
import base64
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os

from src.models.data_models import (
    UserActivity, BehavioralBaseline, RiskScore, 
    DriftAnalysis, Alert, AlertExplanation
)


class EncryptionManager:
    """Handles AES-256 encryption for sensitive data"""
    
    def __init__(self, password: str = None):
        if password is None:
            password = os.environ.get("DRISHTI_ENCRYPTION_KEY", "drishti-default-key-change-in-production")
        
        # Derive encryption key from password using PBKDF2
        salt = b'drishti_salt_v1'  # In production, use random salt stored securely
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        if not data:
            return data
        encrypted = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        if not encrypted_data:
            return encrypted_data
        decoded = base64.b64decode(encrypted_data.encode('utf-8'))
        decrypted = self.cipher.decrypt(decoded)
        return decrypted.decode('utf-8')


class Database:
    """SQLite database with encryption support"""
    
    def __init__(self, db_path: str = "intent_drift_ai.db", encryption_enabled: bool = True):
        self.db_path = db_path
        self.encryption_enabled = encryption_enabled
        self.encryptor = EncryptionManager() if encryption_enabled else None
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User Activities Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                resource_id TEXT,
                resource_type TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Behavioral Baselines Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS behavioral_baselines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                baseline_start TEXT NOT NULL,
                baseline_end TEXT NOT NULL,
                model_data BLOB NOT NULL,
                feature_distributions TEXT NOT NULL,
                activity_patterns TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Risk Scores Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                score REAL NOT NULL,
                risk_level TEXT NOT NULL,
                confidence REAL NOT NULL,
                contributing_factors TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Alerts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                risk_score REAL NOT NULL,
                severity TEXT NOT NULL,
                explanation TEXT NOT NULL,
                status TEXT DEFAULT 'new',
                assigned_to TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Alert Notes Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT NOT NULL,
                analyst_id TEXT NOT NULL,
                note TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (alert_id) REFERENCES alerts(alert_id)
            )
        """)
        
        # Audit Log Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                user_id TEXT,
                details TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Configuration Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuration (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_user_time ON user_activities(user_id, timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_risk_scores_user_time ON risk_scores(user_id, timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)")
        
        conn.commit()
        conn.close()
        
        self._log_audit("database_initialized", None, {"encryption_enabled": self.encryption_enabled})
    
    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def _log_audit(self, action: str, user_id: Optional[str], details: Dict):
        """Log action to audit trail"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audit_log (action, user_id, details) VALUES (?, ?, ?)",
            (action, user_id, json.dumps(details))
        )
        conn.commit()
        conn.close()
    
    # ==================== USER ACTIVITIES ====================
    
    def insert_activity(self, activity: UserActivity):
        """Insert a single user activity"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Encrypt sensitive fields (resource_id only, user_id kept as plaintext for efficient lookups)
        user_id = activity.user_id
        resource_id = self.encryptor.encrypt(activity.resource_id) if self.encryption_enabled else activity.resource_id
        metadata = json.dumps(activity.metadata)
        
        cursor.execute("""
            INSERT INTO user_activities (user_id, timestamp, action, resource_id, resource_type, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, activity.timestamp.isoformat(), activity.action, resource_id, activity.resource_type, metadata))
        
        conn.commit()
        conn.close()
    
    def insert_activities_batch(self, activities: List[UserActivity]):
        """Batch insert activities for performance"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        data = []
        for activity in activities:
            user_id = activity.user_id
            resource_id = self.encryptor.encrypt(activity.resource_id) if self.encryption_enabled else activity.resource_id
            metadata = json.dumps(activity.metadata)
            data.append((user_id, activity.timestamp.isoformat(), activity.action, resource_id, activity.resource_type, metadata))
        
        cursor.executemany("""
            INSERT INTO user_activities (user_id, timestamp, action, resource_id, resource_type, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, data)
        
        conn.commit()
        conn.close()
        
        self._log_audit("activities_inserted", None, {"count": len(activities)})
    
    def fetch_user_activities(self, user_id: str, start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None, limit: int = 10000) -> List[UserActivity]:
        """Fetch activities for a user within date range"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # user_id is stored as plaintext for efficient lookups
        query = "SELECT user_id, timestamp, action, resource_id, resource_type, metadata FROM user_activities WHERE user_id = ?"
        params = [user_id]
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        activities = []
        for row in rows:
            decrypted_resource_id = self.encryptor.decrypt(row[3]) if self.encryption_enabled else row[3]
            
            activities.append(UserActivity(
                user_id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                action=row[2],
                resource_id=decrypted_resource_id,
                resource_type=row[4],
                metadata=json.loads(row[5]) if row[5] else {}
            ))
        
        return activities
    
    def get_all_user_ids(self) -> List[str]:
        """Get list of all unique user IDs"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT user_id FROM user_activities")
        rows = cursor.fetchall()
        conn.close()
        
        # user_id is stored as plaintext, no decryption needed
        user_ids = [row[0] for row in rows]
        return user_ids
    
    # ==================== BEHAVIORAL BASELINES ====================
    
    def save_baseline(self, baseline: BehavioralBaseline):
        """Save or update behavioral baseline"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # user_id stored as plaintext for efficient lookups
        cursor.execute("""
            INSERT OR REPLACE INTO behavioral_baselines 
            (user_id, baseline_start, baseline_end, model_data, feature_distributions, activity_patterns, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            baseline.user_id,
            baseline.baseline_start.isoformat(),
            baseline.baseline_end.isoformat(),
            baseline.model_data,
            json.dumps(baseline.feature_distributions),
            json.dumps(baseline.activity_patterns),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        self._log_audit("baseline_saved", baseline.user_id, {"baseline_days": (baseline.baseline_end - baseline.baseline_start).days})
    
    def fetch_baseline(self, user_id: str) -> Optional[BehavioralBaseline]:
        """Fetch baseline for a user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # user_id stored as plaintext
        cursor.execute("""
            SELECT user_id, baseline_start, baseline_end, model_data, feature_distributions, activity_patterns, created_at
            FROM behavioral_baselines WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return BehavioralBaseline(
            user_id=row[0],
            baseline_start=datetime.fromisoformat(row[1]),
            baseline_end=datetime.fromisoformat(row[2]),
            model_data=row[3],
            feature_distributions=json.loads(row[4]),
            activity_patterns=json.loads(row[5]),
            created_at=datetime.fromisoformat(row[6])
        )
    
    # ==================== RISK SCORES ====================
    
    def save_risk_score(self, risk_score: RiskScore):
        """Save risk score"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # user_id stored as plaintext
        cursor.execute("""
            INSERT INTO risk_scores (user_id, timestamp, score, risk_level, confidence, contributing_factors)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            risk_score.user_id,
            risk_score.timestamp.isoformat(),
            risk_score.score,
            risk_score.risk_level,
            risk_score.confidence,
            json.dumps(risk_score.contributing_factors)
        ))
        
        conn.commit()
        conn.close()
    
    def fetch_risk_scores(self, user_id: str, days: int = 60) -> List[RiskScore]:
        """Fetch recent risk scores for a user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # user_id stored as plaintext
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT user_id, timestamp, score, risk_level, confidence, contributing_factors
            FROM risk_scores WHERE user_id = ? AND timestamp >= ?
            ORDER BY timestamp DESC
        """, (user_id, start_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        scores = []
        for row in rows:
            scores.append(RiskScore(
                user_id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                score=row[2],
                risk_level=row[3],
                confidence=row[4],
                contributing_factors=json.loads(row[5]) if row[5] else {}
            ))
        
        return scores
    
    # ==================== ALERTS ====================
    
    def save_alert(self, alert: Alert):
        """Save security alert"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # user_id stored as plaintext
        cursor.execute("""
            INSERT INTO alerts (alert_id, user_id, timestamp, risk_score, severity, explanation, status, assigned_to)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert.alert_id,
            alert.user_id,
            alert.timestamp.isoformat(),
            alert.risk_score,
            alert.severity,
            json.dumps(alert.explanation.to_dict()),
            alert.status,
            alert.assigned_to
        ))
        
        conn.commit()
        conn.close()
        
        self._log_audit("alert_created", alert.user_id, {"alert_id": alert.alert_id, "severity": alert.severity})
    
    def fetch_alerts(self, status: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Fetch alerts with optional status filter"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT alert_id, user_id, timestamp, risk_score, severity, explanation, status, assigned_to
                FROM alerts WHERE status = ? ORDER BY timestamp DESC LIMIT ?
            """, (status, limit))
        else:
            cursor.execute("""
                SELECT alert_id, user_id, timestamp, risk_score, severity, explanation, status, assigned_to
                FROM alerts ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        alerts = []
        for row in rows:
            # user_id stored as plaintext
            alerts.append({
                "alert_id": row[0],
                "user_id": row[1],
                "timestamp": row[2],
                "risk_score": row[3],
                "severity": row[4],
                "explanation": json.loads(row[5]),
                "status": row[6],
                "assigned_to": row[7]
            })
        
        return alerts
    
    def update_alert_status(self, alert_id: str, status: str, analyst_id: str, note: Optional[str] = None):
        """Update alert status"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE alerts SET status = ?, assigned_to = ?, updated_at = ?
            WHERE alert_id = ?
        """, (status, analyst_id, datetime.now().isoformat(), alert_id))
        
        if note:
            cursor.execute("""
                INSERT INTO alert_notes (alert_id, analyst_id, note)
                VALUES (?, ?, ?)
            """, (alert_id, analyst_id, note))
        
        conn.commit()
        conn.close()
        
        self._log_audit("alert_updated", None, {"alert_id": alert_id, "new_status": status, "analyst": analyst_id})
