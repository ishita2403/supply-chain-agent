# src/supply_chain_agent/orchestrator/agent_run.py

from dataclasses import dataclass, field
from ..models import Event
from ..impact.impact_report import ImpactReport
from ..recovery.recovery_plan import RecoveryPlan
from ..simulation.simulation_result import SimulationResult
from ..scoring.scored_plan import ScoredPlan
from ..recommendation.recommendation import Recommendation
from ..reasoning.explanation_engine import Explanation
from ..prediction.post_recommendation_state import PostRecommendationState


@dataclass
class AgentRun:
    event_id: int
    status: str = "in_progress"        # in_progress -> complete | incomplete
    stopped_at_step: str | None = None
    stop_reason: str | None = None

    event: Event | None = None
    report: ImpactReport | None = None
    plans: list[RecoveryPlan] = field(default_factory=list)
    sim_results: dict[str, SimulationResult] = field(default_factory=dict)
    scored_plans: list[ScoredPlan] = field(default_factory=list)
    recommendation: Recommendation | None = None
    explanation: Explanation | None = None
    post_state: PostRecommendationState | None = None

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "status": self.status,
            "stopped_at_step": self.stopped_at_step,
            "stop_reason": self.stop_reason,
            "event": {
                "id": self.event.id, "event_type": self.event.event_type,
                "severity": self.event.severity, "confidence_score": self.event.confidence_score,
                "raw_text": self.event.raw_text,
            } if self.event else None,
            "impact_report": self.report.to_dict() if self.report else None,
            "recovery_plans": [p.to_dict() for p in self.plans],
            "scored_plans": [sp.to_dict() for sp in self.scored_plans],
            "recommendation": self.recommendation.to_dict() if self.recommendation else None,
            "explanation": {
                "reasoning_trace": self.explanation.reasoning_trace,
                "narrative": self.explanation.narrative,
                "narrative_source": self.explanation.narrative_source,
            } if self.explanation else None,
            "post_recommendation_state": self.post_state.to_dict() if self.post_state else None,
        }