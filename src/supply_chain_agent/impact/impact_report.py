# src/supply_chain_agent/impact/impact_report.py

from dataclasses import dataclass, field


@dataclass
class AffectedPO:
    po_id: int
    product_name: str
    customer_name: str
    customer_priority_tier: int
    quantity: int
    due_date: str
    delay_days: int
    revenue_at_risk: float


@dataclass
class ImpactReport:
    event_id: int
    event_type: str
    source_description: str
    source_delay_days: int
    delay_estimation_method: str

    affected_component_names: list[str] = field(default_factory=list)
    affected_product_names: list[str] = field(default_factory=list)
    affected_factory_names: list[str] = field(default_factory=list)
    affected_pos: list[AffectedPO] = field(default_factory=list)

    total_units_at_risk: int = 0
    total_revenue_at_risk: float = 0.0
    high_priority_customers_affected: int = 0
    overall_severity: str = "low"

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source_description": self.source_description,
            "source_delay_days": self.source_delay_days,
            "delay_estimation_method": self.delay_estimation_method,
            "affected_component_names": self.affected_component_names,
            "affected_product_names": self.affected_product_names,
            "affected_factory_names": self.affected_factory_names,
            "affected_pos": [po.__dict__ for po in self.affected_pos],
            "total_units_at_risk": self.total_units_at_risk,
            "total_revenue_at_risk": self.total_revenue_at_risk,
            "high_priority_customers_affected": self.high_priority_customers_affected,
            "overall_severity": self.overall_severity,
        }