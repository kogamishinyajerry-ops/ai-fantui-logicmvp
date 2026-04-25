from __future__ import annotations

from typing import Any

from well_harness.models import (
    ControllerExplain,
    ControllerOutputs,
    HarnessConfig,
    LogicConditionExplain,
    LogicExplain,
    ResolvedInputs,
)


class DeployController:
    """Pure deploy-side control logic.

    This module reflects only the confirmed logic. It does not embed plant
    assumptions such as actuator delays or lock kinematics.
    """

    def __init__(self, config: HarnessConfig | None = None) -> None:
        self.config = config or HarnessConfig()

    def explain(self, inputs: ResolvedInputs) -> ControllerExplain:
        logic1_conditions = (
            _condition(
                name="radio_altitude_ft",
                current_value=inputs.radio_altitude_ft,
                comparison="<",
                threshold_value=self.config.logic1_ra_ft_threshold,
                passed=inputs.radio_altitude_ft < self.config.logic1_ra_ft_threshold,
            ),
            _condition("sw1", inputs.sw1, "==", True, inputs.sw1),
            _condition(
                "reverser_inhibited",
                inputs.reverser_inhibited,
                "==",
                False,
                not inputs.reverser_inhibited,
            ),
            _condition(
                "reverser_not_deployed_eec",
                inputs.reverser_not_deployed_eec,
                "==",
                True,
                inputs.reverser_not_deployed_eec,
            ),
        )
        logic2_conditions = (
            _condition("engine_running", inputs.engine_running, "==", True, inputs.engine_running),
            _condition(
                "aircraft_on_ground",
                inputs.aircraft_on_ground,
                "==",
                True,
                inputs.aircraft_on_ground,
            ),
            _condition(
                "reverser_inhibited",
                inputs.reverser_inhibited,
                "==",
                False,
                not inputs.reverser_inhibited,
            ),
            _condition("sw2", inputs.sw2, "==", True, inputs.sw2),
            _condition("eec_enable", inputs.eec_enable, "==", True, inputs.eec_enable),
        )
        logic3_conditions = (
            _condition("engine_running", inputs.engine_running, "==", True, inputs.engine_running),
            _condition(
                "aircraft_on_ground",
                inputs.aircraft_on_ground,
                "==",
                True,
                inputs.aircraft_on_ground,
            ),
            _condition(
                "reverser_inhibited",
                inputs.reverser_inhibited,
                "==",
                False,
                not inputs.reverser_inhibited,
            ),
            _condition(
                "tls_unlocked_ls",
                inputs.tls_unlocked_ls,
                "==",
                True,
                inputs.tls_unlocked_ls,
            ),
            _condition(
                name="n1k",
                current_value=inputs.n1k,
                comparison="<",
                threshold_value=inputs.max_n1k_deploy_limit,
                passed=inputs.n1k < inputs.max_n1k_deploy_limit,
            ),
            _condition(
                name="tra_deg",
                current_value=inputs.tra_deg,
                comparison="<=",
                threshold_value=self.config.logic3_tra_deg_threshold,
                passed=inputs.tra_deg <= self.config.logic3_tra_deg_threshold,
            ),
        )
        logic4_conditions = (
            _condition(
                "deploy_90_percent_vdt",
                inputs.deploy_90_percent_vdt,
                "==",
                True,
                inputs.deploy_90_percent_vdt,
            ),
            _condition(
                name="tra_deg",
                current_value=inputs.tra_deg,
                # Lower-inclusive, upper-exclusive: TRA at the mechanical stop
                # (reverse_travel_min_deg = -32°) is a valid fully-reversed
                # position and must engage L4; TRA at 0° is the forward detent
                # and must NOT engage L4. A strict-both-bounds check would
                # silently drop L4 at the slider's leftmost value.
                comparison="between_lower_inclusive",
                threshold_value=(self.config.reverse_travel_min_deg, self.config.reverse_travel_max_deg),
                passed=self.config.reverse_travel_min_deg <= inputs.tra_deg < self.config.reverse_travel_max_deg,
            ),
            _condition(
                "aircraft_on_ground",
                inputs.aircraft_on_ground,
                "==",
                True,
                inputs.aircraft_on_ground,
            ),
            _condition("engine_running", inputs.engine_running, "==", True, inputs.engine_running),
        )
        return ControllerExplain(
            logic1=_logic_explain("logic1", logic1_conditions),
            logic2=_logic_explain("logic2", logic2_conditions),
            logic3=_logic_explain("logic3", logic3_conditions),
            logic4=_logic_explain("logic4", logic4_conditions),
        )

    def evaluate(self, inputs: ResolvedInputs) -> ControllerOutputs:
        outputs, _ = self.evaluate_with_explain(inputs)
        return outputs

    def evaluate_with_explain(self, inputs: ResolvedInputs) -> tuple[ControllerOutputs, ControllerExplain]:
        explain = self.explain(inputs)
        outputs = ControllerOutputs(
            logic1_active=explain.logic1.active,
            logic2_active=explain.logic2.active,
            logic3_active=explain.logic3.active,
            logic4_active=explain.logic4.active,
            tls_115vac_cmd=explain.logic1.active,
            etrac_540vdc_cmd=explain.logic2.active,
            eec_deploy_cmd=explain.logic3.active,
            pls_power_cmd=explain.logic3.active,
            pdu_motor_cmd=explain.logic3.active,
            throttle_electronic_lock_release_cmd=explain.logic4.active,
        )
        return outputs, explain

def _condition(
    name: str,
    current_value: Any,
    comparison: str,
    threshold_value: Any,
    passed: bool,
) -> LogicConditionExplain:
    return LogicConditionExplain(
        name=name,
        current_value=current_value,
        comparison=comparison,
        threshold_value=threshold_value,
        passed=passed,
    )


def _logic_explain(
    logic_name: str,
    conditions: tuple[LogicConditionExplain, ...],
) -> LogicExplain:
    return LogicExplain(
        logic_name=logic_name,
        active=all(condition.passed for condition in conditions),
        conditions=conditions,
    )
