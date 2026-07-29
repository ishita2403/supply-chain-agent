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
) -> Explanation:
    trace = build_reasoning_trace(session, event, report, scored_plans, recommendation)

    prompt = LLM_PROMPT_TEMPLATE.format(facts="\n".join(f"- {line}" for line in trace))
    llm_output = call_ollama(prompt)

    if llm_output and _passes_basic_sanity_check(llm_output, recommendation):
        return Explanation(reasoning_trace=trace, narrative=llm_output, narrative_source="llm")

    # Fallback: LLM unavailable, failed, or its output looked suspicious.
    template_narrative = generate_template_explanation(report, recommendation)
    return Explanation(reasoning_trace=trace, narrative=template_narrative, narrative_source="template")


def _passes_basic_sanity_check(llm_output: str, recommendation: Recommendation) -> bool:
    """
    A lightweight, non-exhaustive guard: confirm the LLM's narrative at
    least MENTIONS the actual selected plan by name. This can't catch every
    possible hallucination, but it catches the most damaging failure mode --
    the LLM contradicting the system's actual decision.
    """
    if not llm_output or len(llm_output) < 20:
        return False
    strategy_words = recommendation.selected_strategy_type.replace("_", " ").split()
    return any(word.lower() in llm_output.lower() for word in strategy_words)