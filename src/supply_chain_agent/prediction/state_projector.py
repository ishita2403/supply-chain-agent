# src/supply_chain_agent/prediction/state_projector.py

from ..impact.impact_report import ImpactReport
from ..impact.severity import compute_severity_from_delay_and_priority
from ..recovery.recovery_plan import RecoveryPlan
from ..simulation.simulation_result import SimulationResult
from .po_projection import project_po_outcomes
from .post_recommendation_state import PostRecommendationState


def project_post_recommendation_state(
    event_id: int,
    report: ImpactReport,
    selected_plan: RecoveryPlan,
    sim_result: SimulationResult,
) -> PostRecommendationState:
    projected_pos = project_po_outcomes(report, selected_plan, sim_result)

    residual_revenue = max(0.0, report.total_revenue_at_risk - sim_result.revenue_recovered)
    residual_high_priority = sum(
        1 for p in projected_pos if p.still_at_risk and p.customer_priority_tier == 1
    )
    max_residual_delay = max((p.projected_delay_days for p in projected_pos), default=0)

    residual_severity = compute_severity_from_delay_and_priority(
        max_residual_delay, residual_high_priority
    )

    return PostRecommendationState(
        event_id=event_id,
        selected_strategy_type=selected_plan.strategy_type,
        projected_pos=projected_pos,
        residual_revenue_at_risk=residual_revenue,
        revenue_recovered=sim_result.revenue_recovered,
        residual_high_priority_customers_at_risk=residual_high_priority,
        residual_severity=residual_severity,
        supplier_reliability_outlook=sim_result.supplier_reliability_score,
        inventory_position_change=-sim_result.inventory_used,
    )