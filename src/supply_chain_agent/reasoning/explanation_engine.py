# src/supply_chain_agent/reasoning/explanation_engine.py

from dataclasses import dataclass
from sqlalchemy.orm import Session

from ..models import Event
from ..impact.impact_report import ImpactReport
from ..scoring.scored_plan import ScoredPlan
from ..recommendation.recommendation import Recommendation
from .reasoning_trace import build_reasoning_trace
from .template_explainer import generate_template_explanation
from .llm_client import call_ollama


@dataclass
class Explanation:
    reasoning_trace: list[str]
    narrative: str
    narrative_source: str  # "llm" or "template"


LLM_PROMPT_TEMPLATE = """You are writing a short business explanation for a supply chain decision that has ALREADY been made by an automated analysis system.

Rewrite the following facts as a clear, fluent paragraph (4-6 sentences) for a supply chain manager.

STRICT RULES:
- Do NOT introduce any number, name, or fact that is not explicitly listed below.
- Do NOT suggest a different plan than the one stated as "Selected plan".
- Do NOT add speculation, caveats, or recommendations beyond what is stated.
- Keep it factual and concise -- this is a business report, not marketing copy.

FACTS:
{facts}

Write the paragraph now:"""


def generate_explanation(
    session: Session,
    event: Event,
    report: ImpactReport,
    scored_plans: list[ScoredPlan],
    recommendation: Recommendation,
    graph=None,
    skip_llm: bool = False,
) -> Explanation:
    """
    Generates the business explanation for the recommendation.

    If a dependency graph has already been built by the orchestrator,
    reuse it to avoid rebuilding the graph.

    If skip_llm=True, bypass the Ollama call and immediately use the
    template explanation for faster execution.
    """

    # Build reasoning trace (reuse graph if supplied)
    trace = build_reasoning_trace(
        session,
        event,
        report,
        scored_plans,
        recommendation,
        graph=graph,
    )

    # Optional fast path: skip the LLM completely
    if skip_llm:
        template_narrative = generate_template_explanation(
            report,
            recommendation,
        )
        return Explanation(
            reasoning_trace=trace,
            narrative=template_narrative,
            narrative_source="template",
        )

    # Build LLM prompt
    prompt = LLM_PROMPT_TEMPLATE.format(
        facts="\n".join(f"- {line}" for line in trace)
    )

    # Call Ollama
    llm_output = call_ollama(prompt)

    # Accept only if the output passes sanity checks
    if llm_output and _passes_basic_sanity_check(
        llm_output,
        recommendation,
    ):
        return Explanation(
            reasoning_trace=trace,
            narrative=llm_output,
            narrative_source="llm",
        )

    # Fallback to deterministic template explanation
    template_narrative = generate_template_explanation(
        report,
        recommendation,
    )

    return Explanation(
        reasoning_trace=trace,
        narrative=template_narrative,
        narrative_source="template",
    )


def _passes_basic_sanity_check(
    llm_output: str,
    recommendation: Recommendation,
) -> bool:
    """
    Lightweight guard against hallucinations.

    Ensures that the generated explanation explicitly mentions
    the selected recovery strategy.
    """

    if not llm_output or len(llm_output) < 20:
        return False

    strategy_words = (
        recommendation.selected_strategy_type
        .replace("_", " ")
        .split()
    )

    return any(
        word.lower() in llm_output.lower()
        for word in strategy_words
    )