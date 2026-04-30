# Editable Hardware Interface Design v1

`editable_hardware_interface_design_v1` is the sandbox-only hardware/interface
design model for Workbench v4. It records candidate LRU, cable, connector,
port, pin, signal binding, and evidence-gap data so the workbench can review
interface design without changing controller truth.

Schema artifact:
`docs/json_schema/editable_hardware_interface_design_v1.schema.json`

Runtime module:
`src/well_harness/editable_hardware_interface_design.py`

## Boundary

- `candidate_state` must be `sandbox_candidate`.
- `truth_level_impact`, `dal_pssa_impact`, and `runtime_truth_effect` must be
  `none`.
- `controller_truth_modified` and `boundaries.certified_truth_modified` must be
  `false`.
- `boundaries.runtime_scope` must be `sandbox_only`.
- Hardware/interface fields are review evidence only. They do not participate
  in `controller.py`, adapter truth, DAL/PSSA, or certified baseline semantics.

## Record Types

- `lrus`: candidate hardware units with evidence status and optional part,
  location, quantity, and failure-rate fields.
- `cables`: candidate cable records that connect two LRUs or explicitly mark
  unknown endpoints as `evidence_gap`.
- `connectors`: candidate connector records attached to LRUs.
- `ports`: candidate logical/electrical ports attached to connectors.
- `pins`: candidate pin records attached to connectors and optionally mapped to
  ports.
- `bindings`: candidate signal-carrier bindings between source/target ports and
  cables. `truth_effect` must always be `none`.
- `evidence_gaps`: explicit missing-data records with subject, field reference,
  severity, impact, proposed fill, and source reference.

## Reference Integrity

The Python validator enforces cross-record invariants that JSON Schema cannot:

- IDs are unique within each collection and across the whole design payload.
- Cable LRU endpoints must resolve to `lrus[].id` unless explicitly set to
  `evidence_gap` with `evidence_status: evidence_gap`.
- Connector `lru_id` must resolve to an LRU unless explicitly marked as an
  evidence gap.
- Port `connector_id` must resolve to a connector unless explicitly marked as an
  evidence gap.
- Pin `connector_id` and `port_id` must resolve, and resolved pins must belong
  to the same connector as their linked port.
- Binding source/target ports and cable must resolve unless explicitly marked
  as evidence gaps.
- Binding `truth_effect` must be `none`.

## Minimal Example

```json
{
  "$schema": "https://well-harness.local/json_schema/editable_hardware_interface_design_v1.schema.json",
  "kind": "well-harness-editable-hardware-interface-design",
  "version": 1,
  "design_id": "thrust-reverser-interface-draft-v1",
  "system_id": "thrust-reverser",
  "candidate_state": "sandbox_candidate",
  "truth_level_impact": "none",
  "dal_pssa_impact": "none",
  "controller_truth_modified": false,
  "runtime_truth_effect": "none",
  "lrus": [
    {
      "id": "TR-LRU-001",
      "display_name": "TR Control Electronics",
      "quantity_per_engine": 1,
      "part_number": null,
      "location": null,
      "failure_rate_per_hour": null,
      "evidence_status": "evidence_gap",
      "source_ref": "workbench.hardware_interface_design"
    }
  ],
  "cables": [],
  "connectors": [],
  "ports": [],
  "pins": [],
  "bindings": [],
  "evidence_gaps": [
    {
      "id": "gap:TR-LRU-001:part_number",
      "subject_id": "TR-LRU-001",
      "field_ref": "lrus.TR-LRU-001.part_number",
      "severity": "medium",
      "impact": "part number unavailable for review packet",
      "proposed_fill": "capture from engineering BOM",
      "source_ref": "workbench.hardware_interface_design"
    }
  ],
  "evidence_metadata": {
    "sample_pack_role": "hardware_interface_design",
    "source_refs": [
      "workbench.hardware_interface_design"
    ]
  },
  "boundaries": {
    "runtime_scope": "sandbox_only",
    "hardware_truth_effect": "none",
    "certified_truth_modified": false,
    "dal_pssa_impact": "none"
  }
}
```
