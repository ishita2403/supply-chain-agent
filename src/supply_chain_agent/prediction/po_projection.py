# src/supply_chain_agent/prediction/po_projection.py

from ..impact.impact_report import ImpactReport
from ..recovery.recovery_plan import RecoveryPlan
from ..simulation.simulation_result import SimulationResult
from .projected_po import ProjectedPO


def project_po_outcomes(
    report: ImpactReport,
    selected_plan: RecoveryPlan,
    sim_result: SimulationResult,
) -> list[ProjectedPO]:
    """
    Projects the residual delay for each individually affected PO.

    Special case: 'delay_low_priority' plans give DIFFERENT outcomes to
    different POs by design (that's the whole point of the strategy), so
    we read the actual protected/delayed PO lists from the plan's own
    action details rather than applying one uniform reduction -- see
    Section 2.3 for why a uniform reduction would be wrong here.
    """
    if selected_plan.strategy_type == "delay_low_priority":
        return _project_delay_low_priority(report, selected_plan)

    # Default case: the plan's delay_reduction_days applies uniformly,
    # since the plan doesn't distinguish between individual orders.
    projected = []
    for po in report.affected_pos:
        residual = max(0, po.delay_days - int(sim_result.delay_reduction_days))
        projected.append(ProjectedPO(
            po_id=po.po_id,
            product_name=po.product_name,
            customer_name=po.customer_name,
            customer_priority_tier=po.customer_priority_tier,
            original_delay_days=po.delay_days,
            projected_delay_days=residual,
            still_at_risk=residual > 0,
        ))
    return projected


def _project_delay_low_priority(report: ImpactReport, selected_plan) -> list[ProjectedPO]:
    action = selected_plan.actions[0]  # deprioritize_orders is always a single-action plan
    protected_ids = set(action.details["protected_po_ids"])
    additional_delay = action.details["additional_delay_days_for_deprioritized"]

    projected = []
    for po in report.affected_pos:
        if po.po_id in protected_ids:
            residual = 0  # fully protected -- supply routed to high-priority orders first
        else:
            residual = po.delay_days + additional_delay  # deprioritized orders get WORSE, not better
        projected.append(ProjectedPO(
            po_id=po.po_id,
            product_name=po.product_name,
            customer_name=po.customer_name,
            customer_priority_tier=po.customer_priority_tier,
            original_delay_days=po.delay_days,
            projected_delay_days=residual,
            still_at_risk=residual > 0,
        ))
    return projected