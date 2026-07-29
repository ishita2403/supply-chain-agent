# src/supply_chain_agent/simulation/simulation_result.py

from dataclasses import dataclass


@dataclass
class SimulationResult:
    plan_id: str
    strategy_type: str

    cost: float = 0.0
    delay_reduction_days: float = 0.0
    inventory_used: int = 0
    customer_satisfaction_score: float = 50.0   # 0-100, default = neutral
    factory_utilization_pct: float = 100.0        # 100 = business-as-usual
    revenue_recovered: float = 0.0
    risk_score: float = 20.0                       # 0-100, lower = safer, default = mild
    supplier_reliability_score: float = 0.9         # 0-1, default = current baseline assumption

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def combine_partial_results(plan_id: str, strategy_type: str,
                             partials: list[SimulationResult]) -> SimulationResult:
    """
    Combines partial SimulationResults from multiple actions within one plan
    into a single overall result. Combination rule differs per metric,
    because different metrics behave differently when actions stack:
      - cost, inventory_used, revenue_recovered: ADDITIVE (each action
        contributes independently to the total)
      - delay_reduction_days: MAX (delay is fixed once ANY action removes
        it -- two actions both "fixing" the same days of delay don't
        double the benefit)
      - customer_satisfaction, factory_utilization, risk, supplier_reliability:
        AVERAGE (these are already 0-100/0-1 normalized judgments; averaging
        avoids them exceeding their natural bounds when combined)
    """
    if not partials:
        return SimulationResult(plan_id=plan_id, strategy_type=strategy_type)

    n = len(partials)
    return SimulationResult(
        plan_id=plan_id,
        strategy_type=strategy_type,
        cost=sum(p.cost for p in partials),
        delay_reduction_days=max(p.delay_reduction_days for p in partials),
        inventory_used=sum(p.inventory_used for p in partials),
        customer_satisfaction_score=sum(p.customer_satisfaction_score for p in partials) / n,
        factory_utilization_pct=sum(p.factory_utilization_pct for p in partials) / n,
        revenue_recovered=sum(p.revenue_recovered for p in partials),
        risk_score=sum(p.risk_score for p in partials) / n,
        supplier_reliability_score=sum(p.supplier_reliability_score for p in partials) / n,
    )