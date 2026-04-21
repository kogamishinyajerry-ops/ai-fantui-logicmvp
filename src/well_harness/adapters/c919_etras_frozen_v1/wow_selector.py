"""§5.1 主轮载选择逻辑"""
from __future__ import annotations

from .signals import RawInputs


def compute_selected_mlg_wow(inp: RawInputs) -> bool:
    v1, v2 = inp.lgcu1_valid, inp.lgcu2_valid
    w1, w2 = inp.lgcu1_mlg_wow, inp.lgcu2_mlg_wow
    if v1 and v2:
        if w1 == w2:
            return bool(w1)
        return False  # 冲突 → 安全侧判为空中
    if v1 and not v2:
        return bool(w1)
    if (not v1) and v2:
        return bool(w2)
    return False
