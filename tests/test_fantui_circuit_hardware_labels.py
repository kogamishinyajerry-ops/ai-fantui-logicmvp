from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FANTUI_CIRCUIT = REPO_ROOT / "src" / "well_harness" / "static" / "fantui_circuit.html"


def _html() -> str:
    return FANTUI_CIRCUIT.read_text(encoding="utf-8")


def test_fantui_circuit_has_hardware_coupling_card_and_schema_endpoint() -> None:
    html = _html()

    assert 'data-hardware-coupling-card="thrust-reverser"' in html
    assert 'data-hardware-schema-endpoint="/api/hardware/schema?system_id=thrust-reverser"' in html
    assert "connector/cable/port: 未录入" in html
    assert "<code>evidence_gap</code>" in html


def test_fantui_circuit_labels_core_lru_inventory_items() -> None:
    html = _html()

    for lru_id in ("etrac", "tls", "pdu", "pls", "vdt", "lock_sensors"):
        assert f'data-lru-id="{lru_id}"' in html


def test_fantui_circuit_signal_nodes_carry_hardware_metadata_only() -> None:
    html = _html()

    expected_signal_attrs = {
        "tls_115vac_cmd": 'data-source-lru-id="etrac" data-lru-id="tls"',
        "etrac_540vdc_cmd": 'data-source-lru-id="etrac" data-lru-id="pdu"',
        "pls_power_cmd": 'data-source-lru-id="etrac" data-lru-id="pls"',
        "pdu_motor_cmd": 'data-source-lru-id="etrac" data-lru-id="pdu"',
        "deploy_90_percent_vdt": 'data-lru-id="vdt"',
        "tls_unlocked_ls": 'data-lru-id="lock_sensors"',
    }
    for signal_id, attrs in expected_signal_attrs.items():
        assert f'data-signal-id="{signal_id}"' in html
        assert attrs in html

    assert 'data-hardware-detail="cable/connector/port:evidence_gap"' in html
