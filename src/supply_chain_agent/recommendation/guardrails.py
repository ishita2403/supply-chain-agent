# src/supply_chain_agent/recommendation/guardrails.py

from dataclasses import dataclass
from ..simulation.simulation_result import SimulationResult

# Configurable policy thresholds -- named and centralized so a real
# organization could tune these without touching guardrail logic.
COST_CEILING_USD = 25000.0
LOW_CONFIDENCE_THRESHOLD = 0.45


@dataclass
class GuardrailFlag:
    guardrail_name: str
    message: str
    forces_human_review: bool


def cost_ceiling_guardrail(top_plan_result: SimulationResult, overall_confidence: float) -> GuardrailFlag | None:
    if top_plan_result.cost > COST_CEILING_USD:
        return GuardrailFlag(
            guardrail_name="cost_ceiling",
            message=(
                f"Top-ranked plan costs ${top_plan_result.cost:,.2f}, exceeding the "
                f"${COST_CEILING_USD:,.2f} auto-approval ceiling. Human sign-off required."
            ),
            forces_human_review=True,
        )
    return None


def low_confidence_guardrail(top_plan_result: SimulationResult, overall_confidence: float) -> GuardrailFlag | None:
    if overall_confidence < LOW_CONFIDENCE_THRESHOLD:
        return GuardrailFlag(
            guardrail_name="low_confidence",
            message=(
                f"Overall confidence ({overall_confidence:.2f}) is below the "
                f"{LOW_CONFIDENCE_THRESHOLD} threshold -- recommend human review before acting."
            ),
            forces_human_review=True,
        )
    return None


GUARDRAILS = [cost_ceiling_guardrail, low_confidence_guardrail]


def run_guardrails(top_plan_result: SimulationResult, overall_confidence: float) -> list[GuardrailFlag]:
    flags = []
    for guardrail_fn in GUARDRAILS:
        flag = guardrail_fn(top_plan_result, overall_confidence)
        if flag is not None:
            flags.append(flag)
    return flags