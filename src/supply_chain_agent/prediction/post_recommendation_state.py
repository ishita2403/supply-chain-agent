# src/supply_chain_agent/prediction/post_recommendation_state.py

from dataclasses import dataclass, field
from .projected_po import ProjectedPO


@dataclass
class PostRecommendationState:
    event_id: int
    selected_strategy_type: str

    projected_pos: list[ProjectedPO] = field(default_factory=list)

    residual_revenue_at_risk: float = 0.0
    revenue_recovered: float = 0.0
    residual_high_priority_customers_at_risk: int = 0
    residual_severity: str = "low"

    supplier_reliability_outlook: float = 0.9
    inventory_position_change: int = 0  # negative = inventory consumed

    narrative: str = ""
    narrative_source: str = "template"

    def to_dict(self) -> dict:
        d = self.__dict__.copy()
        d["projected_pos"] = [p.to_dict() for p in self.projected_pos]
        return d