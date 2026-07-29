# src/supply_chain_agent/scoring/scored_plan.py

from dataclasses import dataclass, field


@dataclass
class MetricContribution:
    weight: float
    normalized_value: float
    contribution: float  # weight * normalized_value -- this metric's share of the final score


@dataclass
class ScoredPlan:
    plan_id: str
    strategy_type: str
    overall_score: float
    score_breakdown: dict[str, MetricContribution] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "strategy_type": self.strategy_type,
            "overall_score": round(self.overall_score, 4),
            "score_breakdown": {
                metric: {
                    "weight": c.weight,
                    "normalized_value": round(c.normalized_value, 3),
                    "contribution": round(c.contribution, 4),
                }
                for metric, c in self.score_breakdown.items()
            },
        }