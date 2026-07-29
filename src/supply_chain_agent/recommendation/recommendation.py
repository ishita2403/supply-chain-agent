# src/supply_chain_agent/recommendation/recommendation.py

from dataclasses import dataclass, field
from .guardrails import GuardrailFlag


@dataclass
class Recommendation:
    event_id: int
    selected_plan_id: str
    selected_strategy_type: str
    selected_score: float

    runner_up_plan_id: str | None
    runner_up_strategy_type: str | None
    runner_up_score: float | None
    score_margin: float

    event_understanding_confidence: float
    margin_confidence: float
    overall_confidence: float
    confidence_label: str

    decision_status: str  # "auto_approved" or "requires_human_review"
    guardrail_flags: list[GuardrailFlag] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = self.__dict__.copy()
        d["guardrail_flags"] = [f.__dict__ for f in self.guardrail_flags]
        return d