"""Executor protocol.

An Executor wraps one of the two control-logic systems (FANTUI demo or
C919 E-TRAS) behind a uniform tick interface. The TimelinePlayer holds
an Executor, feeds it the current input snapshot + active fault set,
and records the result.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class ExecutorTickResult:
    """One tick's output from an Executor."""

    outputs: dict[str, Any]        # e.g. {"logic1_active": True, "tls_115vac_cmd": True, ...}
    logic_states: dict[str, str]   # {"logic1": "active" | "blocked" | "idle", ...}
    # Optional: extra inputs/sensors the executor resolved internally,
    # merged into the TraceFrame.inputs for audit.
    resolved_inputs: dict[str, Any] | None = None


class Executor(Protocol):
    """Unified tick-level interface.

    Implementations MUST NOT mutate `inputs` or `active_faults`.
    Implementations MAY carry internal state between ticks (e.g. the
    C919 12-step system, the FANTUI latched switches and plant state).
    """

    # Short identifier ("fantui" | "c919-etras").
    system_id: str

    # Canonical list of logic node ids this executor reports
    # (e.g. ["logic1", "logic2", "logic3", "logic4"]).
    logic_node_ids: tuple[str, ...]

    def reset(self, initial_inputs: dict[str, Any]) -> None:
        """Reset internal state for a fresh timeline run."""
        ...

    def tick(
        self,
        t_s: float,
        dt_s: float,
        inputs: dict[str, Any],
        active_faults: list[str],
    ) -> ExecutorTickResult:
        """Advance one tick and return controller output + logic gate states.

        Args:
            t_s:            current simulation time (end of this tick's interval).
            dt_s:           tick duration (matches Timeline.step_s).
            inputs:         canonical input dict after event application.
            active_faults:  list of "node_id:fault_type" strings active this tick.
        """
        ...
