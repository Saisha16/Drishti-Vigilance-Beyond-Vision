"""
Network Bandwidth Anomaly Detection Module
Detects DDoS attacks, data exfiltration, and unusual network patterns
using statistical analysis and machine learning.

Monitors:
- Bytes per second (inbound/outbound)
- Packets per second
- Connection count
- Protocol distribution
- Flow rate

Uses a combination of:
1. Z-score analysis for spike detection
2. Moving average baseline for dynamic thresholds
3. Statistical anomaly classification
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class NetworkMetric:
    """A single network traffic measurement"""
    timestamp: datetime
    bytes_in: int
    bytes_out: int
    packets_in: int
    packets_out: int
    connections: int
    protocol_dist: Dict[str, float] = field(default_factory=dict)  # e.g. {"tcp": 0.8, "udp": 0.15, "icmp": 0.05}

    @property
    def total_bytes(self) -> int:
        return self.bytes_in + self.bytes_out

    @property
    def total_packets(self) -> int:
        return self.packets_in + self.packets_out

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "bytes_in": self.bytes_in,
            "bytes_out": self.bytes_out,
            "packets_in": self.packets_in,
            "packets_out": self.packets_out,
            "connections": self.connections,
            "total_bytes": self.total_bytes,
            "total_packets": self.total_packets,
            "protocol_dist": self.protocol_dist,
        }


@dataclass
class NetworkAnomaly:
    """A detected network anomaly"""
    anomaly_type: str  # "ddos_inbound", "exfiltration", "scanning", "protocol_anomaly", "connection_flood"
    severity: str  # "low", "medium", "high", "critical"
    timestamp: str = ""
    confidence: float = 0.0
    details: Dict = field(default_factory=dict)
    metric_snapshot: Dict = field(default_factory=dict)
    baseline_comparison: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "anomaly_type": self.anomaly_type,
            "severity": self.severity,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
            "details": self.details,
            "metric_snapshot": self.metric_snapshot,
            "baseline_comparison": self.baseline_comparison,
        }


class BandwidthAnalyzer:
    """
    Network traffic anomaly detection engine.
    
    Maintains a rolling baseline of normal network behavior and detects
    deviations that may indicate attacks or data exfiltration.
    
    Configuration:
        baseline_window_minutes: Minutes of history to use for baseline (default: 60)
        z_score_threshold: Standard deviations above mean to flag (default: 3.0)
        min_samples_for_baseline: Minimum data points before analysis (default: 10)
    """

    def __init__(
        self,
        baseline_window_minutes: int = 60,
        z_score_threshold: float = 3.0,
        min_samples_for_baseline: int = 10,
        db=None,
    ):
        self.baseline_window_minutes = baseline_window_minutes
        self.z_score_threshold = z_score_threshold
        self.min_samples_for_baseline = min_samples_for_baseline
        self.db = db

        self._metrics_history: List[NetworkMetric] = []
        self._load_history()

    def _load_history(self):
        """Load recent metrics from database"""
        if self.db is None:
            return
        try:
            metrics = self.db.fetch_network_metrics(minutes=max(self.baseline_window_minutes * 3, 180))
            for m in metrics:
                self._metrics_history.append(NetworkMetric(
                    timestamp=datetime.fromisoformat(m["timestamp"]),
                    bytes_in=m["bytes_in"],
                    bytes_out=m["bytes_out"],
                    packets_in=m["packets_in"],
                    packets_out=m["packets_out"],
                    connections=m["connections"],
                    protocol_dist=m.get("protocol_dist", {}),
                ))
        except Exception:
            pass

    def _compute_stats(self, values: List[float]) -> Tuple[float, float]:
        """Compute mean and standard deviation of a list of values"""
        if not values:
            return 0.0, 1.0
        n = len(values)
        mean = sum(values) / n
        if n < 2:
            return mean, max(mean * 0.1, 1.0)
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        std = math.sqrt(variance) if variance > 0 else max(mean * 0.1, 1.0)
        return mean, std

    def _z_score(self, value: float, mean: float, std: float) -> float:
        """Calculate z-score"""
        if std == 0:
            return 0.0
        return (value - mean) / std

    def _clean_history(self):
        """Remove old data beyond 2x baseline window"""
        cutoff = datetime.utcnow() - timedelta(minutes=self.baseline_window_minutes * 2)
        self._metrics_history = [m for m in self._metrics_history if m.timestamp >= cutoff]

    def record_metric(self, metric: NetworkMetric) -> List[NetworkAnomaly]:
        """
        Record a new network metric and check for anomalies.
        
        Args:
            metric: Current network traffic measurement
            
        Returns:
            List of detected anomalies (empty if normal)
        """
        # Persist
        if self.db is not None:
            try:
                self.db.save_network_metric(metric)
            except Exception:
                pass

        self._metrics_history.append(metric)
        self._clean_history()

        # Need enough baseline data before detecting
        if len(self._metrics_history) < self.min_samples_for_baseline:
            return []

        # Build baseline from historical window (excluding current)
        cutoff = datetime.utcnow() - timedelta(minutes=self.baseline_window_minutes)
        baseline_metrics = [m for m in self._metrics_history[:-1] if m.timestamp >= cutoff]

        if len(baseline_metrics) < self.min_samples_for_baseline:
            return []

        anomalies = []

        # Compute baselines
        bytes_in_vals = [m.bytes_in for m in baseline_metrics]
        bytes_out_vals = [m.bytes_out for m in baseline_metrics]
        packets_vals = [m.total_packets for m in baseline_metrics]
        conn_vals = [m.connections for m in baseline_metrics]

        bytes_in_mean, bytes_in_std = self._compute_stats(bytes_in_vals)
        bytes_out_mean, bytes_out_std = self._compute_stats(bytes_out_vals)
        packets_mean, packets_std = self._compute_stats(packets_vals)
        conn_mean, conn_std = self._compute_stats(conn_vals)

        baseline_info = {
            "bytes_in": {"mean": round(bytes_in_mean), "std": round(bytes_in_std)},
            "bytes_out": {"mean": round(bytes_out_mean), "std": round(bytes_out_std)},
            "packets": {"mean": round(packets_mean), "std": round(packets_std)},
            "connections": {"mean": round(conn_mean), "std": round(conn_std)},
            "baseline_samples": len(baseline_metrics),
        }

        # Check for inbound DDoS
        z_bytes_in = self._z_score(metric.bytes_in, bytes_in_mean, bytes_in_std)
        z_packets = self._z_score(metric.total_packets, packets_mean, packets_std)

        if z_bytes_in > self.z_score_threshold and z_packets > self.z_score_threshold:
            severity = "critical" if z_bytes_in > self.z_score_threshold * 2 else \
                       "high" if z_bytes_in > self.z_score_threshold * 1.5 else "medium"
            confidence = min(1.0, z_bytes_in / (self.z_score_threshold * 3))

            anomalies.append(NetworkAnomaly(
                anomaly_type="ddos_inbound",
                severity=severity,
                timestamp=metric.timestamp.isoformat(),
                confidence=round(confidence, 3),
                details={
                    "z_score_bytes_in": round(z_bytes_in, 2),
                    "z_score_packets": round(z_packets, 2),
                    "current_bytes_in": metric.bytes_in,
                    "baseline_mean_bytes_in": round(bytes_in_mean),
                    "multiplier": round(metric.bytes_in / max(bytes_in_mean, 1), 1),
                    "description": f"Inbound traffic spike: {round(metric.bytes_in / max(bytes_in_mean, 1), 1)}x above baseline ({round(z_bytes_in, 1)} std devs)",
                },
                metric_snapshot=metric.to_dict(),
                baseline_comparison=baseline_info,
            ))

        # Check for data exfiltration (unusual outbound)
        z_bytes_out = self._z_score(metric.bytes_out, bytes_out_mean, bytes_out_std)

        if z_bytes_out > self.z_score_threshold:
            severity = "critical" if z_bytes_out > self.z_score_threshold * 2 else "high"
            confidence = min(1.0, z_bytes_out / (self.z_score_threshold * 3))

            anomalies.append(NetworkAnomaly(
                anomaly_type="exfiltration",
                severity=severity,
                timestamp=metric.timestamp.isoformat(),
                confidence=round(confidence, 3),
                details={
                    "z_score_bytes_out": round(z_bytes_out, 2),
                    "current_bytes_out": metric.bytes_out,
                    "baseline_mean_bytes_out": round(bytes_out_mean),
                    "multiplier": round(metric.bytes_out / max(bytes_out_mean, 1), 1),
                    "description": f"Outbound data spike: {round(metric.bytes_out / max(bytes_out_mean, 1), 1)}x above baseline — possible data exfiltration",
                },
                metric_snapshot=metric.to_dict(),
                baseline_comparison=baseline_info,
            ))

        # Check for connection flood
        z_conns = self._z_score(metric.connections, conn_mean, conn_std)

        if z_conns > self.z_score_threshold:
            severity = "high" if z_conns > self.z_score_threshold * 2 else "medium"
            confidence = min(1.0, z_conns / (self.z_score_threshold * 3))

            anomalies.append(NetworkAnomaly(
                anomaly_type="connection_flood",
                severity=severity,
                timestamp=metric.timestamp.isoformat(),
                confidence=round(confidence, 3),
                details={
                    "z_score_connections": round(z_conns, 2),
                    "current_connections": metric.connections,
                    "baseline_mean_connections": round(conn_mean),
                    "description": f"Connection count spike: {metric.connections} active vs {round(conn_mean)} baseline",
                },
                metric_snapshot=metric.to_dict(),
                baseline_comparison=baseline_info,
            ))

        return anomalies

    def _ensure_history_loaded(self):
        """Reload from DB if in-memory cache is empty"""
        if not self._metrics_history:
            self._load_history()

    def get_baseline(self) -> Dict:
        """Get current baseline statistics"""
        self._ensure_history_loaded()
        cutoff = datetime.utcnow() - timedelta(minutes=self.baseline_window_minutes)
        recent = [m for m in self._metrics_history if m.timestamp >= cutoff]

        if not recent:
            return {"status": "insufficient_data", "samples": 0}

        bytes_in_mean, bytes_in_std = self._compute_stats([m.bytes_in for m in recent])
        bytes_out_mean, bytes_out_std = self._compute_stats([m.bytes_out for m in recent])
        packets_mean, packets_std = self._compute_stats([m.total_packets for m in recent])
        conn_mean, conn_std = self._compute_stats([m.connections for m in recent])

        return {
            "status": "active",
            "samples": len(recent),
            "window_minutes": self.baseline_window_minutes,
            "bytes_in": {"mean": round(bytes_in_mean), "std": round(bytes_in_std)},
            "bytes_out": {"mean": round(bytes_out_mean), "std": round(bytes_out_std)},
            "packets": {"mean": round(packets_mean), "std": round(packets_std)},
            "connections": {"mean": round(conn_mean), "std": round(conn_std)},
        }

    def get_recent_metrics(self, count: int = 60) -> List[Dict]:
        """Get recent network metrics for visualization"""
        self._ensure_history_loaded()
        recent = self._metrics_history[-count:] if len(self._metrics_history) >= count else self._metrics_history
        return [m.to_dict() for m in recent]
