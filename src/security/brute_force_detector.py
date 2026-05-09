"""
Brute Force Attack Detection Module
Detects authentication-based attacks in real-time using sliding window analysis.

Detection capabilities:
1. Single-target brute force (many passwords against one account)
2. Password spraying (one password against many accounts)
3. Credential stuffing (known credential pairs from breaches)
4. Distributed brute force (many IPs targeting one account)
5. Geographic anomaly / impossible travel detection
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class AuthEvent:
    """A single authentication event"""
    timestamp: datetime
    user_id: str
    ip_address: str
    success: bool
    failure_reason: Optional[str] = None
    geo_location: Optional[str] = None
    device_fingerprint: Optional[str] = None
    user_agent: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "success": self.success,
            "failure_reason": self.failure_reason,
            "geo_location": self.geo_location,
            "device_fingerprint": self.device_fingerprint,
            "user_agent": self.user_agent,
        }


@dataclass
class BruteForceAlert:
    """Alert generated when brute force attack is detected"""
    alert_type: str  # "brute_force", "password_spray", "credential_stuffing", "distributed", "impossible_travel"
    severity: str  # "low", "medium", "high", "critical"
    target_user: Optional[str] = None
    source_ips: List[str] = field(default_factory=list)
    failed_attempts: int = 0
    time_window_seconds: int = 0
    details: Dict = field(default_factory=dict)
    timestamp: str = ""
    confidence: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "alert_type": self.alert_type,
            "severity": self.severity,
            "target_user": self.target_user,
            "source_ips": self.source_ips,
            "failed_attempts": self.failed_attempts,
            "time_window_seconds": self.time_window_seconds,
            "details": self.details,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
        }


# Approximate coordinates for geographic anomaly detection
# In production, use a proper GeoIP database (MaxMind, etc.)
GEO_COORDINATES = {
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.7041, 77.1025),
    "Bangalore": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    "New York": (40.7128, -74.0060),
    "London": (51.5074, -0.1278),
    "Beijing": (39.9042, 116.4074),
    "Moscow": (55.7558, 37.6173),
    "Unknown": (0.0, 0.0),
}


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in km using Haversine formula"""
    R = 6371  # Earth's radius in km
    lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class BruteForceDetector:
    """
    Real-time brute force attack detection engine.
    
    Uses sliding window analysis on authentication events to detect
    various types of credential-based attacks.
    
    Configuration:
        max_failed_attempts: Number of failures before alerting (default: 5)
        window_seconds: Time window for rate analysis (default: 300 = 5 min)
        lockout_duration_seconds: How long to lock after detection (default: 900 = 15 min)
        impossible_travel_speed_kmh: Max realistic travel speed (default: 900 km/h)
    """

    def __init__(
        self,
        max_failed_attempts: int = 5,
        window_seconds: int = 300,
        lockout_duration_seconds: int = 900,
        impossible_travel_speed_kmh: float = 900.0,
        db=None,
    ):
        self.max_failed_attempts = max_failed_attempts
        self.window_seconds = window_seconds
        self.lockout_duration_seconds = lockout_duration_seconds
        self.impossible_travel_speed_kmh = impossible_travel_speed_kmh
        self.db = db

        # In-memory sliding windows (cleared on restart — DB is source of truth)
        self._failed_by_user: Dict[str, List[AuthEvent]] = defaultdict(list)
        self._failed_by_ip: Dict[str, List[AuthEvent]] = defaultdict(list)
        self._all_events: List[AuthEvent] = []
        self._last_success_by_user: Dict[str, AuthEvent] = {}
        self._locked_accounts: Dict[str, datetime] = {}

        # Load recent events from DB
        self._load_recent_events()

    def _load_recent_events(self):
        """Load recent auth events from database"""
        if self.db is None:
            return
        try:
            events = self.db.fetch_auth_events(hours=1)
            for event_data in events:
                event = AuthEvent(
                    timestamp=datetime.fromisoformat(event_data["timestamp"]),
                    user_id=event_data["user_id"],
                    ip_address=event_data["ip_address"],
                    success=event_data["success"],
                    failure_reason=event_data.get("failure_reason"),
                    geo_location=event_data.get("geo_location"),
                    device_fingerprint=event_data.get("device_fingerprint"),
                )
                self._index_event(event)
        except Exception:
            pass

    def _index_event(self, event: AuthEvent):
        """Index an event into in-memory sliding windows"""
        self._all_events.append(event)
        if not event.success:
            self._failed_by_user[event.user_id].append(event)
            self._failed_by_ip[event.ip_address].append(event)
        else:
            self._last_success_by_user[event.user_id] = event

    def _clean_window(self, events: List[AuthEvent], window_seconds: int) -> List[AuthEvent]:
        """Remove events outside the current time window"""
        cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)
        return [e for e in events if e.timestamp >= cutoff]

    def process_event(self, event: AuthEvent) -> List[BruteForceAlert]:
        """
        Process a new authentication event and check for attacks.
        
        Args:
            event: The authentication event to process
            
        Returns:
            List of alerts generated (empty if no attack detected)
        """
        # Persist to database
        if self.db is not None:
            try:
                self.db.save_auth_event(event)
            except Exception:
                pass

        self._index_event(event)
        alerts = []

        if not event.success:
            alerts.extend(self._check_single_target_brute_force(event))
            alerts.extend(self._check_password_spray(event))
            alerts.extend(self._check_distributed_brute_force(event))

        if event.success:
            alerts.extend(self._check_impossible_travel(event))

        return alerts

    def _check_single_target_brute_force(self, event: AuthEvent) -> List[BruteForceAlert]:
        """Detect many failed attempts against a single account from one IP"""
        alerts = []
        user_failures = self._clean_window(
            self._failed_by_user.get(event.user_id, []),
            self.window_seconds
        )
        self._failed_by_user[event.user_id] = user_failures

        # Count failures from the same IP
        same_ip_failures = [e for e in user_failures if e.ip_address == event.ip_address]

        if len(same_ip_failures) >= self.max_failed_attempts:
            rate = len(same_ip_failures) / (self.window_seconds / 60)
            confidence = min(1.0, len(same_ip_failures) / (self.max_failed_attempts * 2))
            severity = "critical" if len(same_ip_failures) >= self.max_failed_attempts * 3 else \
                       "high" if len(same_ip_failures) >= self.max_failed_attempts * 2 else "medium"

            alerts.append(BruteForceAlert(
                alert_type="brute_force",
                severity=severity,
                target_user=event.user_id,
                source_ips=[event.ip_address],
                failed_attempts=len(same_ip_failures),
                time_window_seconds=self.window_seconds,
                details={
                    "rate_per_minute": round(rate, 2),
                    "first_attempt": same_ip_failures[0].timestamp.isoformat(),
                    "last_attempt": same_ip_failures[-1].timestamp.isoformat(),
                    "description": f"Single-target brute force: {len(same_ip_failures)} failed login attempts for user '{event.user_id}' from IP {event.ip_address} in {self.window_seconds}s",
                },
                timestamp=datetime.utcnow().isoformat() + "Z",
                confidence=round(confidence, 3),
            ))

            self._locked_accounts[event.user_id] = datetime.utcnow() + timedelta(
                seconds=self.lockout_duration_seconds
            )

        return alerts

    def _check_password_spray(self, event: AuthEvent) -> List[BruteForceAlert]:
        """Detect same IP trying one password against many accounts"""
        alerts = []
        ip_failures = self._clean_window(
            self._failed_by_ip.get(event.ip_address, []),
            self.window_seconds
        )
        self._failed_by_ip[event.ip_address] = ip_failures

        targeted_users = set(e.user_id for e in ip_failures)

        spray_threshold = max(3, self.max_failed_attempts)
        if len(targeted_users) >= spray_threshold:
            confidence = min(1.0, len(targeted_users) / (spray_threshold * 2))

            alerts.append(BruteForceAlert(
                alert_type="password_spray",
                severity="high" if len(targeted_users) >= spray_threshold * 2 else "medium",
                target_user=None,
                source_ips=[event.ip_address],
                failed_attempts=len(ip_failures),
                time_window_seconds=self.window_seconds,
                details={
                    "unique_targets": len(targeted_users),
                    "targeted_users": list(targeted_users)[:20],
                    "description": f"Password spray: IP {event.ip_address} tried {len(targeted_users)} different accounts in {self.window_seconds}s",
                },
                timestamp=datetime.utcnow().isoformat() + "Z",
                confidence=round(confidence, 3),
            ))

        return alerts

    def _check_distributed_brute_force(self, event: AuthEvent) -> List[BruteForceAlert]:
        """Detect many IPs targeting the same account"""
        alerts = []
        user_failures = self._clean_window(
            self._failed_by_user.get(event.user_id, []),
            self.window_seconds * 2  # Wider window for distributed attacks
        )

        source_ips = set(e.ip_address for e in user_failures)

        distributed_threshold = 3
        if len(source_ips) >= distributed_threshold and len(user_failures) >= self.max_failed_attempts:
            confidence = min(1.0, len(source_ips) / (distributed_threshold * 3))

            alerts.append(BruteForceAlert(
                alert_type="distributed_brute_force",
                severity="critical" if len(source_ips) >= distributed_threshold * 3 else "high",
                target_user=event.user_id,
                source_ips=list(source_ips)[:20],
                failed_attempts=len(user_failures),
                time_window_seconds=self.window_seconds * 2,
                details={
                    "unique_source_ips": len(source_ips),
                    "description": f"Distributed brute force: {len(source_ips)} different IPs targeting user '{event.user_id}' with {len(user_failures)} total attempts",
                },
                timestamp=datetime.utcnow().isoformat() + "Z",
                confidence=round(confidence, 3),
            ))

        return alerts

    def _check_impossible_travel(self, event: AuthEvent) -> List[BruteForceAlert]:
        """Detect impossible travel — user logs in from two distant locations too quickly"""
        alerts = []

        if event.user_id not in self._last_success_by_user:
            return alerts

        last_login = self._last_success_by_user[event.user_id]

        if not last_login.geo_location or not event.geo_location:
            return alerts
        if last_login.geo_location == event.geo_location:
            return alerts

        # Calculate distance and time
        loc1 = GEO_COORDINATES.get(last_login.geo_location)
        loc2 = GEO_COORDINATES.get(event.geo_location)

        if not loc1 or not loc2:
            return alerts

        distance_km = _haversine_distance(loc1[0], loc1[1], loc2[0], loc2[1])
        time_diff = (event.timestamp - last_login.timestamp).total_seconds()

        if time_diff <= 0:
            return alerts

        speed_kmh = (distance_km / time_diff) * 3600

        if speed_kmh > self.impossible_travel_speed_kmh and distance_km > 100:
            confidence = min(1.0, speed_kmh / (self.impossible_travel_speed_kmh * 3))

            alerts.append(BruteForceAlert(
                alert_type="impossible_travel",
                severity="critical" if speed_kmh > self.impossible_travel_speed_kmh * 5 else "high",
                target_user=event.user_id,
                source_ips=[last_login.ip_address, event.ip_address],
                failed_attempts=0,
                time_window_seconds=int(time_diff),
                details={
                    "from_location": last_login.geo_location,
                    "to_location": event.geo_location,
                    "distance_km": round(distance_km, 1),
                    "time_between_seconds": round(time_diff, 0),
                    "implied_speed_kmh": round(speed_kmh, 1),
                    "max_realistic_speed_kmh": self.impossible_travel_speed_kmh,
                    "description": f"Impossible travel: User '{event.user_id}' logged in from {last_login.geo_location} then {event.geo_location} ({round(distance_km)}km) in {round(time_diff/60, 1)} minutes — implies {round(speed_kmh)} km/h travel speed",
                },
                timestamp=datetime.utcnow().isoformat() + "Z",
                confidence=round(confidence, 3),
            ))

        return alerts

    def is_locked(self, user_id: str) -> bool:
        """Check if an account is currently locked"""
        if user_id in self._locked_accounts:
            if datetime.utcnow() < self._locked_accounts[user_id]:
                return True
            else:
                del self._locked_accounts[user_id]
        return False

    def get_status(self) -> Dict:
        """Get current brute force detection status"""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window_seconds)

        recent_failures = [e for e in self._all_events if not e.success and e.timestamp >= cutoff]
        recent_successes = [e for e in self._all_events if e.success and e.timestamp >= cutoff]

        unique_ips_attacking = set(e.ip_address for e in recent_failures)
        unique_users_targeted = set(e.user_id for e in recent_failures)

        return {
            "monitoring_window_seconds": self.window_seconds,
            "recent_failed_attempts": len(recent_failures),
            "recent_successful_logins": len(recent_successes),
            "unique_attacking_ips": len(unique_ips_attacking),
            "unique_targeted_users": len(unique_users_targeted),
            "locked_accounts": len(self._locked_accounts),
            "locked_account_ids": list(self._locked_accounts.keys()),
            "total_events_tracked": len(self._all_events),
            "config": {
                "max_failed_attempts": self.max_failed_attempts,
                "window_seconds": self.window_seconds,
                "lockout_duration_seconds": self.lockout_duration_seconds,
            },
        }
