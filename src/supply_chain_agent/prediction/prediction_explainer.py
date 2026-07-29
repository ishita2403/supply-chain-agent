# src/supply_chain_agent/prediction/prediction_explainer.py

from ..impact.impact_report import ImpactReport
from .post_recommendation_state import PostRecommendationState
from ..reasoning.llm_client import call_ollama

PREDICTION_PROMPT_TEMPLATE = """You are writing a short "before vs after" business summary for a supply chain recovery plan that has ALREADY been decided and is ABOUT TO BE applied.

Rewrite the following facts as a clear, fluent paragraph (3-5 sentences).

STRICT RULES:
- Do NOT introduce any number or fact not explicitly listed below.
- Do NOT speculate about outcomes beyond what is stated.
- Be factual and concise.

FACTS:
{facts}

Write the paragraph now:"""


def build_prediction_trace(report: ImpactReport, after: PostRecommendationState) -> list[str]:
    trace = [
        f"Before: total revenue at risk was ${report.total_revenue_at_risk:,.2f}.",
        f"After applying '{after.selected_strategy_type}': residual revenue at risk is "
        f"${after.residual_revenue_at_risk:,.2f} (${after.revenue_recovered:,.2f} recovered).",
        f"Before: overall severity was '{report.overall_severity}'.",
        f"After: projected overall severity is '{after.residual_severity}'.",
        f"Before: {report.high_priority_customers_affected} high-priority customer(s) affected.",
        f"After: {after.residual_high_priority_customers_at_risk} high-priority customer(s) still at risk.",
        f"Supplier reliability outlook after this plan: {after.supplier_reliability_outlook}.",
    ]
    if after.inventory_position_change != 0:
        trace.append(f"Inventory position change: {after.inventory_position_change} units.")

    still_at_risk = [p for p in after.projected_pos if p.still_at_risk]
    if still_at_risk:
        names = ", ".join(f"PO #{p.po_id} ({p.customer_name})" for p in still_at_risk)
        trace.append(f"Purchase orders still at risk after this plan: {names}.")
    else:
        trace.append("No purchase orders remain at risk after this plan.")

    return trace


def generate_prediction_narrative(trace: list[str]) -> tuple[str, str]:
    """Returns (narrative, source) -- mirrors Phase 10's pattern exactly."""
    prompt = PREDICTION_PROMPT_TEMPLATE.format(facts="\n".join(f"- {line}" for line in trace))
    llm_output = call_ollama(prompt)

    if llm_output and len(llm_output) > 20:
        return llm_output, "llm"

    # Template fallback -- always available, same philosophy as Phase 10.
    return " ".join(trace), "template"