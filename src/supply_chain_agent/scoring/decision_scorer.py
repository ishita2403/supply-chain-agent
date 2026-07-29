# src/supply_chain_agent/scoring/decision_scorer.py

from ..simulation.simulation_result import SimulationResult
from .scoring_weights import ScoringWeights
from .normalizer import normalize_metric
from .scored_plan import ScoredPlan, MetricContribution

# Maps each scored metric -> (attribute on SimulationResult, higher_is_better?)
SCORED_METRICS = {
    "cost": ("cost", False),
    "delay_reduction": ("delay_reduction_days", True),
    "customer_satisfaction": ("customer_satisfaction_score", True),
    "risk": ("risk_score", False),
    "revenue_recovered": ("revenue_recovered", True),
    "supplier_reliability": ("supplier_reliability_score", True),
}


def score_all_plans(
    results: dict[str, SimulationResult],
    weights: ScoringWeights = ScoringWeights(),
    exclude_baseline: bool = True,
) -> list[ScoredPlan]:
    """
    Scores every plan's SimulationResult using the Weighted Sum Model.
    Returns plans sorted by overall_score, descending (best first).
    """
    plan_ids = [pid for pid in results if not (exclude_baseline and pid == "baseline_do_nothing")]
    if not plan_ids:
        return []

    weights_dict = weights.as_dict()

    # Step 1: for each metric, gather raw values across all plans and normalize together.
    # This MUST happen metric-by-metric across ALL plans at once -- normalizing
    # one plan's cost in isolation is meaningless; it only means something
    # relative to the other candidates' costs.
    normalized_by_metric: dict[str, dict[str, float]] = {}
    for metric_name, (attr, higher_is_better) in SCORED_METRICS.items():
        raw_values = {pid: getattr(results[pid], attr) for pid in plan_ids}
        normalized_by_metric[metric_name] = normalize_metric(raw_values, higher_is_better)

    # Step 2: build each plan's weighted sum + breakdown.
    scored_plans = []
    for pid in plan_ids:
        breakdown = {}
        overall_score = 0.0
        for metric_name in SCORED_METRICS:
            weight = weights_dict[metric_name]
            norm_val = normalized_by_metric[metric_name][pid]
            contribution = weight * norm_val
            breakdown[metric_name] = MetricContribution(
                weight=weight, normalized_value=norm_val, contribution=contribution
            )
            overall_score += contribution

        scored_plans.append(ScoredPlan(
            plan_id=pid,
            strategy_type=results[pid].strategy_type,
            overall_score=overall_score,
            score_breakdown=breakdown,
        ))

    scored_plans.sort(key=lambda sp: sp.overall_score, reverse=True)
    return scored_plans