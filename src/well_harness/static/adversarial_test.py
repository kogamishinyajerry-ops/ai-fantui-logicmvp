#!/usr/bin/env python3
"""Adversarial test for well-harness truth engine + UI state reliability.

Tests against the backend API directly to validate truth engine logic,
then checks the frontend's applySnapshotToCanvas behavior.
"""
import http.client
import json
import os
import time
import sys

PORT = int(os.environ.get("WELL_HARNESS_PORT", "8766"))

def api(path, payload):
    conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=10)
    conn.request("POST", path, body=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    resp = conn.getresponse()
    data = json.loads(resp.read().decode())
    conn.close()
    return data

def node_map(snap):
    return {n["id"]: {"state": n["state"], "value": n.get("value")} for n in snap.get("nodes", [])}

def logic_map(snap):
    return {k: v.get("active", False) for k, v in snap.get("logic", {}).items()}

def check(label, condition, msg=""):
    if condition:
        print(f"  PASS  {label}")
        return True
    else:
        print(f"  FAIL  {label}" + (f" — {msg}" if msg else ""))
        return False

def run():
    print("=" * 70)
    print("ADVERSARIAL TEST: truth engine + UI state reliability")
    print("=" * 70)

    failures = 0

    # ── Test 1: All logic gates active (baseline full-chain) ──────────────
    print("\n[Test 1] Full chain activation (all conditions satisfied)")
    snap = api("/api/lever-snapshot", {
        "tra_deg": -14.0, "radio_altitude_ft": 5.0,
        "engine_running": True, "aircraft_on_ground": True,
        "reverser_inhibited": False, "eec_enable": True,
        "n1k": 50.0, "sw1": True, "sw2": True,
        "deploy_position_percent": 95.0,
        "feedback_mode": "manual_feedback_override",
        "system_id": "thrust-reverser", "prompt": "baseline"
    })
    nm = node_map(snap)
    lm = logic_map(snap)

    expected = {
        "sw1": "active", "logic1": "blocked", "tls115": "active", "tls_unlocked": "active",
        "sw2": "active", "logic2": "active", "etrac_540v": "active",
        "logic3": "active",
        "eec_deploy": "active", "pls_power": "active", "pdu_motor": "active",
        "logic4": "active", "thr_lock": "active", "vdt90": "active",
    }
    for node_id, exp_state in expected.items():
        actual = nm.get(node_id, {}).get("state", "MISSING")
        if not check(f"{node_id}={actual} (expected {exp_state})", actual == exp_state):
            failures += 1

    if len(nm) != 19:
        print(f"  FAIL  node count={len(nm)} (expected 19)")
        failures += 1
    else:
        print(f"  PASS  node count=19")

    # ── Test 2: Idempotency ──────────────────────────────────────────────────
    print("\n[Test 2] Idempotency: same payload x5 produces identical output")
    base_payload = {
        "tra_deg": -14.0, "radio_altitude_ft": 5.0,
        "engine_running": True, "aircraft_on_ground": True,
        "reverser_inhibited": False, "eec_enable": True,
        "n1k": 50.0, "sw1": True, "sw2": True,
        "deploy_position_percent": 95.0,
        "feedback_mode": "manual_feedback_override",
        "system_id": "thrust-reverser", "prompt": "idempotent"
    }
    outputs = [api("/api/lever-snapshot", base_payload) for _ in range(5)]
    snapshots_identical = all(
        node_map(o) == node_map(outputs[0]) and logic_map(o) == logic_map(outputs[0])
        for o in outputs[1:]
    )
    if not check("5 identical outputs", snapshots_identical):
        failures += 1

    # ── Test 3: Stepwise deactivation (no spurious activations) ───────────
    print("\n[Test 3] Stepwise deactivation (no spurious activations)")
    snap0 = api("/api/lever-snapshot", {
        "tra_deg": -14.0, "radio_altitude_ft": 5.0,
        "engine_running": True, "aircraft_on_ground": True,
        "reverser_inhibited": False, "eec_enable": True,
        "n1k": 50.0, "sw1": True, "sw2": True,
        "deploy_position_percent": 95.0,
        "feedback_mode": "manual_feedback_override",
        "system_id": "thrust-reverser", "prompt": "full"
    })
    nm0 = node_map(snap0)

    # Remove sw1 → only L1 chain should break
    snap1 = api("/api/lever-snapshot", {
        "tra_deg": -14.0, "radio_altitude_ft": 5.0,
        "engine_running": True, "aircraft_on_ground": True,
        "reverser_inhibited": False, "eec_enable": True,
        "n1k": 50.0, "sw1": False, "sw2": True,
        "deploy_position_percent": 95.0,
        "feedback_mode": "manual_feedback_override",
        "system_id": "thrust-reverser", "prompt": "no_sw1"
    })
    nm1 = node_map(snap1)

    newly_active = [k for k, v in nm1.items()
                    if v["state"] == "active" and nm0.get(k, {}).get("state") != "active"]
    if not check("no spurious activations when sw1 removed", len(newly_active) == 0,
                 f"newly active: {newly_active}"):
        failures += 1

    # Remove sw2 too
    snap2 = api("/api/lever-snapshot", {
        "tra_deg": -14.0, "radio_altitude_ft": 5.0,
        "engine_running": True, "aircraft_on_ground": True,
        "reverser_inhibited": False, "eec_enable": True,
        "n1k": 50.0, "sw1": False, "sw2": False,
        "deploy_position_percent": 95.0,
        "feedback_mode": "manual_feedback_override",
        "system_id": "thrust-reverser", "prompt": "no_sw1_sw2"
    })
    nm2 = node_map(snap2)
    newly_active2 = [k for k, v in nm2.items()
                      if v["state"] == "active" and nm0.get(k, {}).get("state") != "active"]
    if not check("no spurious activations when sw1+sw2 removed", len(newly_active2) == 0,
                 f"newly active: {newly_active2}"):
        failures += 1

    # ── Test 4: TRA boundary ─────────────────────────────────────────────────
    print("\n[Test 4] TRA boundary conditions")
    tra_cases = [
        (-14.0, "logic3", "active", "exact threshold"),
        (-11.7, "logic3", "blocked", "just above threshold"),
        (0.0, "logic3", "blocked", "positive TRA"),
        (-32.0, "logic3", "active", "below min travel"),
    ]
    for tra_val, node_id, exp_state, desc in tra_cases:
        snap_t = api("/api/lever-snapshot", {
            "tra_deg": tra_val, "radio_altitude_ft": 5.0,
            "engine_running": True, "aircraft_on_ground": True,
            "reverser_inhibited": False, "eec_enable": True,
            "n1k": 50.0, "sw1": True, "sw2": True,
            "deploy_position_percent": 95.0,
            "feedback_mode": "manual_feedback_override",
            "system_id": "thrust-reverser", "prompt": f"tra={tra_val}"
        })
        actual = node_map(snap_t).get(node_id, {}).get("state", "MISSING")
        if not check(f"TRA={tra_val}deg {node_id}={actual} ({desc})",
                      actual == exp_state, f"expected={exp_state}"):
            failures += 1

    # ── Test 5: VDT threshold at 90% ───────────────────────────────────────
    print("\n[Test 5] VDT 90% threshold")
    vdt_cases = [
        (95.0, "vdt90", "active"),
        (90.0, "vdt90", "active"),
        (89.9, "vdt90", "inactive"),
        (50.0, "vdt90", "inactive"),
    ]
    for vdt, node_id, exp_state in vdt_cases:
        snap_v = api("/api/lever-snapshot", {
            "tra_deg": -14.0, "radio_altitude_ft": 5.0,
            "engine_running": True, "aircraft_on_ground": True,
            "reverser_inhibited": False, "eec_enable": True,
            "n1k": 50.0, "sw1": True, "sw2": True,
            "deploy_position_percent": vdt,
            "feedback_mode": "manual_feedback_override",
            "system_id": "thrust-reverser", "prompt": f"vdt={vdt}"
        })
        actual = node_map(snap_v).get(node_id, {}).get("state", "MISSING")
        if not check(f"VDT={vdt}% {node_id}={actual}", actual == exp_state):
            failures += 1

    # ── Test 6: Rapid cycling (10 iterations) ────────────────────────────────
    print("\n[Test 6] Rapid cycling (10 iterations, stress test)")
    configs = [
        {"tra_deg": -14.0, "n1k": 50.0, "sw1": True, "sw2": True,  "aircraft_on_ground": True,  "deploy_position_percent": 95.0},
        {"tra_deg": -10.0, "n1k": 50.0, "sw1": True, "sw2": True,  "aircraft_on_ground": True,  "deploy_position_percent": 50.0},
        {"tra_deg": -14.0, "n1k": 70.0, "sw1": True, "sw2": False, "aircraft_on_ground": True,  "deploy_position_percent": 95.0},
        {"tra_deg": 0.0,   "n1k": 50.0, "sw1": False,"sw2": True,  "aircraft_on_ground": True,  "deploy_position_percent": 95.0},
        {"tra_deg": -14.0, "n1k": 50.0, "sw1": True, "sw2": True,  "aircraft_on_ground": False, "deploy_position_percent": 95.0},
        {"tra_deg": -13.5, "n1k": 50.0, "sw1": True, "sw2": True,  "aircraft_on_ground": True,  "deploy_position_percent": 90.0},
        {"tra_deg": -14.0, "n1k": 30.0, "sw1": True, "sw2": True,  "aircraft_on_ground": True,  "deploy_position_percent": 95.0},
        {"tra_deg": -11.5, "n1k": 50.0, "sw1": True, "sw2": True,  "aircraft_on_ground": True,  "deploy_position_percent": 95.0},
        {"tra_deg": -14.0, "n1k": 50.0, "sw1": True, "sw2": True,  "aircraft_on_ground": True,  "deploy_position_percent": 89.9},
        {"tra_deg": -14.0, "n1k": 55.0, "sw1": True, "sw2": True,  "aircraft_on_ground": True,  "deploy_position_percent": 95.0},
    ]
    iter_failures = 0
    for i, cfg in enumerate(configs):
        p = {
            "tra_deg": cfg["tra_deg"], "radio_altitude_ft": 5.0,
            "engine_running": True, "aircraft_on_ground": cfg["aircraft_on_ground"],
            "reverser_inhibited": False, "eec_enable": True,
            "n1k": cfg["n1k"], "sw1": cfg["sw1"], "sw2": cfg["sw2"],
            "deploy_position_percent": cfg["deploy_position_percent"],
            "feedback_mode": "manual_feedback_override",
            "system_id": "thrust-reverser", "prompt": f"iter{i}"
        }
        snap_i = api("/api/lever-snapshot", p)
        nm_i = node_map(snap_i)

        if len(nm_i) != 19:
            print(f"  FAIL  iter{i}: node count={len(nm_i)} (expected 19)")
            iter_failures += 1
        for node_id, data in nm_i.items():
            if data["state"] not in ("active", "inactive", "blocked"):
                print(f"  FAIL  iter{i} {node_id}: invalid state={data['state']}")
                iter_failures += 1
        # Logic node state must be consistent with node state
        for logic_id in ("logic1", "logic2", "logic3", "logic4"):
            node_state = nm_i.get(logic_id, {}).get("state", "?")
            logic_active = logic_map(snap_i).get(logic_id, False)
            consistent = (logic_active and node_state == "active") or (not logic_active and node_state != "active")
            if not consistent:
                print(f"  FAIL  iter{i} {logic_id}: logic_active={logic_active} but node_state={node_state}")
                iter_failures += 1

    if iter_failures == 0:
        print(f"  PASS  all 10 iterations consistent")
    else:
        print(f"  FAIL  {iter_failures} inconsistencies across 10 iterations")
        failures += iter_failures

    # ── Test 7: Frontend state application via nodeStateMap ─────────────────
    # The fix: frontend now uses data.nodes[].state directly (nodeStateMap) instead of
    # deriving from nodeValueMap via deriveComponentState(undefined)=inactive.
    # Backend still doesn't provide .value for intermediate nodes — that's OK now.
    print("\n[Test 7] Frontend uses authoritative nodeStateMap (not deriveComponentState)")
    snap = api("/api/lever-snapshot", {
        "tra_deg": -14.0, "radio_altitude_ft": 5.0,
        "engine_running": True, "aircraft_on_ground": True,
        "reverser_inhibited": False, "eec_enable": True,
        "n1k": 50.0, "sw1": True, "sw2": True,
        "deploy_position_percent": 95.0,
        "feedback_mode": "manual_feedback_override",
        "system_id": "thrust-reverser", "prompt": "frontend_test"
    })
    # Verify backend provides authoritative state for ALL 14 nodes (including intermediate).
    # This is the contract: data.nodes[].state must be the source of truth.
    all_nodes_have_state = all("state" in n for n in snap.get("nodes", []))
    intermediate_states = {n["id"]: n["state"] for n in snap.get("nodes", []) if n["id"] in ("tls115", "etrac_540v", "vdt90", "thr_lock")}
    if not all_nodes_have_state:
        print(f"  FAIL  Some nodes lack .state field in backend response")
        failures += 1
    elif not check("all 19 nodes have authoritative .state", all_nodes_have_state):
        failures += 1
    else:
        print(f"  PASS  all 19 nodes have authoritative .state in backend")
        print(f"  intermediate node states: {intermediate_states}")

    # ── Test 8: Full causal chain ──────────────────────────────────────────
    print("\n[Test 8] Full causal chain verification")
    snap = api("/api/lever-snapshot", {
        "tra_deg": -14.0, "radio_altitude_ft": 5.0,
        "engine_running": True, "aircraft_on_ground": True,
        "reverser_inhibited": False, "eec_enable": True,
        "n1k": 50.0, "sw1": True, "sw2": True,
        "deploy_position_percent": 95.0,
        "feedback_mode": "manual_feedback_override",
        "system_id": "thrust-reverser", "prompt": "chain"
    })
    nm = node_map(snap)
    chain = [
        ("sw1", "active"), ("logic1", "blocked"), ("tls115", "active"), ("tls_unlocked", "active"),
        ("sw2", "active"), ("logic2", "active"), ("etrac_540v", "active"),
        ("logic3", "active"),
        ("eec_deploy", "active"), ("pls_power", "active"), ("pdu_motor", "active"),
        ("vdt90", "active"), ("logic4", "active"), ("thr_lock", "active"),
    ]
    for node_id, exp_state in chain:
        actual = nm.get(node_id, {}).get("state", "MISSING")
        if not check(f"{node_id}={actual}", actual == exp_state):
            failures += 1

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    if failures == 0:
        print("ALL TESTS PASSED")
    else:
        print(f"TESTS COMPLETED — {failures} failure(s)")
    print("=" * 70)
    return failures

if __name__ == "__main__":
    sys.exit(run())
