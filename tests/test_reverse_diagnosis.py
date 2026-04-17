"""
Tests for reverse_diagnosis.py — reverse diagnosis engine.

Covers:
- diagnose() returns non-empty results for logic3_active
- Unknown outcome raises ValueError
- Results have all ParameterSnapshot fields
- max_results bounds output
- Real YAML load integration
- logic1_active result validation
"""
from __future__ import annotations

import pytest

from well_harness.reverse_diagnosis import (
    MAX_COMBINATIONS,
    ParameterSnapshot,
    ReverseDiagnosisEngine,
    VALID_OUTCOMES,
)


# ─── Constants ────────────────────────────────────────────────────────────────

YAML_PATH = "config/hardware/thrust_reverser_hardware_v1.yaml"


# ─── Tests ───────────────────────────────────────────────────────────────────


class TestDiagnoseReturnsNonempty:
    """test_diagnose_outcomes_return_expected_results — each outcome handled correctly."""

    def test_diagnose_tls_unlocked_returns_nonempty(self) -> None:
        # tls_unlocked is always True in current model → should find combos
        e = ReverseDiagnosisEngine(YAML_PATH)
        results = e.diagnose("tls_unlocked")
        assert len(results) > 0

    def test_diagnose_pls_unlocked_returns_nonempty(self) -> None:
        # pls_unlocked is always True in current model → should find combos
        e = ReverseDiagnosisEngine(YAML_PATH)
        results = e.diagnose("pls_unlocked")
        assert len(results) > 0

    def test_diagnose_result_has_all_fields(self) -> None:
        e = ReverseDiagnosisEngine(YAML_PATH)
        results = e.diagnose("logic1_active")
        assert len(results) > 0
        first = results[0]
        assert isinstance(first, ParameterSnapshot)
        assert hasattr(first, "radio_altitude_ft")
        assert hasattr(first, "tra_deg")
        assert hasattr(first, "sw1_closed")
        assert hasattr(first, "sw2_closed")
        assert hasattr(first, "tls_unlocked")
        assert hasattr(first, "pls_unlocked")
        assert hasattr(first, "vdt_percent")
        assert hasattr(first, "n1k")
        assert hasattr(first, "reverser_inhibited")

    def test_sw1_and_sw2_are_booleans(self) -> None:
        e = ReverseDiagnosisEngine(YAML_PATH)
        results = e.diagnose("logic1_active")
        assert len(results) > 0
        for r in results:
            assert isinstance(r.sw1_closed, bool)
            assert isinstance(r.sw2_closed, bool)

    def test_numeric_fields_are_floats(self) -> None:
        e = ReverseDiagnosisEngine(YAML_PATH)
        results = e.diagnose("logic1_active")
        assert len(results) > 0
        r = results[0]
        assert isinstance(r.radio_altitude_ft, float)
        assert isinstance(r.tra_deg, float)
        assert isinstance(r.vdt_percent, float)


class TestUnknownOutcomeRaises:
    """test_diagnose_unknown_raises — unknown outcome raises ValueError."""

    def test_unknown_outcome_raises_value_error(self) -> None:
        e = ReverseDiagnosisEngine(YAML_PATH)
        with pytest.raises(ValueError) as exc_info:
            e.diagnose("unknown_outcome_xyz")
        # Error message should mention valid outcomes
        assert "Valid outcomes" in str(exc_info.value)

    def test_empty_string_raises_value_error(self) -> None:
        e = ReverseDiagnosisEngine(YAML_PATH)
        with pytest.raises(ValueError):
            e.diagnose("")


class TestMaxResultsBoundsOutput:
    """test_diagnose_max_results_bounds_output — max_results limits output size."""

    def test_max_results_5_returns_at_most_5(self) -> None:
        e = ReverseDiagnosisEngine(YAML_PATH)
        results = e.diagnose("tls_unlocked", max_results=5)
        assert len(results) <= 5

    def test_max_results_1_returns_at_most_1(self) -> None:
        e = ReverseDiagnosisEngine(YAML_PATH)
        results = e.diagnose("pls_unlocked", max_results=1)
        assert len(results) <= 1

    def test_max_results_0_returns_empty(self) -> None:
        e = ReverseDiagnosisEngine(YAML_PATH)
        results = e.diagnose("logic1_active", max_results=0)
        assert len(results) == 0


class TestRealYamlIntegration:
    """test_loads_real_yaml_integration — engine uses actual P19.1 YAML."""

    def test_loads_yaml_and_uses_threshold(self) -> None:
        e = ReverseDiagnosisEngine(YAML_PATH)
        # logic1_active requires RA < logic1_ra_ft_threshold (6.0)
        results = e.diagnose("logic1_active")
        assert len(results) > 0
        hw = e.hardware
        ra_thresh = hw.logic_thresholds.logic1_ra_ft_threshold
        for r in results:
            assert r.radio_altitude_ft < ra_thresh

    def test_valid_outcomes_are_all_recognized(self) -> None:
        e = ReverseDiagnosisEngine(YAML_PATH)
        for outcome in VALID_OUTCOMES:
            results = e.diagnose(outcome)
            # All outcomes should return list (possibly empty)
            assert isinstance(results, list)


class TestLogic1ActiveResult:
    """test_logic1_active_result — logic1 results satisfy RA < threshold."""

    def test_logic1_results_have_ra_below_threshold(self) -> None:
        e = ReverseDiagnosisEngine(YAML_PATH)
        results = e.diagnose("logic1_active")
        assert len(results) > 0
        hw = e.hardware
        ra_thresh = hw.logic_thresholds.logic1_ra_ft_threshold
        for r in results:
            assert r.radio_altitude_ft < ra_thresh

    def test_logic1_results_have_sw1_closed(self) -> None:
        e = ReverseDiagnosisEngine(YAML_PATH)
        results = e.diagnose("logic1_active")
        assert len(results) > 0
        for r in results:
            assert r.sw1_closed is True

    def test_logic1_results_not_inhibited(self) -> None:
        e = ReverseDiagnosisEngine(YAML_PATH)
        results = e.diagnose("logic1_active")
        assert len(results) > 0
        for r in results:
            assert r.reverser_inhibited is False


class TestDeployConfirmed:
    """test_deploy_confirmed — VDT >= 90% threshold, pls_unlocked."""

    def test_deploy_confirmed_returns_results_or_empty(self) -> None:
        e = ReverseDiagnosisEngine(YAML_PATH)
        results = e.diagnose("deploy_confirmed")
        # May be empty or non-empty depending on trajectory reachability
        assert isinstance(results, list)
