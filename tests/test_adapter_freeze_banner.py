"""
P35-03 · Adapter Freeze Banner Regression Guard

Ensures the FROZEN banner added in P35-02 is present in all 7 files covering
the 3 demonstrative adapters (bleed_air / efds / landing_gear). If the banner
is deleted or the key warning text is stripped, this test fails immediately.

Invariants (per docs/provenance/adapter_truth_levels.md):
- 3 adapter module docstrings contain "FROZEN" + "no authoritative upstream spec"
- 2 intake packet module docstrings contain "FROZEN" + "no authoritative upstream spec"
- 2 hardware YAML heads contain "FROZEN" + "no authoritative upstream spec"
- All 7 files point at docs/provenance/adapter_truth_levels.md

Scope note: thrust_reverser (controller.py) and c919_etras (adapter.py) are NOT
checked here. thrust_reverser is pending P36β certified-upgrade (will get its own
anchoring via docx); c919_etras is already certified and has its own matrix under
docs/c919_etras/.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

FROZEN_KEYWORDS = ("FROZEN", "no authoritative upstream spec")
REGISTRY_POINTER = "docs/provenance/adapter_truth_levels.md"

DEMONSTRATIVE_ADAPTER_DOCSTRING_FILES = (
    "src/well_harness/adapters/bleed_air_adapter.py",
    "src/well_harness/adapters/efds_adapter.py",
    "src/well_harness/adapters/landing_gear_adapter.py",
)

DEMONSTRATIVE_INTAKE_DOCSTRING_FILES = (
    "src/well_harness/adapters/bleed_air_intake_packet.py",
    "src/well_harness/adapters/landing_gear_intake_packet.py",
)

DEMONSTRATIVE_HARDWARE_YAML_FILES = (
    "config/hardware/bleed_air_hardware_v1.yaml",
    "config/hardware/landing_gear_hardware_v1.yaml",
)

ALL_FROZEN_FILES = (
    DEMONSTRATIVE_ADAPTER_DOCSTRING_FILES
    + DEMONSTRATIVE_INTAKE_DOCSTRING_FILES
    + DEMONSTRATIVE_HARDWARE_YAML_FILES
)


def _read(relpath: str) -> str:
    return (REPO_ROOT / relpath).read_text(encoding="utf-8")


@pytest.mark.parametrize("relpath", ALL_FROZEN_FILES)
def test_frozen_keywords_present(relpath: str) -> None:
    content = _read(relpath)
    for kw in FROZEN_KEYWORDS:
        assert kw in content, (
            f"{relpath} missing FROZEN banner keyword {kw!r}. "
            f"If this banner was removed, restore it or update "
            f"docs/provenance/adapter_truth_levels.md to reclassify the adapter."
        )


@pytest.mark.parametrize("relpath", ALL_FROZEN_FILES)
def test_registry_pointer_present(relpath: str) -> None:
    content = _read(relpath)
    assert REGISTRY_POINTER in content, (
        f"{relpath} missing registry pointer {REGISTRY_POINTER!r}. "
        f"The banner must always cite the registry for audit traceability."
    )


def test_registry_file_exists_and_lists_frozen_systems() -> None:
    registry_path = REPO_ROOT / REGISTRY_POINTER
    assert registry_path.exists(), (
        f"Registry file {REGISTRY_POINTER} is missing; "
        f"banner in 7 files points at it but target is gone."
    )
    registry = registry_path.read_text(encoding="utf-8")
    for system_id in ("bleed-air-valve", "emergency_flare_deployment_system", "minimal_landing_gear_extension"):
        assert system_id in registry, (
            f"Registry {REGISTRY_POINTER} missing row for {system_id!r}. "
            f"Every demonstrative adapter with a FROZEN banner must appear in the registry."
        )
