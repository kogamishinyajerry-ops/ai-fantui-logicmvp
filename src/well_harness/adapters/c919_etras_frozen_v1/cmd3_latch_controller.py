"""§5.4 CMD3 置位—保持—复位锁存

Set  = (Engine_Running OR TRCU_Menu_Mode) AND Selected_MLG_WOW AND NOT TR_Inhibited
       AND APWTLA
       （v2 §4.4 字面仅写 APWTLA。Codex 审查复现：去掉 v1.0 兜底后，空中
        APWTLA 故障会误上三相电达 1s。在需求方给出完整 TR_Command3_Enable
        公式前，此处保留 v1.0 兜底作为安全底线。详见 OPEN-Q-V2-01。）
Reset = NOT TR_Command3_Enable
        （TR_Command3_Enable 是 FADEC→EICU 信号，见下方 derive_tr_command3_enable）
优先级：**Reset 优先**（冻结§9 验收#6："E_TRAS_OverTemp_Fault 触发后必须立即
进入保护断电路径"；同时§5.4 原文把 Reset 的 IF 放在 Set 之后，语义上后置 IF
覆盖前置 IF）。只有 tr_command3_enable==TRUE 时 Set 才能生效。
冻结§2: 回杆后（APWTLA=0）不得立即掉三相电——Hold 由 TR_Command3_Enable 维持。
"""
from __future__ import annotations

from .signals import RawInputs


def derive_tr_command3_enable(
    tr_stowed_and_locked: bool,
    etras_over_temp_fault: bool,
) -> bool:
    """FADEC→EICU 使能信号（v2 §4.5）：TR 收起上锁或过温时禁止三相电。

    OPEN-Q-V2-02: v2 只声明此信号来自 FADEC，但未给出新的计算公式。当前延用
    V1.0 冻结版的 NOT(stowed_and_locked OR over_temp)。若 FADEC 侧还有其它
    禁止条件（如 APU 通道故障、主电源异常）需在 v2 评审会上向主机所确认。
    """
    return not (tr_stowed_and_locked or etras_over_temp_fault)


class Cmd3LatchController:
    def __init__(self):
        self._latch = False

    @property
    def latch(self) -> bool:
        return self._latch

    def tick(
        self,
        inp: RawInputs,
        selected_mlg_wow: bool,
        tr_command3_enable: bool,
    ) -> bool:
        # OPEN-Q-V2-01: v1.0 安全兜底，待 v2 Enable 公式确认后再决定能否去掉。
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
