"""
Reverse diagnosis engine for thrust-reverser system.

Given a desired outcome (e.g., "logic3_active"), enumerates all parameter
combinations within YAML-defined ranges that satisfy the outcome.

This is a DIAGNOSIS ANALYZER — it reads hardware YAML and produces enumerated
possibilities. It does NOT call controller.py or affect truth engine behavior.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from well_harness.hardware_schema import (
    ThrustReverserHardware,
    load_thrust_reverser_hardware,
)


# ─── Constants ─────────────────────────────────────────────────────────────────

MAX_COMBINATIONS = 1000  # Safety bound to prevent runaway enumeration

VALID_OUTCOMES = {
    "logic3_active",       # TRA <= threshold AND TLS unlocked AND SW2 closed
    "logic1_active",       # RA < threshold AND SW1 closed AND not inhibited
    "thr_lock_active",     # pls_power active AND pls_unlocked
    "deploy_confirmed",    # VDT >= 90% AND thr_lock active
    "tls_unlocked",       # tls_unlock_delay elapsed
    "pls_unlocked",       # pls_unlock_delay elapsed
}

# Parameter grid resolution (number of steps per dimension)
_GRID_RESOLUTION = 20  # Finer grid to capture switch windows (~1.6 deg steps)


# ─── Dataclasses ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ParameterSnapshot:
    """A parameter combination that satisfies the target outcome."""

    radio_altitude_ft: float
    tra_deg: float
    sw1_closed: bool
    sw2_closed: bool
    tls_unlocked: bool
    pls_unlocked: bool
    vdt_percent: float
    n1k: float
    reverser_inhibited: bool


# ─── Engine ───────────────────────────────────────────────────────────────────


class ReverseDiagnosisEngine:
    """
    Reverse diagnosis engine for thrust-reverser parameter analysis.

    Enumerates parameter combinations within YAML-defined ranges that satisfy
    a given target outcome.

    Deterministic — no randomness.

    Args:
        hardware_yaml_path: Path to thrust-reverser hardware YAML (P19.1 format).
    """

    def __init__(self, hardware_yaml_path: str | Path) -> None:
        self.hardware = load_thrust_reverser_hardware(hardware_yaml_path)

    def diagnose(
        self,
        outcome: str,
        *,
        max_results: int = MAX_COMBINATIONS,
    ) -> list[ParameterSnapshot]:
        """
        Enumerate parameter combinations that satisfy the target outcome.

        Args:
            outcome: One of VALID_OUTCOMES (e.g., "logic3_active").
            max_results: Maximum number of combinations to return.

        Returns:
            List of ParameterSnapshot, each satisfying the outcome.

        Raises:
            ValueError: Unknown outcome string.
        """
        if outcome not in VALID_OUTCOMES:
            raise ValueError(
                f"Unknown outcome: {outcome!r}. "
                f"Valid outcomes: {sorted(VALID_OUTCOMES)}"
            )

        hw = self.hardware
        results: list[ParameterSnapshot] = []

        # ── Grid-enumerate within YAML parameter ranges ─────────────────────
        ra_values = _linspace(0.0, hw.sensor.typical_range_ft, _GRID_RESOLUTION)
        tra_values = _linspace(
            hw.physical_limits.reverse_travel_min_deg,
            hw.physical_limits.reverse_travel_max_deg,
            _GRID_RESOLUTION,
        )
        vdt_values = _linspace(0.0, 100.0, _GRID_RESOLUTION)
        n1k_values = [50.0, 80.0, 95.0]  # Representative N1K values

        for ra in ra_values:
            for tra in tra_values:
                for vdt in vdt_values:
                    for n1k in n1k_values:
                        for inhibited in (False, True):
                            # Compute derived states
                            sw1_closed = _sw1_closed(tra, hw)
                            sw2_closed = _sw2_closed(tra, hw)
                            tls_unlocked = True  # Assume unlocked for logic3
                            pls_unlocked = True  # Assume unlocked for thr_lock

                            # ── Evaluate outcome conditions ───────────────────
                            satisfies = False
                            if outcome == "logic3_active":
                                tra_thresh = hw.logic_thresholds.logic3_tra_deg_threshold
                                satisfies = (
                                    tra <= tra_thresh
                                    and tls_unlocked
                                    and sw2_closed
                                    and not inhibited
                                )
                            elif outcome == "logic1_active":
                                ra_thresh = hw.logic_thresholds.logic1_ra_ft_threshold
                                satisfies = (
                                    ra < ra_thresh
                                    and sw1_closed
                                    and not inhibited
                                )
                            elif outcome == "thr_lock_active":
                                pls_delay = hw.timing.pls_unlock_delay_s
                                satisfies = pls_unlocked
                            elif outcome == "deploy_confirmed":
                                vdt_thresh = hw.logic_thresholds.deploy_90_threshold_percent
                                pls_delay = hw.timing.pls_unlock_delay_s
                                satisfies = (
                                    vdt >= vdt_thresh
                                    and pls_unlocked
                                )
                            elif outcome == "tls_unlocked":
                                tls_delay = hw.timing.tls_unlock_delay_s
                                satisfies = tls_unlocked
                            elif outcome == "pls_unlocked":
                                pls_delay = hw.timing.pls_unlock_delay_s
                                satisfies = pls_unlocked

                            if satisfies:
                                if len(results) >= max_results:
                                    return results
                                results.append(
                                    ParameterSnapshot(
                                        radio_altitude_ft=ra,
                                        tra_deg=tra,
                                        sw1_closed=sw1_closed,
                                        sw2_closed=sw2_closed,
                                        tls_unlocked=tls_unlocked,
                                        pls_unlocked=pls_unlocked,
                                        vdt_percent=vdt,
                                        n1k=n1k,
                                        reverser_inhibited=inhibited,
                                    )
                                )

        return results

    def diagnose_and_report(
        self,
        outcome: str,
        *,
        max_results: int = MAX_COMBINATIONS,
    ) -> dict:
        """
        Convenience wrapper: run diagnose() and return a serializable report dict.

        Returns:
            {
                "outcome": outcome,
                "total_combos_found": len(results),
                "grid_resolution": _GRID_RESOLUTION,
                "timestamp": "<ISO-8601>",
                "results": [list of ParameterSnapshot dicts],
            }
        """
        from datetime import datetime, timezone

        results = self.diagnose(outcome, max_results=max_results)
        return {
            "outcome": outcome,
            "total_combos_found": len(results),
            "grid_resolution": _GRID_RESOLUTION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": [_parameter_snapshot_to_dict(r) for r in results],
        }


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _parameter_snapshot_to_dict(snapshot: ParameterSnapshot) -> dict:
    """Convert a ParameterSnapshot to a plain dict for JSON serialization."""
    return {
        "radio_altitude_ft": snapshot.radio_altitude_ft,
        "tra_deg": snapshot.tra_deg,
        "sw1_closed": snapshot.sw1_closed,
        "sw2_closed": snapshot.sw2_closed,
        "tls_unlocked": snapshot.tls_unlocked,
        "pls_unlocked": snapshot.pls_unlocked,
        "vdt_percent": snapshot.vdt_percent,
        "n1k": snapshot.n1k,
        "reverser_inhibited": snapshot.reverser_inhibited,
    }


def _linspace(start: float, stop: float, num: int) -> list[float]:
    """Return num evenly-spaced values in [start, stop]."""
    if num <= 1:
        return [start]
    step = (stop - start) / (num - 1)
    return [start + i * step for i in range(num)]


def _sw1_closed(tra_deg: float, hw: ThrustReverserHardware) -> bool:
    sw1 = hw.physical_limits.sw1_window
    lo = min(sw1.near_zero_deg, sw1.deep_reverse_deg)
    hi = max(sw1.near_zero_deg, sw1.deep_reverse_deg)
    return lo <= tra_deg <= hi


def _sw2_closed(tra_deg: float, hw: ThrustReverserHardware) -> bool:
    sw2 = hw.physical_limits.sw2_window
    lo = min(sw2.near_zero_deg, sw2.deep_reverse_deg)
    hi = max(sw2.near_zero_deg, sw2.deep_reverse_deg)
    return lo <= tra_deg <= hi
