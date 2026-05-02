"""
Mock telemetry feed — simulates F1 car + race data per lap.

TODO (you): Replace this with the real FastF1 library to pull
           actual session data. See README.md for instructions.
"""

from __future__ import annotations
import random
import math


# ── Race scenario definitions ─────────────────────────────────────────────────
# Certain laps trigger special conditions to make the dashboard interesting.
SCENARIO_LAPS = {
    12: {"vsc_active": True,  "predicted_gap_s": 0.0},    # VSC + QA bug trigger
    28: {"drs_packet_rate": 180, "gps_drift_m": 0.4},     # DRS spoof attempt
    34: {"unauthorized_pit_command": True},                # Replay attack sim
    41: {"vsc_active": False, "drs_enabled": True,
         "gap_to_ahead_s": 1.8},                           # DRS window edge case
    50: {"tyre_deg_model_error_pct": 4.2},                 # Tyre model regression
}


def get_telemetry(lap: int) -> dict:
    """
    Returns a telemetry snapshot for the given lap number.
    Merges base random values with any scripted scenario events.
    """
    base = {
        # Car state
        "lap":                       lap,
        "speed_kph":                 random.randint(280, 330),
        "throttle_pct":              random.randint(60, 100),
        "brake_pct":                 random.randint(0, 40),
        "gear":                      random.randint(6, 8),
        "drs_enabled":               random.random() < 0.3,
        "tyre_compound":             random.choice(["soft", "medium", "hard"]),
        "tyre_age_laps":             lap % 15,

        # Race state
        "gap_to_ahead_s":            round(random.uniform(0.3, 4.0), 2),
        "gap_to_behind_s":           round(random.uniform(0.3, 6.0), 2),
        "safety_car_delta_s":        round(random.uniform(3.0, 7.0), 1),
        "vsc_active":                False,
        "sc_active":                 False,
        "predicted_gap_s":           round(random.uniform(0.5, 3.0), 2),

        # Telemetry signal quality
        "drs_packet_rate":           random.randint(60, 120),  # normal = 60–120
        "gps_drift_m":               round(random.uniform(0.0, 0.8), 2),
        "encryption_verified":       True,
        "unauthorized_pit_command":  False,

        # QA model inputs
        "tyre_deg_model_error_pct":  round(random.uniform(-1.5, 1.5), 2),

        # Lap metadata
        "air_temp_c":                random.randint(18, 32),
        "track_temp_c":              random.randint(28, 52),
        "humidity_pct":              random.randint(30, 70),
    }

    # Overlay any scripted scenario for this lap
    if lap in SCENARIO_LAPS:
        base.update(SCENARIO_LAPS[lap])

    return base
