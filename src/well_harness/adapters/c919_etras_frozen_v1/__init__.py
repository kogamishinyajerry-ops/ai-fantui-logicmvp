"""C919 反推控制逻辑 — 冻结版 V1.0 实现

唯一真值：20260421《C919 反推控制逻辑正式冻结版需求文档 V1.0》
"""
from .signals import (
    FrozenConfig,
    LockInputs,
    Outputs,
    RawInputs,
    SystemState,
    DerivedSignals,
)
from .wow_selector import compute_selected_mlg_wow
from .tr_wow_filter import TrWowFilter
from .lock_status_aggregator import LockStatusAggregator
from .cmd2_controller import Cmd2Controller
from .cmd3_latch_controller import Cmd3LatchController, derive_tr_command3_enable
from .fadec_deploy_logic import compute_fadec_deploy_command
from .fadec_stow_logic import compute_fadec_stow_command
from .state_machine import StateMachine, StateMachineContext
from .safety_interlock_manager import SafetyInterlockManager
from .telemetry_logger import TelemetryLogger
from .tick import C919ReverseThrustSystem

__all__ = [
    "FrozenConfig",
    "LockInputs",
    "Outputs",
    "RawInputs",
    "SystemState",
    "DerivedSignals",
    "compute_selected_mlg_wow",
    "TrWowFilter",
    "LockStatusAggregator",
    "Cmd2Controller",
    "Cmd3LatchController",
    "derive_tr_command3_enable",
    "compute_fadec_deploy_command",
    "compute_fadec_stow_command",
    "StateMachine",
    "StateMachineContext",
    "SafetyInterlockManager",
    "TelemetryLogger",
    "C919ReverseThrustSystem",
]
