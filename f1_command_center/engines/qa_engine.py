"""
QA / Testing engine — race strategy model test suite + bug tracker.
"""

from __future__ import annotations
from typing import Dict


# ── Test definitions ──────────────────────────────────────────────────────────
# Each entry: test_id -> callable(telemetry) -> (passed: bool, bug_id, detail)
# Add your own test functions below following the same pattern.

def _test_pit_stop_delta(tel: dict):
    """Verifies the pit stop delta calculator handles all compound types."""
    compound = tel.get("tyre_compound", "medium")
    valid_compounds = {"soft", "medium", "hard", "intermediate", "wet"}
    if compound not in valid_compounds:
        return False, "F1-210", f"Unknown compound '{compound}' — delta calc undefined"
    return True, None, None


def _test_undercut_model(tel: dict):
    """Undercut model must not produce 0-second gaps under VSC."""
    if tel.get("vsc_active") and tel.get("predicted_gap_s", 1.0) == 0.0:
        return False, "F1-884", "Null pointer in lap delta calc during VSC entry"
    return True, None, None


def _test_tyre_deg_regression(tel: dict):
    """Tyre degradation curve must stay within ±3% of baseline."""
    deg_error = tel.get("tyre_deg_model_error_pct", 0.0)
    if abs(deg_error) > 3.0:
        return False, "F1-901", f"Tyre deg model error {deg_error:.1f}% — exceeds 3% tolerance"
    return True, None, None


def _test_safety_car_delta(tel: dict):
    """Safety car delta must be positive and non-zero."""
    sc_delta = tel.get("safety_car_delta_s", 5.0)
    if sc_delta <= 0:
        return False, "F1-933", f"Safety car delta {sc_delta}s — must be positive"
    return True, None, None


def _test_drs_activation_window(tel: dict):
    """DRS window should only activate beyond 1 second gap."""
    gap = tel.get("gap_to_ahead_s", 2.0)
    drs_enabled = tel.get("drs_enabled", False)
    if drs_enabled and gap > 1.0:
        return False, "F1-960", f"DRS active with {gap:.2f}s gap — should be disabled beyond 1s"
    return True, None, None


# Registry of all tests
TEST_REGISTRY: Dict[str, callable] = {
    "pit_stop_delta_calc":     _test_pit_stop_delta,
    "undercut_model_v2":       _test_undercut_model,
    "tyre_deg_regression":     _test_tyre_deg_regression,
    "safety_car_delta":        _test_safety_car_delta,
    "drs_activation_window":   _test_drs_activation_window,
}


class QAEngine:
    """
    Runs the strategy model test suite against live telemetry each lap.

    TODO (you): Integrate with your real strategy simulation binary by
    replacing the test functions above with subprocess calls or API calls
    to your strategy solver.
    """

    # Coverage is simulated here — replace with actual coverage.py output
    BASE_COVERAGE = 94.2

    def run_suite(self, telemetry: dict) -> dict:
        results: Dict[str, dict] = {}
        failures = []

        for test_id, test_fn in TEST_REGISTRY.items():
            passed, bug_id, detail = test_fn(telemetry)
            if passed:
                results[test_id] = {"status": "PASS"}
            else:
                results[test_id] = {"status": "FAIL", "bug": bug_id, "detail": detail}
                failures.append(test_id)

        # Penalise coverage slightly per failure (simulation only)
        coverage = max(0.0, self.BASE_COVERAGE - len(failures) * 1.5)

        return {
            "results": results,
            "coverage": round(coverage, 1),
            "failures": failures,
            "total": len(TEST_REGISTRY),
            "passed": len(TEST_REGISTRY) - len(failures),
        }
