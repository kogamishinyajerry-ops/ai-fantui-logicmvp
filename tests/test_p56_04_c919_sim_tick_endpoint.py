"""P56-04 — C919 sim ▶仿真 button starts working in the unified workbench.

User-reported bug (2026-04-28): "C919 ETRAS的仿真面板点击'仿真'也不会开始仿真,
说明载入有问题."

Root cause: c919_etras_panel/index.html POSTs to /api/tick on every
100ms tick, but demo_server.py (the unified :8002 server) only had
/api/fantui/tick (thrust-reverser specific). /api/tick returned 404
silently, so the simulation never advanced.

The C919 state machine (FSM S0..S10+SF, lock aggregator, WOW filter,
CMD2/3 timers, etc.) is fully implemented at
well_harness.adapters.c919_etras_frozen_v1.C919ReverseThrustSystem.
The standalone :9191 server (scripts/c919_etras_panel_server.py)
already exposes it; this fix mounts the same system on :8002 so the
panel works in the unified workbench.

Implementation contract:

  1. New module well_harness.c919_tick_api with:
       - parse_c919_raw_inputs(payload) -> RawInputs
       - build_c919_tick_response(outputs, system, inp) -> dict
       - handle_c919_tick(system, lock, payload, config) -> (status, dict)
       - reset_c919_system(system) -> dict
     Both servers (demo_server.py + :9191 standalone) import from
     here so the parse + response shape stay in one place.

  2. demo_server.py exposes:
       - POST /api/tick           (legacy panel uses this)
       - POST /api/c919/tick      (namespaced alias)
       - POST /api/reset          (legacy)
       - POST /api/c919/reset     (namespaced alias)

  3. Module-level _c919_system + _c919_lock so successive ticks
     accumulate state (the simulation needs continuity across the
     100ms interval ticks the panel sends).

  4. State must actually transition on input: send a payload that
     drives WOW true + TLS unlocked + valid TRA + n1k → state
     advances past S0_AIR_STOWED_LOCKED.
"""

from __future__ import annotations

import json
from http.server import HTTPServer
from threading import Thread
from urllib.request import Request, urlopen

import pytest


# ─── 1. The shared helper module exists ───


def test_c919_tick_api_module_importable() -> None:
    """The shared helpers move from scripts/c919_etras_panel_server.py
    into a proper well_harness submodule so demo_server.py can
    import them too without duplicating ~100 lines."""
    import well_harness.c919_tick_api  # noqa: F401


def test_c919_tick_api_exports_expected_helpers() -> None:
    from well_harness import c919_tick_api

    assert callable(getattr(c919_tick_api, "parse_c919_raw_inputs", None)), (
        "parse_c919_raw_inputs(payload) must be exported"
    )
    assert callable(getattr(c919_tick_api, "build_c919_tick_response", None)), (
        "build_c919_tick_response(outputs, system, inp) must be exported"
    )
    assert callable(getattr(c919_tick_api, "handle_c919_tick", None)), (
        "handle_c919_tick(system, lock, payload, config) must be exported"
    )


# ─── 2. parse_c919_raw_inputs honors the panel's POST schema ───


def test_parse_c919_raw_inputs_with_minimal_payload() -> None:
    """An empty payload yields a defaulted RawInputs (all booleans
    False, all numerics 0, locks all-locked) so a reset state is
    safe to tick."""
    from well_harness import c919_tick_api

    inp = c919_tick_api.parse_c919_raw_inputs({})
    assert inp.lgcu1_mlg_wow is False
    assert inp.tra_deg == 0.0
    assert inp.locks.tls_locked is True
    assert inp.locks.tls_unlocked is False


def test_parse_c919_raw_inputs_propagates_lock_overrides() -> None:
    from well_harness import c919_tick_api

    payload = {
        "lgcu1_mlg_wow": True,
        "lgcu2_mlg_wow": True,
        "engine_running": True,
        "atltla": True,
        "tra_deg": -28.0,
        "n1k_pct": 60.0,
        "locks": {
            "tls_locked": False,
            "tls_unlocked": True,
        },
    }
    inp = c919_tick_api.parse_c919_raw_inputs(payload)
    assert inp.lgcu1_mlg_wow is True
    assert inp.tra_deg == pytest.approx(-28.0)
    assert inp.n1k_pct == pytest.approx(60.0)
    assert inp.locks.tls_locked is False
    assert inp.locks.tls_unlocked is True


# ─── 3. build_c919_tick_response shape matches the panel's UI ───


def test_build_response_has_state_derived_outputs_locks() -> None:
    """The C919 panel JS reads `data.state`, `data.derived.*`,
    `data.outputs.*`, `data.locks.*` — these top-level shapes
    must be present."""
    from well_harness import c919_tick_api
    from well_harness.adapters.c919_etras_frozen_v1 import (
        C919ReverseThrustSystem,
        FrozenConfig,
        TelemetryLogger,
    )

    config = FrozenConfig()
    system = C919ReverseThrustSystem(config=config, logger=TelemetryLogger())
    inp = c919_tick_api.parse_c919_raw_inputs({})
    out = system.tick(inp, config.step_s)
    resp = c919_tick_api.build_c919_tick_response(out, system, inp)
    assert "state" in resp
    assert "derived" in resp
    assert "outputs" in resp
    assert "locks" in resp
    assert "t_s" in resp
    # Derived must contain the keys the panel surfaces.
    derived = resp["derived"]
    for key in [
        "selected_mlg_wow",
        "tr_wow",
        "unlock_confirmed",
        "tr_stowed_and_locked",
        "cmd2_timer_s",
    ]:
        assert key in derived, f"derived missing {key}"


# ─── 4. demo_server.py exposes /api/tick + /api/reset endpoints ───


@pytest.fixture
def demo_server_url():
    """Spin up the unified demo_server on a random port; tear down
    after the test. Uses 127.0.0.1 to avoid hitting any running
    instance on :8002."""
    from well_harness.demo_server import DemoRequestHandler

    server = HTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    port = server.server_address[1]
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


def _post_json(url: str, payload: dict) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8")
    req = Request(
        url, data=body, headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        # urlopen raises HTTPError on 4xx/5xx; capture status + body.
        if hasattr(e, "code") and hasattr(e, "read"):
            try:
                return e.code, json.loads(e.read().decode("utf-8"))
            except Exception:
                return e.code, {}
        raise


def test_unified_server_serves_bare_api_tick(demo_server_url: str) -> None:
    """The legacy bare path the C919 panel HTML uses must work on
    :8002 just as it does on the standalone :9191 — that's the
    user-facing fix this phase ships."""
    status, body = _post_json(f"{demo_server_url}/api/tick", {})
    assert status == 200, f"/api/tick returned {status}: {body}"
    assert "state" in body, f"response missing state: {body}"


def test_unified_server_serves_namespaced_api_c919_tick(
    demo_server_url: str,
) -> None:
    """A namespaced /api/c919/tick alias coexists with the legacy
    bare path so future code can use the cleaner form."""
    status, body = _post_json(f"{demo_server_url}/api/c919/tick", {})
    assert status == 200, f"/api/c919/tick returned {status}"
    assert "state" in body


def test_unified_server_serves_api_reset(demo_server_url: str) -> None:
    status, body = _post_json(f"{demo_server_url}/api/reset", {})
    assert status == 200
    assert body.get("ok") is True or "state" in body


def test_unified_server_serves_namespaced_api_c919_reset(
    demo_server_url: str,
) -> None:
    status, body = _post_json(f"{demo_server_url}/api/c919/reset", {})
    assert status == 200


# ─── 5. State actually transitions across ticks ───


def test_consecutive_ticks_advance_simulation_clock(
    demo_server_url: str,
) -> None:
    """The simulation must accumulate `t_s` across successive
    ticks — this is what the panel's setInterval(doTick, 100)
    relies on. Without persistent module-level state, t_s would
    reset to 0 on every request."""
    # Reset first to start from a known state.
    _post_json(f"{demo_server_url}/api/reset", {})
    _, first = _post_json(f"{demo_server_url}/api/tick", {"dt_s": 0.1})
    _, second = _post_json(f"{demo_server_url}/api/tick", {"dt_s": 0.1})
    _, third = _post_json(f"{demo_server_url}/api/tick", {"dt_s": 0.1})
    t1 = first.get("t_s", 0)
    t3 = third.get("t_s", 0)
    assert t3 > t1, (
        f"t_s did not advance across ticks: {t1} -> {t3}. "
        f"The unified server must hold persistent C919 system state."
    )


def test_reset_zeros_simulation_clock(demo_server_url: str) -> None:
    """After several ticks, /api/reset must zero t_s. Confirms the
    reset endpoint actually rebuilds the system (not just no-ops)."""
    # Advance some time.
    for _ in range(5):
        _post_json(f"{demo_server_url}/api/tick", {"dt_s": 0.1})
    # Reset.
    _post_json(f"{demo_server_url}/api/reset", {})
    # Tick once more — t_s should be ~0.1, not ~0.6.
    _, post_reset = _post_json(f"{demo_server_url}/api/tick", {"dt_s": 0.1})
    assert post_reset.get("t_s", 99) <= 0.2, (
        f"after /api/reset, first tick t_s={post_reset.get('t_s')} — "
        f"expected ~0.1 (reset must rebuild the system, not preserve t_s)"
    )
