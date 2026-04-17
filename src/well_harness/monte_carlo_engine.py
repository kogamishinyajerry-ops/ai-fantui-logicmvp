"""
Monte Carlo reliability simulation engine for thrust-reverser system.

Consumes hardware parameters from P19.1 YAML config and runs statistical
simulation to estimate deployment reliability metrics.

MUST use numpy.random directly — no LLM for probability calculations.
Freeze constraint: this is a SIMULATION/ANALYSIS module, not truth engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

from well_harness.hardware_schema import (
    ThrustReverserHardware,
    load_thrust_reverser_hardware,
)


# ─── Result dataclass ─────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ReliabilityResult:
    """Output of a Monte Carlo reliability simulation run."""

    n_trials: int
    n_failures: int
    success_rate: float  # fraction [0.0, 1.0]
    mean_cycles_to_failure: Optional[float]  # None if no failures
    mtbf_cycles: float  # analytical MTBF from hardware params
    seed: Optional[int]
    failure_modes: dict[str, int]  # mode name -> count
    sw1_window_crossings_mean: float  # mean SW1 crossings per trial
    sw2_window_crossings_mean: float  # mean SW2 crossings per trial


# ─── Engine ───────────────────────────────────────────────────────────────────


class MonteCarloEngine:
    """
    Monte Carlo simulation engine for thrust-reverser reliability analysis.

    Reads hardware parameters from YAML and simulates deployment cycles
    to estimate reliability metrics.

    Deterministic when `seed` is provided.

    Args:
        hardware_yaml_path: Path to thrust-reverser hardware YAML (P19.1 format).
        seed: Random seed for reproducibility. None = system randomness.
    """

    def __init__(
        self,
        hardware_yaml_path: str | Path,
        *,
        seed: Optional[int] = None,
    ) -> None:
        self.hardware = load_thrust_reverser_hardware(hardware_yaml_path)
        self._seed = seed

    def run(self, n_trials: int, seed: Optional[int] = None) -> ReliabilityResult:
        """
        Run Monte Carlo simulation for n_trials deployment cycles.

        Args:
            n_trials: Number of Monte Carlo trials to run.
            seed: Override random seed for this run (optional).

        Returns:
            ReliabilityResult with aggregated statistics.
        """
        rng = np.random.default_rng(seed if seed is not None else self._seed)
        hw = self.hardware

        # Extract hardware parameters
        ra_threshold = hw.logic_thresholds.logic1_ra_ft_threshold
        sw1_near = hw.physical_limits.sw1_window.near_zero_deg
        sw1_deep = hw.physical_limits.sw1_window.deep_reverse_deg
        sw2_near = hw.physical_limits.sw2_window.near_zero_deg
        sw2_deep = hw.physical_limits.sw2_window.deep_reverse_deg
        ra_accuracy = hw.sensor.accuracy_ft
        deploy_rate = hw.actuator_tra.nominal_deployment_rate_percent_per_s

        n_failures = 0
        failure_modes: dict[str, int] = {
            "sw1_missed": 0,
            "sw2_missed": 0,
            "tra_stall": 0,
            "ra_sensor_failure": 0,
        }
        sw1_total_crossings = 0.0
        sw2_total_crossings = 0.0

        for _ in range(n_trials):
            # ── Simulate RA sensor reading with noise ──────────────────────
            ra_noise = rng.normal(0.0, ra_accuracy)
            # Effective RA: true threshold + noise, clipped to non-negative
            ra_effective = max(0.0, ra_threshold + ra_noise)
            ra_passed = ra_effective < ra_threshold

            if not ra_passed:
                n_failures += 1
                failure_modes["ra_sensor_failure"] += 1
                sw1_total_crossings += 0.0
                sw2_total_crossings += 0.0
                continue

            # ── Simulate TRA stall probability ─────────────────────────────
            # TRA reaches L3 threshold with base reliability ~99%
            tra_reaches_threshold = rng.random() > 0.01
            if not tra_reaches_threshold:
                n_failures += 1
                failure_modes["tra_stall"] += 1
                sw1_total_crossings += 0.0
                sw2_total_crossings += 0.0
                continue

            # ── Simulate SW1 window crossings ───────────────────────────────
            sw1_lambda = deploy_rate * abs(sw1_deep - sw1_near) / 100.0
            sw1_crossings = rng.poisson(sw1_lambda)
            # SW1 closes successfully based on deploy rate probability
            sw1_closed = rng.random() < (deploy_rate / 100.0)
            if not sw1_closed:
                n_failures += 1
                failure_modes["sw1_missed"] += 1
                sw1_total_crossings += float(sw1_crossings)
                sw2_total_crossings += 0.0
                continue
            sw1_total_crossings += float(sw1_crossings)

            # ── Simulate SW2 window crossings ──────────────────────────────
            sw2_lambda = deploy_rate * abs(sw2_deep - sw2_near) / 100.0
            sw2_crossings = rng.poisson(sw2_lambda)
            sw2_closed = rng.random() < (deploy_rate / 100.0)
            if not sw2_closed:
                n_failures += 1
                failure_modes["sw2_missed"] += 1
                sw2_total_crossings += float(sw2_crossings)
                continue
            sw2_total_crossings += float(sw2_crossings)

        # ── Compute aggregated metrics ─────────────────────────────────────
        success_rate = (n_trials - n_failures) / n_trials if n_trials > 0 else 1.0

        if n_failures > 0:
            mean_cycles_to_failure = float(n_trials) / n_failures
        else:
            mean_cycles_to_failure = None

        # Analytical MTBF from hardware timing parameters
        # MTBF ≈ 1 / failure_rate, where failure rate derived from timing delays
        tls_delay = hw.timing.tls_unlock_delay_s
        pls_delay = hw.timing.pls_unlock_delay_s
        # Use sum of delay inverses as proxy for failure rate
        failure_rate = tls_delay + pls_delay
        mtbf_cycles = 1.0 / max(1e-9, failure_rate)

        return ReliabilityResult(
            n_trials=n_trials,
            n_failures=n_failures,
            success_rate=success_rate,
            mean_cycles_to_failure=mean_cycles_to_failure,
            mtbf_cycles=mtbf_cycles,
            seed=seed if seed is not None else self._seed,
            failure_modes=dict(failure_modes),
            sw1_window_crossings_mean=sw1_total_crossings / n_trials if n_trials > 0 else 0.0,
            sw2_window_crossings_mean=sw2_total_crossings / n_trials if n_trials > 0 else 0.0,
        )
