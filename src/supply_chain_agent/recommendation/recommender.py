# src/supply_chain_agent/recommendation/recommender.py

from ..models import Event
from ..scoring.scored_plan import ScoredPlan
from ..simulation.simulation_result import SimulationResult
from .confidence import compute_margin_confidence, compute_overall_confidence, confidence_label
from .guardrails import run_guardrails
from .recommendation import Recommendation


def recommend(
    event: Event,
    scored_plans: list[ScoredPlan],
    sim_results: dict[str, SimulationResult],
) -> Recommendation | None:
    if not scored_plans:
        return None  # Phase 6 guarantees this shouldn't happen, but stay defensive

    top = scored_plans[0]
    runner_up = scored_plans[1] if len(scored_plans) > 1 else None

    margin_conf = compute_margin_confidence(scored_plans)
    event_conf = event.confidence_score or 0.0
    overall_conf = compute_overall_confidence(event_conf, margin_conf)

    top_plan_sim_result = sim_results[top.plan_id]
    guardrail_flags = run_guardrails(top_plan_sim_result, overall_conf)

    decision_status = (
        "requires_human_review"
        if any(f.forces_human_review for f in guardrail_flags)
        else "auto_approved"
    )

    return Recommendation(
        event_id=event.id,
        selected_plan_id=top.plan_id,
        selected_strategy_type=top.strategy_type,
        selected_score=top.overall_score,
        runner_up_plan_id=runner_up.plan_id if runner_up else None,
        runner_up_strategy_type=runner_up.strategy_type if runner_up else None,
        runner_up_score=runner_up.overall_score if runner_up else None,
        score_margin=(top.overall_score - runner_up.overall_score) if runner_up else 1.0,
        event_understanding_confidence=event_conf,
        margin_confidence=margin_conf,
        overall_confidence=overall_conf,
        confidence_label=confidence_label(overall_conf),
        decision_status=decision_status,
        guardrail_flags=guardrail_flags,
    )