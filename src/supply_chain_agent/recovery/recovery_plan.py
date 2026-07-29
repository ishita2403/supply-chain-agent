# src/supply_chain_agent/recovery/recovery_plan.py

from dataclasses import dataclass, field
import uuid


@dataclass
class RecoveryAction:
    """A single concrete, executable step within a recovery plan."""
    action_type: str        # e.g. "switch_supplier", "expedite_shipping"
    details: dict            # structured parameters the Simulation Engine will use


@dataclass
class RecoveryPlan:
    plan_id: str
    strategy_type: str        # e.g. "alternate_supplier", "hybrid"
    description: str          # human-readable summary (for Phase 10 / frontend)
    actions: list[RecoveryAction] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)

    @staticmethod
    def new(strategy_type: str, description: str,
            actions: list[RecoveryAction], assumptions: list[str] | None = None) -> "RecoveryPlan":
        return RecoveryPlan(
            plan_id=f"{strategy_type}_{uuid.uuid4().hex[:8]}",
            strategy_type=strategy_type,
            description=description,
            actions=actions,
            assumptions=assumptions or [],
        )

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "strategy_type": self.strategy_type,
            "description": self.description,
            "actions": [a.__dict__ for a in self.actions],
            "assumptions": self.assumptions,
        }