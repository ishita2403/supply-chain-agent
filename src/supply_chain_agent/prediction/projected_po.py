# src/supply_chain_agent/prediction/projected_po.py

from dataclasses import dataclass


@dataclass
class ProjectedPO:
    po_id: int
    product_name: str
    customer_name: str
    customer_priority_tier: int
    original_delay_days: int
    projected_delay_days: int
    still_at_risk: bool

    def to_dict(self) -> dict:
        return self.__dict__.copy()