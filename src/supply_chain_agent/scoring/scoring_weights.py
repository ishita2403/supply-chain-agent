# src/supply_chain_agent/scoring/scoring_weights.py

from dataclasses import dataclass


@dataclass
class ScoringWeights:
    """
    Business priority weights for scoring recovery plans.
    Must sum to 1.0 -- enforced in __post_init__ so a misconfigured
    weight set fails loudly at construction time, not silently
    later inside a score calculation.
    """
    cost: float = 0.20
    delay_reduction: float = 0.25
    customer_satisfaction: float = 0.20
    risk: float = 0.15                # inverted during scoring: lower risk -> higher contribution
    revenue_recovered: float = 0.15
    supplier_reliability: float = 0.05

    def __post_init__(self):
        total = (self.cost + self.delay_reduction + self.customer_satisfaction
                 + self.risk + self.revenue_recovered + self.supplier_reliability)
        if not (0.99 <= total <= 1.01):  # small float tolerance
            raise ValueError(f"ScoringWeights must sum to 1.0, got {total:.3f}")

    def as_dict(self) -> dict:
        return {
            "cost": self.cost, "delay_reduction": self.delay_reduction,
            "customer_satisfaction": self.customer_satisfaction, "risk": self.risk,
            "revenue_recovered": self.revenue_recovered,
            "supplier_reliability": self.supplier_reliability,
        }


# A named alternate profile, ready to demo weight-sensitivity in your viva.
COST_SENSITIVE_WEIGHTS = ScoringWeights(
    cost=0.40, delay_reduction=0.20, customer_satisfaction=0.10,
    risk=0.15, revenue_recovered=0.10, supplier_reliability=0.05,
)

CUSTOMER_FIRST_WEIGHTS = ScoringWeights(
    cost=0.10, delay_reduction=0.20, customer_satisfaction=0.40,
    risk=0.10, revenue_recovered=0.15, supplier_reliability=0.05,
)