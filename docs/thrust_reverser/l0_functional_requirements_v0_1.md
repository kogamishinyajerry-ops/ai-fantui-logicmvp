# Thrust-Reverser L0 Functional Requirements v0.1 Draft

Status: non-authoritative draft  
Scope: M3 preparation only  
Truth-level impact: none  
DAL/PSSA: TBD / not assigned

This draft does not change controller.py, does not certify DAL, does not promote truth-level, and does not supersede docs/thrust_reverser/requirements_supplement.md.
It is a functional framing layer for later review and trace planning.

## Draft Requirements

### REQ-L0-001 Reverse Thrust Function

- Level: L0
- Authority: non-authoritative draft
- DAL/PSSA: TBD / not assigned
- Trace placeholders: L1=TBD, L2=TBD, L3=TBD, L4=TBD

The thrust-reverser function should provide commanded reverse thrust only through the approved thrust-reverser control path and only when the modeled aircraft/system state permits reverse-thrust operation.

### REQ-L0-002 Safe Enablement

- Level: L0
- Authority: non-authoritative draft
- DAL/PSSA: TBD / not assigned
- Trace placeholders: L1=TBD, L2=TBD, L3=TBD, L4=TBD

The thrust-reverser function should require safe enablement conditions before deploy or unlock behavior is considered available, including positive confirmation of relevant aircraft state and inhibit conditions.

### REQ-L0-003 State and Condition Gating

- Level: L0
- Authority: non-authoritative draft
- DAL/PSSA: TBD / not assigned
- Trace placeholders: L1=TBD, L2=TBD, L3=TBD, L4=TBD

The thrust-reverser function should gate each high-level behavior by explicit state and condition gating so that deploy, lock, inhibit, and permissive states remain explainable and traceable.

### REQ-L0-004 Fault Isolation

- Level: L0
- Authority: non-authoritative draft
- DAL/PSSA: TBD / not assigned
- Trace placeholders: L1=TBD, L2=TBD, L3=TBD, L4=TBD

The thrust-reverser function should support fault isolation evidence that distinguishes command-side, sensor-side, actuator-side, and hardware-coupling evidence gaps without inventing certified cause truth.

### REQ-L0-005 Response-Time Placeholder

- Level: L0
- Authority: non-authoritative draft
- DAL/PSSA: TBD / not assigned
- Trace placeholders: L1=TBD, L2=TBD, L3=TBD, L4=TBD

The thrust-reverser function should reserve a response-time placeholder for future timing requirements, while explicitly marking timing values as TBD until Kogami/PSSA/DAL review provides authority.

## Trace Planning Notes

- L1 decomposition: TBD after Kogami/Charter review.
- L2 signal mapping: TBD; do not infer certified signal timing from current controller behavior.
- L3 hardware coupling: TBD; may reference thrust-reverser hardware metadata only as evidence, not truth promotion.
- L4 verification: TBD; future tests must distinguish unit, bench, simulation, and certification-facing evidence.
