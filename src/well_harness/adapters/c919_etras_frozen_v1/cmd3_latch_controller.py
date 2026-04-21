"""§5.4 CMD3 置位—保持—复位锁存

Set  = (Engine_Running OR TRCU_Menu_Mode) AND Selected_MLG_WOW==1
       AND TR_Inhibited==0 AND APWTLA==1
Reset = NOT TR_Command3_Enable
        （派生：TR_Command3_Enable = NOT (TR_Stowed_And_Locked OR E_TRAS_OverTemp_Fault)）
优先级：**Reset 优先**（冻结§9 验收#6："E_TRAS_OverTemp_Fault 触发后必须立即
进入保护断电路径"；同时§5.4 原文把 Reset 的 IF 放在 Set 之后，语义上后置 IF
覆盖前置 IF）。只有 tr_command3_enable==TRUE 时 Set 才能生效。
冻结§2: 回杆后（APWTLA=0）不得立即掉三相电——Hold 由 TR_Command3_Enable 维持。
"""
from __future__ import annotations

from .signals import RawInputs


class Cmd3LatchController:
    def __init__(self):
        self._latch = False

    @property
    def latch(self) -> bool:
        return self._latch

    @staticmethod
    def derive_tr_command3_enable(
        tr_stowed_and_locked: bool,
        etras_over_temp_fault: bool,
    ) -> bool:
        return not (tr_stowed_and_locked or etras_over_temp_fault)

    def tick(
        self,
        inp: RawInputs,
        selected_mlg_wow: bool,
        tr_command3_enable: bool,
    ) -> bool:
        set_cond = (
            (inp.engine_running or inp.trcu_menu_mode)
            and selected_mlg_wow
            and (not inp.tr_inhibited)
            and inp.apwtla
        )
        if not tr_command3_enable:
            self._latch = False
        elif set_cond:
            self._latch = True
        # else: hold
        return self._latch
