# src/supply_chain_agent/recovery/plan_generator.py

from sqlalchemy.orm import Session
from ..models import Event
from ..impact.impact_report import ImpactReport
from .recovery_plan import RecoveryPlan
from .strategies import (
    generate_alternate_supplier_plan, generate_air_freight_plan,
    generate_reschedule_plan, generate_inventory_allocation_plan,
    generate_split_production_plan, generate_delay_low_priority_plan,
)


def generate_recovery_plans(session: Session, event: Event, report: ImpactReport) -> list[RecoveryPlan]:
    candidates: list[RecoveryPlan] = []

    # Reschedule is always feasible -- guarantees we NEVER return zero plans.
    candidates.append(generate_reschedule_plan(event, report))

    for generator in (
        lambda: generate_alternate_supplier_plan(session, event, report),
        lambda: generate_air_freight_plan(event, report),
        lambda: generate_inventory_allocation_plan(session, event, report),
        lambda: generate_split_production_plan(session, event, report),
        lambda: generate_delay_low_priority_plan(report),
    ):
        plan = generator()
        if plan is not None:
            candidates.append(plan)

    hybrid = _generate_hybrid_plan(candidates)
    if hybrid is not None:
        candidates.append(hybrid)

    return candidates


def _generate_hybrid_plan(existing_plans: list[RecoveryPlan]) -> RecoveryPlan | None:
    """
    Combines two complementary strategies into one plan, when both are
    independently feasible. We specifically pair a SUPPLY-SIDE fix
    (alternate_supplier or air_freight) with a DEMAND-SIDE fix
    (allocate_inventory or delay_low_priority), since combining two
    supply-side plans (e.g. alternate supplier + air freight) would be
    redundant rather than complementary.
    """
    supply_side = next((p for p in existing_plans if p.strategy_type in
                         ("alternate_supplier", "air_freight")), None)
    demand_side = next((p for p in existing_plans if p.strategy_type in
                         ("allocate_inventory", "delay_low_priority")), None)

    if supply_side is None or demand_side is None:
        return None

    combined_actions = supply_side.actions + demand_side.actions
    combined_assumptions = supply_side.assumptions + demand_side.assumptions

    return RecoveryPlan.new(
        strategy_type="hybrid",
        description=(
            f"Hybrid strategy combining '{supply_side.strategy_type}' "
            f"({supply_side.description}) with '{demand_side.strategy_type}' "
            f"({demand_side.description})."
        ),
        actions=combined_actions,
        assumptions=combined_assumptions,
    )