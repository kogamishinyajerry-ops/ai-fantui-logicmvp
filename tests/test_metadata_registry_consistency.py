"""P42-05 · Bidirectional registry ↔ runtime ↔ markdown consistency guard.

Resolves Codex Counter C: three sources of truth (runtime + yaml + markdown
table) must stay aligned; this test enforces the alignment so silent
drift cannot land on main.

Three layers cross-checked (yaml is the machine SoT):

  1. yaml entries            (docs/provenance/adapter_truth_levels.yaml)
  2. runtime metadata        (dynamic importlib on metadata_module, scan
                              for ControllerTruthMetadata instances)
  3. markdown registry table (docs/provenance/adapter_truth_levels.md)

Forward (yaml → runtime):
  - Every yaml entry must resolve to a live ControllerTruthMetadata
    instance at module-level on the declared module.
  - The instance's (adapter_id, truth_level, status) must match the yaml.

Reverse (runtime → yaml):
  - The set of ControllerTruthMetadata instances discovered in the
    well_harness namespace must equal the set of metadata_const values
    in the yaml (no ghost runtime instances without a yaml row, no
    ghost yaml rows without a runtime instance).
  - Every discovered production instance MUST declare both truth_level
    and status (non-None); None governance is a P42 regression.

Markdown sanity (yaml → md table):
  - Every yaml entry's system_id must appear as a literal substring in
    docs/provenance/adapter_truth_levels.md.
  - The registry table in the markdown must contain exactly the same
    number of data rows as yaml entries.
"""
from __future__ import annotations

import importlib
import re
import sys
import unittest
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "src"))

from well_harness.controller_adapter import ControllerTruthMetadata  # noqa: E402


YAML_PATH = _REPO_ROOT / "docs/provenance/adapter_truth_levels.yaml"
MARKDOWN_PATH = _REPO_ROOT / "docs/provenance/adapter_truth_levels.md"

# Modules known to carry production ControllerTruthMetadata instances. The
# yaml lists these under entries[].metadata_module — this tuple mirrors the
# yaml and acts as a reverse-direction check (any module added here but not
# declared in yaml will fail the bidir test).
KNOWN_RUNTIME_MODULES = (
    "well_harness.controller_adapter",
    "well_harness.adapters.bleed_air_adapter",
    "well_harness.adapters.efds_adapter",
    "well_harness.adapters.landing_gear_adapter",
    "well_harness.adapters.c919_etras_adapter",
)

VALID_TRUTH_LEVELS = frozenset({"demonstrative", "certified", "placeholder"})
VALID_STATUSES = frozenset({"In use", "Frozen", "Upgrade pending", "Upgrade in progress"})


def _load_yaml_entries() -> list[dict]:
    try:
        import yaml  # type: ignore
    except ImportError as exc:  # pragma: no cover — PyYAML ships in dev extras
        raise unittest.SkipTest(f"PyYAML required for registry consistency: {exc}") from exc
    data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict) and "entries" in data, f"yaml SoT malformed: {YAML_PATH}"
    return list(data["entries"])


def _discover_runtime_metadata() -> dict[str, tuple[str, ControllerTruthMetadata]]:
    """Return {metadata_const_name: (module_name, instance)} for every
    module-level ControllerTruthMetadata found across KNOWN_RUNTIME_MODULES."""
    found: dict[str, tuple[str, ControllerTruthMetadata]] = {}
    for module_name in KNOWN_RUNTIME_MODULES:
        module = importlib.import_module(module_name)
        for attr_name in dir(module):
            if attr_name.startswith("_"):
                continue
            value = getattr(module, attr_name)
            if isinstance(value, ControllerTruthMetadata):
                if attr_name in found:
                    existing_module = found[attr_name][0]
                    raise AssertionError(
                        f"ControllerTruthMetadata const {attr_name!r} defined in both "
                        f"{existing_module!r} and {module_name!r}; const names must be unique."
                    )
                found[attr_name] = (module_name, value)
    return found


class RegistryYamlShapeTests(unittest.TestCase):
    """Basic yaml SoT schema sanity before running cross-layer checks."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.entries = _load_yaml_entries()

    def test_yaml_has_at_least_one_entry(self) -> None:
        self.assertGreater(len(self.entries), 0)

    def test_every_entry_declares_required_fields(self) -> None:
        required = {"system_id", "adapter_id", "metadata_const", "metadata_module", "truth_level", "status"}
        for idx, entry in enumerate(self.entries):
            missing = required - set(entry.keys())
            self.assertFalse(
                missing,
                f"yaml entry #{idx} ({entry.get('system_id', '<unknown>')}) missing fields: {missing}",
            )

    def test_every_entry_uses_valid_enum_values(self) -> None:
        for entry in self.entries:
            self.assertIn(entry["truth_level"], VALID_TRUTH_LEVELS,
                          f"yaml entry {entry['system_id']!r} has invalid truth_level={entry['truth_level']!r}")
            self.assertIn(entry["status"], VALID_STATUSES,
                          f"yaml entry {entry['system_id']!r} has invalid status={entry['status']!r}")

    def test_system_ids_are_unique(self) -> None:
        ids = [e["system_id"] for e in self.entries]
        self.assertEqual(len(ids), len(set(ids)),
                         f"duplicate system_id in yaml: {ids}")

    def test_metadata_consts_are_unique(self) -> None:
        consts = [e["metadata_const"] for e in self.entries]
        self.assertEqual(len(consts), len(set(consts)),
                         f"duplicate metadata_const in yaml: {consts}")


class YamlRuntimeBidirectionalTests(unittest.TestCase):
    """Each yaml entry resolves to a runtime instance with matching fields,
    and every runtime instance is declared in yaml."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.entries = _load_yaml_entries()
        cls.runtime = _discover_runtime_metadata()

    def test_yaml_modules_match_known_runtime_modules(self) -> None:
        yaml_modules = {e["metadata_module"] for e in self.entries}
        self.assertEqual(
            yaml_modules, set(KNOWN_RUNTIME_MODULES),
            "yaml metadata_module set must equal the test's KNOWN_RUNTIME_MODULES allowlist; "
            "if you added a new adapter, update both yaml AND KNOWN_RUNTIME_MODULES in this test.",
        )

    def test_every_yaml_entry_has_a_runtime_instance(self) -> None:
        for entry in self.entries:
            const_name = entry["metadata_const"]
            module_name = entry["metadata_module"]
            self.assertIn(
                const_name, self.runtime,
                f"yaml entry {entry['system_id']!r} references "
                f"{module_name}.{const_name} but no matching ControllerTruthMetadata found at runtime.",
            )
            resolved_module, instance = self.runtime[const_name]
            self.assertEqual(
                resolved_module, module_name,
                f"yaml entry {entry['system_id']!r}: metadata_module is {module_name!r} but "
                f"{const_name!r} was actually discovered in {resolved_module!r}.",
            )
            self.assertEqual(
                instance.adapter_id, entry["adapter_id"],
                f"adapter_id mismatch for {entry['system_id']!r}: "
                f"yaml={entry['adapter_id']!r} runtime={instance.adapter_id!r}",
            )
            self.assertEqual(
                instance.truth_level, entry["truth_level"],
                f"truth_level mismatch for {entry['system_id']!r}: "
                f"yaml={entry['truth_level']!r} runtime={instance.truth_level!r}",
            )
            self.assertEqual(
                instance.status, entry["status"],
                f"status mismatch for {entry['system_id']!r}: "
                f"yaml={entry['status']!r} runtime={instance.status!r}",
            )

    def test_every_runtime_instance_has_a_yaml_entry(self) -> None:
        yaml_consts = {e["metadata_const"] for e in self.entries}
        runtime_consts = set(self.runtime.keys())
        ghost_runtime = runtime_consts - yaml_consts
        self.assertFalse(
            ghost_runtime,
            f"runtime ControllerTruthMetadata instances missing from yaml SoT: {ghost_runtime}. "
            f"Every production metadata const MUST appear in docs/provenance/adapter_truth_levels.yaml.",
        )
        ghost_yaml = yaml_consts - runtime_consts
        self.assertFalse(
            ghost_yaml,
            f"yaml entries without a live runtime instance: {ghost_yaml}. "
            f"Either restore the metadata const or remove the yaml entry.",
        )


class ProductionInstancesDeclareGovernanceTests(unittest.TestCase):
    """No production metadata is allowed to rely on the None-sentinel defaults."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime = _discover_runtime_metadata()

    def test_no_production_instance_has_none_truth_level(self) -> None:
        offenders = [
            f"{module}.{name}"
            for name, (module, instance) in self.runtime.items()
            if instance.truth_level is None
        ]
        self.assertFalse(
            offenders,
            f"Production ControllerTruthMetadata instances with truth_level=None: {offenders}. "
            f"None is reserved for pre-P42/unclassified migration state and test fixtures.",
        )

    def test_no_production_instance_has_none_status(self) -> None:
        offenders = [
            f"{module}.{name}"
            for name, (module, instance) in self.runtime.items()
            if instance.status is None
        ]
        self.assertFalse(
            offenders,
            f"Production ControllerTruthMetadata instances with status=None: {offenders}.",
        )


class MarkdownTableSanityTests(unittest.TestCase):
    """Markdown registry table shape mirrors yaml entries."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.entries = _load_yaml_entries()
        cls.markdown = MARKDOWN_PATH.read_text(encoding="utf-8")

    def test_every_yaml_system_id_appears_in_markdown(self) -> None:
        for entry in self.entries:
            system_id = entry["system_id"]
            self.assertIn(
                system_id, self.markdown,
                f"yaml entry system_id={system_id!r} does not appear in "
                f"{MARKDOWN_PATH.name}; sync the markdown table after editing yaml.",
            )

    def test_markdown_table_row_count_matches_yaml(self) -> None:
        # Find the registry table block: header row `| system_id | truth_level | ...` followed by
        # a separator line `|---|---|...`, then the data rows until the first non-table line.
        table_header_match = re.search(
            r"^\| system_id \| truth_level \| status \|.*$",
            self.markdown,
            re.MULTILINE,
        )
        self.assertIsNotNone(
            table_header_match,
            "Could not locate the registry table header in the markdown registry.",
        )
        start = table_header_match.end()
        # Skip the separator line that follows the header.
        tail = self.markdown[start:].lstrip("\n")
        separator, _, body = tail.partition("\n")
        self.assertTrue(separator.startswith("|---"), "Expected markdown separator row after header.")
        data_rows = []
        for line in body.splitlines():
            if not line.startswith("|"):
                break
            # Skip empty rows, but capture all non-empty pipe-started lines.
            data_rows.append(line)
        self.assertEqual(
            len(data_rows), len(self.entries),
            f"markdown registry table has {len(data_rows)} data rows but yaml has {len(self.entries)} entries. "
            f"Both must mirror each other — edit yaml first, then sync the markdown table in the same commit.",
        )


if __name__ == "__main__":
    unittest.main()
