# src/supply_chain_agent/reasoning/reasoning_trace.py

from sqlalchemy.orm import Session
from ..models import Event
from ..impact.impact_report import ImpactReport
from ..scoring.scored_plan import ScoredPlan
from ..recommendation.recommendation import Recommendation
from ..graph.dependency_graph import build_graph, supplier_node, component_node, po_node
from ..graph.graph_utils import shortest_impact_path


def build_reasoning_trace(
    session: Session,
    event: Event,
    report: ImpactReport,
    scored_plans: list[ScoredPlan],
    recommendation: Recommendation,
) -> list[str]:
    """
    Produces a list of plain factual statements, EVERY ONE OF WHICH is
    directly derived from already-computed data structures -- nothing here
    is inferred or guessed. This is the ONLY input the LLM will be allowed
    to rewrite; it is the grounding boundary described in Section 2.1.
    """
    trace: list[str] = []

    # --- What happened ---
    trace.append(f"Event type: {event.event_type} (severity: {event.severity}).")
    trace.append(f"Event understanding confidence: {event.confidence_score}.")
    trace.append(
        f"Estimated source delay: {report.source_delay_days} days "
        f"(method: {report.delay_estimation_method})."
    )

    # --- Causal path (Phase 4 utility, used here for the first time) ---
    if event.component_id:
        G = build_graph(session)
        start = component_node(event.component_id)
        if report.affected_pos:
            target = po_node(report.affected_pos[0].po_id)
            path = shortest_impact_path(G, start, target)
            if path:
                readable = " -> ".join(
                    G.nodes[n].get("name", n) for n in path
                )
                trace.append(f"Impact chain (example): {readable}.")

    # --- Business impact ---
    trace.append(
        f"Affected products: {', '.join(report.affected_product_names) or 'none identified'}."
    )
    trace.append(f"Purchase orders affected: {len(report.affected_pos)}.")
    trace.append(f"Total revenue at risk: ${report.total_revenue_at_risk:,.2f}.")
    trace.append(f"High-priority customers affected: {report.high_priority_customers_affected}.")
    trace.append(f"Overall disruption severity: {report.overall_severity}.")

    # --- Options considered ---
    trace.append(f"Number of recovery plans evaluated: {len(scored_plans)}.")
    for sp in scored_plans:
        trace.append(
            f"Plan '{sp.strategy_type}' scored {sp.overall_score:.3f} "
            f"(top contributors: {_top_contributors(sp)})."
        )

    # --- The decision ---
    trace.append(
        f"Selected plan: '{recommendation.selected_strategy_type}' "
        f"with score {recommendation.selected_score:.3f}."
    )
    if recommendation.runner_up_strategy_type:
        trace.append(
            f"Runner-up: '{recommendation.runner_up_strategy_type}' "
            f"with score {recommendation.runner_up_score:.3f} "
            f"(margin: {recommendation.score_margin:.3f})."
        )
    trace.append(
        f"Overall confidence: {recommendation.overall_confidence} ({recommendation.confidence_label})."
    )
    trace.append(f"Decision status: {recommendation.decision_status}.")
    for flag in recommendation.guardrail_flags:
        trace.append(f"Guardrail triggered ({flag.guardrail_name}): {flag.message}")

    return trace


def _top_contributors(scored_plan: ScoredPlan, top_n: int = 2) -> str:
    sorted_metrics = sorted(
        scored_plan.score_breakdown.items(), key=lambda kv: kv[1].contribution, reverse=True
    )[:top_n]
    return ", ".join(f"{name} ({c.contribution:.3f})" for name, c in sorted_metrics)