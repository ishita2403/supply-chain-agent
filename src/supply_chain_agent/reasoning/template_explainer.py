# src/supply_chain_agent/reasoning/template_explainer.py

from ..recommendation.recommendation import Recommendation
from ..impact.impact_report import ImpactReport


def generate_template_explanation(report: ImpactReport, recommendation: Recommendation) -> str:
    """
    A fully deterministic, dependency-free explanation. This ALWAYS works,
    regardless of whether Ollama/the LLM is installed, running, or reachable --
    it is the guaranteed baseline described in Section 2.2.
    """
    parts = []

    parts.append(
        f"A {report.overall_severity}-severity disruption was detected, expected to "
        f"cause a {report.source_delay_days}-day delay affecting "
        f"{len(report.affected_pos)} purchase order(s) and "
        f"${report.total_revenue_at_risk:,.2f} in revenue."
    )

    parts.append(
        f"We recommend the '{recommendation.selected_strategy_type}' plan "
        f"(overall score {recommendation.selected_score:.2f})."
    )

    if recommendation.runner_up_strategy_type:
        parts.append(
            f"This narrowly/clearly outperformed the next-best option, "
            f"'{recommendation.runner_up_strategy_type}' "
            f"(score {recommendation.runner_up_score:.2f}, margin {recommendation.score_margin:.2f})."
        )

    parts.append(
        f"Overall confidence in this recommendation is {recommendation.confidence_label} "
        f"({recommendation.overall_confidence})."
    )

    if recommendation.decision_status == "requires_human_review":
        reasons = "; ".join(f.message for f in recommendation.guardrail_flags)
        parts.append(f"NOTE: This recommendation requires human review. Reasons: {reasons}")

    return " ".join(parts)