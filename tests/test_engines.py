"""
Unit tests for all three engines.
Run with:  pytest tests/ -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engines.cyber_engine import CyberEngine
from engines.qa_engine import QAEngine
from engines.devops_engine import DevOpsEngine
from data.mock_telemetry import get_telemetry


# ── CyberEngine tests ─────────────────────────────────────────────────────────

class TestCyberEngine:
    def setup_method(self):
        self.engine = CyberEngine()

    def test_clean_telemetry_low_threat(self):
        tel = get_telemetry(1)
        tel["drs_packet_rate"] = 80
        result = self.engine.scan(tel)
        assert result["threat_score"] < 60
        assert result["encryption_ok"] is True

    def test_drs_spoof_detected(self):
        tel = get_telemetry(1)
        tel["drs_packet_rate"] = 200  # above threshold
        result = self.engine.scan(tel)
        assert any(a["type"] == "DRS_SPOOF" for a in result["anomalies"])

    def test_threat_score_bounded(self):
        tel = get_telemetry(28)  # scenario lap with high DRS rate
        result = self.engine.scan(tel)
        assert 0 <= result["threat_score"] <= 100

    def test_cves_always_present(self):
        result = self.engine.scan(get_telemetry(1))
        assert len(result["cves"]) > 0


# ── QAEngine tests ────────────────────────────────────────────────────────────

class TestQAEngine:
    def setup_method(self):
        self.engine = QAEngine()

    def test_all_pass_on_clean_lap(self):
        tel = get_telemetry(5)  # no scenario events
        tel["vsc_active"] = False
        tel["tyre_deg_model_error_pct"] = 0.5
        result = self.engine.run_suite(tel)
        assert len(result["failures"]) == 0

    def test_undercut_fails_on_vsc(self):
        tel = get_telemetry(12)  # VSC scenario
        result = self.engine.run_suite(tel)
        assert "undercut_model_v2" in result["failures"]

    def test_coverage_decreases_with_failures(self):
        tel = get_telemetry(12)
        result = self.engine.run_suite(tel)
        assert result["coverage"] < 94.2

    def test_result_counts_consistent(self):
        tel = get_telemetry(1)
        result = self.engine.run_suite(tel)
        assert result["passed"] + len(result["failures"]) == result["total"]


# ── DevOpsEngine tests ────────────────────────────────────────────────────────

class TestDevOpsEngine:
    def setup_method(self):
        self.engine = DevOpsEngine()

    def test_all_keys_present(self):
        result = self.engine.check()
        required = [
            "telemetry_latency_ms", "strategy_api_latency_ms",
            "radio_encoder_latency_ms", "pit_wall_uptime_pct",
            "strategy_cpu_pct", "cicd_status", "replicas", "alerts",
        ]
        for key in required:
            assert key in result, f"Missing key: {key}"

    def test_latency_positive(self):
        result = self.engine.check()
        assert result["telemetry_latency_ms"] > 0
        assert result["strategy_api_latency_ms"] > 0

    def test_uptime_realistic(self):
        result = self.engine.check()
        assert 99.0 <= result["pit_wall_uptime_pct"] <= 100.0

    def test_replicas_scale_with_cpu(self):
        # Run multiple times to hit the high-CPU branch
        results = [self.engine.check() for _ in range(20)]
        high_cpu = [r for r in results if r["strategy_cpu_pct"] > 75]
        if high_cpu:
            assert all(r["replicas"] == 3 for r in high_cpu)


# ── Mock telemetry tests ──────────────────────────────────────────────────────

class TestMockTelemetry:
    def test_basic_keys(self):
        tel = get_telemetry(1)
        assert "speed_kph" in tel
        assert "tyre_compound" in tel
        assert tel["lap"] == 1

    def test_scenario_lap_12_has_vsc(self):
        tel = get_telemetry(12)
        assert tel["vsc_active"] is True
        assert tel["predicted_gap_s"] == 0.0

    def test_scenario_lap_28_has_drs_spoof(self):
        tel = get_telemetry(28)
        assert tel["drs_packet_rate"] == 180
