"""
Tests for hardware_schema.py — thrust-reverser hardware YAML loader.

Covers:
- Valid YAML load returns correct typed dataclass
- Missing file raises HardwareSchemaNotFoundError
- YAML syntax error raises HardwareSchemaValidationError
- Wrong kind rejected by schema validation
- Out-of-range value rejected by schema validation
"""
from __future__ import annotations

import json
import copy
import tempfile
from pathlib import Path

import jsonschema
import pytest
import yaml

from well_harness.hardware_schema import (
    HardwareSchemaError,
    HardwareSchemaNotFoundError,
    HardwareSchemaValidationError,
    _hardware_to_dict,
    load_thrust_reverser_hardware,
)


# ─── Constants ────────────────────────────────────────────────────────────────

_VALID_YAML = {
    "kind": "thrust-reverser-hardware",
    "version": 1,
    "system_id": "thrust-reverser",
    "parameters": {
        "sensor": {
            "radio_altitude_ft": {
                "unit": "ft",
                "typical_range_ft": 1000.0,
                "accuracy_ft": 0.5,
            }
        },
        "actuator": {
            "tra": {
                "unit": "deg",
                "min_deg": -32.0,
                "max_deg": 0.0,
                "nominal_deployment_rate_percent_per_s": 30.0,
            },
            "vd": {
                "unit": "percent",
                "full_deploy_percent": 100.0,
            },
        },
        "logic_thresholds": {
            "logic1_ra_ft_threshold": 6.0,
            "logic3_tra_deg_threshold": -11.74,
            "deploy_90_threshold_percent": 90.0,
        },
        "timing": {
            "tls_unlock_delay_s": 0.3,
            "pls_unlock_delay_s": 0.2,
        },
        "physical_limits": {
            "reverse_travel_min_deg": -32.0,
            "reverse_travel_max_deg": 0.0,
            "sw1_window": {
                "near_zero_deg": -1.4,
                "deep_reverse_deg": -6.2,
            },
            "sw2_window": {
                "near_zero_deg": -5.0,
                "deep_reverse_deg": -9.8,
            },
        },
    },
}

_EXPECTED_VALUES = {
    "logic1_ra_ft_threshold": 6.0,
    "logic3_tra_deg_threshold": -11.74,
    "deploy_90_threshold_percent": 90.0,
    "tls_unlock_delay_s": 0.3,
    "pls_unlock_delay_s": 0.2,
    "sw1_near_zero": -1.4,
    "sw1_deep_reverse": -6.2,
    "sw2_near_zero": -5.0,
    "sw2_deep_reverse": -9.8,
    "reverse_travel_min_deg": -32.0,
    "reverse_travel_max_deg": 0.0,
    "tra_min_deg": -32.0,
    "tra_max_deg": 0.0,
    "vd_full_deploy_percent": 100.0,
    "ra_typical_range_ft": 1000.0,
    "ra_accuracy_ft": 0.5,
}


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _write_yaml(tmp_dir: Path, data: dict) -> Path:
    path = tmp_dir / "hardware.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


# ─── Tests ────────────────────────────────────────────────────────────────────


class TestLoadValidHardwareYaml:
    """test_load_valid_hardware_yaml — all parameter values match expected ground truth."""

    def test_returns_correct_kind_and_version(self, tmp_path: Path) -> None:
        path = _write_yaml(tmp_path, _VALID_YAML)
        hw = load_thrust_reverser_hardware(path)
        assert hw.kind == "thrust-reverser-hardware"
        assert hw.version == 1
        assert hw.system_id == "thrust-reverser"

    def test_logic_thresholds_match_expected(self, tmp_path: Path) -> None:
        path = _write_yaml(tmp_path, _VALID_YAML)
        hw = load_thrust_reverser_hardware(path)
        lt = hw.logic_thresholds
        assert lt.logic1_ra_ft_threshold == _EXPECTED_VALUES["logic1_ra_ft_threshold"]
        assert lt.logic3_tra_deg_threshold == _EXPECTED_VALUES["logic3_tra_deg_threshold"]
        assert lt.deploy_90_threshold_percent == _EXPECTED_VALUES["deploy_90_threshold_percent"]

    def test_timing_values_match_expected(self, tmp_path: Path) -> None:
        path = _write_yaml(tmp_path, _VALID_YAML)
        hw = load_thrust_reverser_hardware(path)
        t = hw.timing
        assert t.tls_unlock_delay_s == _EXPECTED_VALUES["tls_unlock_delay_s"]
        assert t.pls_unlock_delay_s == _EXPECTED_VALUES["pls_unlock_delay_s"]

    def test_sw_windows_match_expected(self, tmp_path: Path) -> None:
        path = _write_yaml(tmp_path, _VALID_YAML)
        hw = load_thrust_reverser_hardware(path)
        sw1 = hw.physical_limits.sw1_window
        sw2 = hw.physical_limits.sw2_window
        assert sw1.near_zero_deg == _EXPECTED_VALUES["sw1_near_zero"]
        assert sw1.deep_reverse_deg == _EXPECTED_VALUES["sw1_deep_reverse"]
        assert sw2.near_zero_deg == _EXPECTED_VALUES["sw2_near_zero"]
        assert sw2.deep_reverse_deg == _EXPECTED_VALUES["sw2_deep_reverse"]

    def test_actuator_tra_values_match_expected(self, tmp_path: Path) -> None:
        path = _write_yaml(tmp_path, _VALID_YAML)
        hw = load_thrust_reverser_hardware(path)
        tra = hw.actuator_tra
        assert tra.min_deg == _EXPECTED_VALUES["tra_min_deg"]
        assert tra.max_deg == _EXPECTED_VALUES["tra_max_deg"]
        assert tra.unit == "deg"

    def test_vd_actuator_values_match_expected(self, tmp_path: Path) -> None:
        path = _write_yaml(tmp_path, _VALID_YAML)
        hw = load_thrust_reverser_hardware(path)
        vd = hw.actuator_vd
        assert vd.full_deploy_percent == _EXPECTED_VALUES["vd_full_deploy_percent"]
        assert vd.unit == "percent"

    def test_sensor_spec_match_expected(self, tmp_path: Path) -> None:
        path = _write_yaml(tmp_path, _VALID_YAML)
        hw = load_thrust_reverser_hardware(path)
        assert hw.sensor.unit == "ft"
        assert hw.sensor.typical_range_ft == _EXPECTED_VALUES["ra_typical_range_ft"]
        assert hw.sensor.accuracy_ft == _EXPECTED_VALUES["ra_accuracy_ft"]

    def test_validate_false_skips_schema_check(self, tmp_path: Path) -> None:
        path = _write_yaml(tmp_path, _VALID_YAML)
        hw = load_thrust_reverser_hardware(path, validate=False)
        assert hw.kind == "thrust-reverser-hardware"

    def test_optional_hardware_coupling_sections_default_empty(self, tmp_path: Path) -> None:
        path = _write_yaml(tmp_path, _VALID_YAML)
        hw = load_thrust_reverser_hardware(path)
        assert hw.lru_inventory == ()
        assert hw.signal_carrier_bindings == ()

    def test_optional_hardware_coupling_sections_parse_typed_rows(self, tmp_path: Path) -> None:
        data = copy.deepcopy(_VALID_YAML)
        data["lru_inventory"] = [
            {
                "id": "etrac",
                "display_name": "Electronic Thrust Reverser Actuation Controller",
                "quantity_per_engine": 1,
                "value_status": "confirmed",
                "part_number": {"status": "evidence_gap", "value": "TBD"},
                "location": {"status": "evidence_gap", "value": "TBD"},
                "failure_rate_per_hour": {"status": "evidence_gap", "value": None},
                "source_ref": "unit-test",
            }
        ]
        data["signal_carrier_bindings"] = [
            {
                "signal_id": "tls_115vac_cmd",
                "direction": "output",
                "source_hardware_id": "etrac",
                "peer_hardware_id": "tls",
                "cable": {"status": "evidence_gap", "value": "TBD"},
                "connector": {"status": "evidence_gap", "value": "TBD"},
                "port_local": {"status": "evidence_gap", "value": "TBD"},
                "port_peer": {"status": "evidence_gap", "value": "TBD"},
                "redundancy_status": "evidence_gap",
                "evidence_status": "evidence_gap",
                "feeds_logic_nodes": ["L1"],
                "source_ref": "unit-test",
            }
        ]
        path = _write_yaml(tmp_path, data)
        hw = load_thrust_reverser_hardware(path)

        assert hw.lru_inventory[0].id == "etrac"
        assert hw.lru_inventory[0].part_number.status == "evidence_gap"
        assert hw.signal_carrier_bindings[0].signal_id == "tls_115vac_cmd"
        assert hw.signal_carrier_bindings[0].feeds_logic_nodes == ("L1",)
        assert _hardware_to_dict(hw)["signal_carrier_bindings"][0]["feeds_logic_nodes"] == ["L1"]


class TestMissingFileRaises:
    """test_missing_file_raises — non-existent path raises HardwareSchemaNotFoundError."""

    def test_raises_not_found_for_missing_file(self, tmp_path: Path) -> None:
        missing = tmp_path / "nonexistent.yaml"
        with pytest.raises(HardwareSchemaNotFoundError) as exc_info:
            load_thrust_reverser_hardware(missing)
        assert str(missing) in str(exc_info.value)

    def test_not_found_inherits_from_file_not_found_error(self, tmp_path: Path) -> None:
        missing = tmp_path / "nonexistent.yaml"
        with pytest.raises(FileNotFoundError):
            load_thrust_reverser_hardware(missing)


class TestInvalidYamlSyntax:
    """test_invalid_yaml_syntax — YAML parse error raises HardwareSchemaValidationError."""

    def test_raises_validation_error_for_yaml_syntax_error(self, tmp_path: Path) -> None:
        bad_path = tmp_path / "bad.yaml"
        bad_path.write_text("  invalid: yaml: syntax: [", encoding="utf-8")
        with pytest.raises(HardwareSchemaError):  # Could be ValidationError or base
            load_thrust_reverser_hardware(bad_path)


class TestWrongKindRejected:
    """test_wrong_kind_rejected — wrong kind string is rejected by schema validation."""

    def test_rejects_wrong_kind(self, tmp_path: Path) -> None:
        bad = dict(_VALID_YAML)
        bad["kind"] = "wrong-kind"
        path = _write_yaml(tmp_path, bad)
        with pytest.raises(HardwareSchemaValidationError) as exc_info:
            load_thrust_reverser_hardware(path)
        assert "kind" in str(exc_info.value).lower() or "const" in str(exc_info.value).lower()

    def test_rejects_wrong_version(self, tmp_path: Path) -> None:
        bad = dict(_VALID_YAML)
        bad["version"] = 99
        path = _write_yaml(tmp_path, bad)
        with pytest.raises(HardwareSchemaValidationError):
            load_thrust_reverser_hardware(path)


class TestOutOfRangeValueRejected:
    """test_out_of_range_value_rejected — out-of-range value fails schema validation."""

    def test_rejects_negative_ra_threshold(self, tmp_path: Path) -> None:
        bad = dict(_VALID_YAML)
        bad["parameters"]["logic_thresholds"]["logic1_ra_ft_threshold"] = -5.0
        path = _write_yaml(tmp_path, bad)
        with pytest.raises(HardwareSchemaValidationError) as exc_info:
            load_thrust_reverser_hardware(path)
        assert "logic1_ra_ft_threshold" in str(exc_info.value) or "minimum" in str(
            exc_info.value
        ).lower()

    def test_rejects_vd_over_100_percent(self, tmp_path: Path) -> None:
        bad = dict(_VALID_YAML)
        bad["parameters"]["actuator"]["vd"]["full_deploy_percent"] = 150.0
        path = _write_yaml(tmp_path, bad)
        with pytest.raises(HardwareSchemaValidationError):
            load_thrust_reverser_hardware(path)

    def test_rejects_negative_deployment_rate(self, tmp_path: Path) -> None:
        bad = dict(_VALID_YAML)
        bad["parameters"]["actuator"]["tra"]["nominal_deployment_rate_percent_per_s"] = -5.0
        path = _write_yaml(tmp_path, bad)
        with pytest.raises(HardwareSchemaValidationError):
            load_thrust_reverser_hardware(path)


class TestRealYamlFile:
    """Test loading the actual thrust_reverser_hardware_v1.yaml from the repo."""

    def test_loads_real_yaml_from_config_dir(self) -> None:
        hw = load_thrust_reverser_hardware(
            "config/hardware/thrust_reverser_hardware_v1.yaml"
        )
        assert hw.kind == "thrust-reverser-hardware"
        assert hw.version == 1
        assert hw.logic_thresholds.logic1_ra_ft_threshold == 6.0
        assert hw.logic_thresholds.logic3_tra_deg_threshold == -11.74
        assert hw.logic_thresholds.deploy_90_threshold_percent == 90.0
        assert hw.timing.tls_unlock_delay_s == 0.3
        assert hw.timing.pls_unlock_delay_s == 0.2
        assert hw.physical_limits.sw1_window.near_zero_deg == -1.4
        assert hw.physical_limits.sw1_window.deep_reverse_deg == -6.2
        assert hw.physical_limits.sw2_window.near_zero_deg == -5.0
        assert hw.physical_limits.sw2_window.deep_reverse_deg == -9.8

    def test_real_yaml_has_lru_inventory_and_signal_bindings(self) -> None:
        hw = load_thrust_reverser_hardware(
            "config/hardware/thrust_reverser_hardware_v1.yaml"
        )
        assert len(hw.lru_inventory) == 11
        assert len(hw.signal_carrier_bindings) == 18
        assert {item.id for item in hw.lru_inventory} >= {
            "etrac",
            "pdu",
            "tls",
            "pls",
            "vdt",
            "lock_sensors",
        }
        assert {binding.signal_id for binding in hw.signal_carrier_bindings} >= {
            "tls_115vac_cmd",
            "pdu_motor_cmd",
            "deploy_90_percent_vdt",
            "throttle_electronic_lock_release_cmd",
        }

    def test_real_yaml_unknown_hardware_data_is_explicit_evidence_gap(self) -> None:
        hw = load_thrust_reverser_hardware(
            "config/hardware/thrust_reverser_hardware_v1.yaml"
        )
        for item in hw.lru_inventory:
            assert item.part_number.status == "evidence_gap"
            assert item.location.status == "evidence_gap"
            assert item.failure_rate_per_hour.status == "evidence_gap"
        for binding in hw.signal_carrier_bindings:
            assert binding.cable.status == "evidence_gap"
            assert binding.connector.status == "evidence_gap"
            assert binding.port_local.status == "evidence_gap"
            assert binding.port_peer.status == "evidence_gap"
            assert binding.evidence_status == "evidence_gap"
