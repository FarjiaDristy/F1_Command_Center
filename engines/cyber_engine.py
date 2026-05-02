"""
Cybersecurity engine — CVE database, anomaly detection, threat scoring.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


# ── CVE database (extend this with real NVD API calls later) ─────────────────
CVE_DB = [
    {
        "id": "CVE-2024-3921",
        "severity": "HIGH",
        "desc": "Pit wall comms library outdated — remote code execution possible",
        "cvss": 8.8,
    },
    {
        "id": "CVE-2024-1102",
        "severity": "MEDIUM",
        "desc": "Telemetry dashboard XSS vulnerability in chart renderer",
        "cvss": 5.4,
    },
    {
        "id": "CVE-2023-9871",
        "severity": "LOW",
        "desc": "Deprecated SSL 3.0 handshake in legacy logger endpoint",
        "cvss": 3.1,
    },
]

# Severity multipliers for composite threat score
SEVERITY_WEIGHT = {"HIGH": 40, "MEDIUM": 20, "LOW": 5}


@dataclass
class Anomaly:
    type: str
    severity: str
    detail: str


@dataclass
class CyberReport:
    threat_score: int
    cves: List[dict]
    anomalies: List[dict]
    encryption_ok: bool


class CyberEngine:
    """
    Scans live telemetry for anomalies and computes a composite threat score.

    TODO (you): Replace CVE_DB with a live NVD API fetch:
        GET https://services.nvd.nist.gov/rest/json/cves/2.0
    """

    # Threshold above which a DRS packet rate is considered abnormal
    DRS_RATE_THRESHOLD = 150  # packets/second

    def scan(self, telemetry: dict) -> dict:
        anomalies: List[dict] = []

        # ── Anomaly: DRS packet spoofing ─────────────────────────────────────
        drs_rate = telemetry.get("drs_packet_rate", 0)
        if drs_rate > self.DRS_RATE_THRESHOLD:
            anomalies.append({
                "type": "DRS_SPOOF",
                "severity": "HIGH",
                "detail": f"Unusual DRS packet rate: {drs_rate} pkt/s (threshold {self.DRS_RATE_THRESHOLD})",
            })

        # ── Anomaly: GPS drift ────────────────────────────────────────────────
        gps_drift = telemetry.get("gps_drift_m", 0)
        if gps_drift > 2.5:
            anomalies.append({
                "type": "GPS_DRIFT",
                "severity": "MEDIUM",
                "detail": f"Car GPS drifting {gps_drift:.1f}m — possible signal interference",
            })

        # ── Anomaly: unexpected pit command ───────────────────────────────────
        if telemetry.get("unauthorized_pit_command"):
            anomalies.append({
                "type": "UNAUTHORIZED_PIT_CMD",
                "severity": "HIGH",
                "detail": "Pit command received from unknown source IP — possible replay attack",
            })

        # ── Threat score calculation ──────────────────────────────────────────
        cve_score = sum(SEVERITY_WEIGHT.get(c["severity"], 0) for c in CVE_DB)
        anomaly_score = sum(SEVERITY_WEIGHT.get(a["severity"], 0) for a in anomalies)
        threat_score = min(100, (cve_score // 3) + anomaly_score)

        return {
            "threat_score": threat_score,
            "cves": CVE_DB,
            "anomalies": anomalies,
            "encryption_ok": telemetry.get("encryption_verified", True),
        }
