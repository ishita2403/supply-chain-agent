# src/supply_chain_agent/recovery/strategies.py

from sqlalchemy.orm import Session
from ..models import Event, SupplierComponent, Supplier
from ..impact.impact_report import ImpactReport
from .recovery_plan import RecoveryPlan, RecoveryAction


def generate_alternate_supplier_plan(session: Session, event: Event, report: ImpactReport) -> RecoveryPlan | None:
    if event.component_id is None:
        return None  # can't check alternates without knowing the component

    alternates = (
        session.query(SupplierComponent)
        .filter(SupplierComponent.component_id == event.component_id)
        .filter(SupplierComponent.supplier_id != event.supplier_id)
        .all()
    )
    if not alternates:
        return None  # FEASIBILITY CHECK: no alternate supplier exists -- don't propose this plan

    # Pick the alternate with the shortest lead time -- the most
    # operationally sensible default if there are multiple options.
    best_alt = min(alternates, key=lambda sc: sc.lead_time_days)
    supplier = session.query(Supplier).get(best_alt.supplier_id)

    total_qty = sum(po.quantity for po in report.affected_pos) or 1000  # fallback if no PO data

    action = RecoveryAction(
        action_type="switch_supplier",
        details={
            "component_id": event.component_id,
            "new_supplier_id": supplier.id,
            "new_supplier_name": supplier.name,
            "new_lead_time_days": best_alt.lead_time_days,
            "new_unit_cost": best_alt.unit_cost,
            "quantity": total_qty,
        },
    )

    return RecoveryPlan.new(
        strategy_type="alternate_supplier",
        description=(
            f"Switch sourcing of the affected component to {supplier.name}, "
            f"with a {best_alt.lead_time_days}-day lead time at ${best_alt.unit_cost:.2f}/unit."
        ),
        actions=[action],
        assumptions=[f"Assumes {supplier.name} has capacity for {total_qty} units on short notice."],
    )
def generate_air_freight_plan(event: Event, report: ImpactReport) -> RecoveryPlan | None:
    # Air freight only makes sense for delays rooted in shipping/sourcing time --
    # not, say, a quality defect (expediting a defective batch doesn't help).
    APPLICABLE_EVENT_TYPES = {"supplier_delay", "transportation_delay", "inventory_shortage"}
    if event.event_type not in APPLICABLE_EVENT_TYPES:
        return None

    if report.source_delay_days <= 0:
        return None

    # Domain assumption: air freight can recover most, but not all, of a
    # ground/sea-based lead time -- and carries a cost premium.
    AIR_FREIGHT_DELAY_RECOVERY_DAYS = min(report.source_delay_days, 7)
    AIR_FREIGHT_COST_MULTIPLIER = 3.5  # vs. standard shipping cost

    total_qty = sum(po.quantity for po in report.affected_pos) or 1000

    action = RecoveryAction(
        action_type="expedite_shipping",
        details={
            "component_id": event.component_id,
            "quantity": total_qty,
            "delay_recovered_days": AIR_FREIGHT_DELAY_RECOVERY_DAYS,
            "cost_multiplier": AIR_FREIGHT_COST_MULTIPLIER,
        },
    )

    return RecoveryPlan.new(
        strategy_type="air_freight",
        description=(
            f"Expedite shipment via air freight, recovering up to "
            f"{AIR_FREIGHT_DELAY_RECOVERY_DAYS} days of delay at {AIR_FREIGHT_COST_MULTIPLIER}x "
            f"standard shipping cost."
        ),
        actions=[action],
        assumptions=["Assumes air freight capacity is available on short notice.",
                     "Assumes a 3.5x cost multiplier vs. standard shipping (industry-typical estimate)."],
    )


def generate_reschedule_plan(event: Event, report: ImpactReport) -> RecoveryPlan:
    # Always feasible -- this is the "acknowledge reality, no exotic action" baseline.
    action = RecoveryAction(
        action_type="reschedule_due_dates",
        details={
            "delay_days": report.source_delay_days,
            "affected_po_ids": [po.po_id for po in report.affected_pos],
        },
    )
    return RecoveryPlan.new(
        strategy_type="reschedule_production",
        description=(
            f"Formally reschedule affected purchase orders by "
            f"{report.source_delay_days} days to reflect the actual disruption, "
            f"with proactive customer communication."
        ),
        actions=[action],
        assumptions=["Assumes customers can be notified and accept the revised timeline."],
    )


def generate_inventory_allocation_plan(session: Session, event: Event, report: ImpactReport) -> RecoveryPlan | None:
    from ..models import Inventory

    if not report.affected_pos:
        return None

    # Look for FINISHED PRODUCT inventory (not component inventory) --
    # this strategy is about using stock that's already a completed product.
    product_names_to_ids = {}
    for po in report.affected_pos:
        product_names_to_ids.setdefault(po.product_name, None)

    # We need product_id, but AffectedPO only stores product_name -- look it up.
    from ..models import Product
    for name in list(product_names_to_ids.keys()):
        product = session.query(Product).filter_by(name=name).first()
        if product:
            product_names_to_ids[name] = product.id

    total_available = 0
    for pid in product_names_to_ids.values():
        if pid is None:
            continue
        total_available += sum(
            inv.quantity_on_hand for inv in
            session.query(Inventory).filter_by(item_type="product", item_id=pid).all()
        )

    if total_available <= 0:
        return None  # FEASIBILITY CHECK: no finished-goods inventory to draw on

    total_needed = sum(po.quantity for po in report.affected_pos)
    units_covered = min(total_available, total_needed)

    action = RecoveryAction(
        action_type="allocate_inventory",
        details={
            "units_available": total_available,
            "units_covered": units_covered,
            "units_still_short": max(0, total_needed - total_available),
        },
    )
    return RecoveryPlan.new(
        strategy_type="allocate_inventory",
        description=(
            f"Use {units_covered} units of existing finished-goods inventory to "
            f"immediately (partially) fulfill affected orders, buying time for the "
            f"underlying disruption to resolve."
        ),
        actions=[action],
        assumptions=["Assumes finished-goods inventory is not already earmarked for other orders."],
    )
def generate_split_production_plan(session: Session, event: Event, report: ImpactReport) -> RecoveryPlan | None:
    from ..models import FactoryProduct, Product

    if not report.affected_product_names:
        return None

    product = session.query(Product).filter_by(name=report.affected_product_names[0]).first()
    if product is None:
        return None

    factory_links = session.query(FactoryProduct).filter_by(product_id=product.id).all()
    if len(factory_links) < 2:
        return None  # FEASIBILITY CHECK: only one factory can make this product

    total_qty = sum(po.quantity for po in report.affected_pos) or 1000
    total_capacity = sum(fl.production_rate_per_day for fl in factory_links)

    split_details = [
        {
            "factory_id": fl.factory_id,
            "share_of_production": round(fl.production_rate_per_day / total_capacity, 2),
        }
        for fl in factory_links
    ]

    action = RecoveryAction(
        action_type="split_production",
        details={"product_id": product.id, "quantity": total_qty, "factory_split": split_details},
    )
    return RecoveryPlan.new(
        strategy_type="split_production",
        description=(
            f"Split production of {product.name} across {len(factory_links)} factories, "
            f"proportional to their production rates, to parallelize catch-up."
        ),
        actions=[action],
        assumptions=["Assumes all listed factories currently have spare capacity to take on additional load."],
    )


def generate_delay_low_priority_plan(report: ImpactReport) -> RecoveryPlan | None:
    tiers_present = {po.customer_priority_tier for po in report.affected_pos}
    if len(tiers_present) < 2:
        return None  # FEASIBILITY CHECK: nothing to differentiate -- all one tier

    low_priority_pos = [po for po in report.affected_pos if po.customer_priority_tier >= 3]
    high_priority_pos = [po for po in report.affected_pos if po.customer_priority_tier == 1]
    if not low_priority_pos or not high_priority_pos:
        return None

    action = RecoveryAction(
        action_type="deprioritize_orders",
        details={
            "delayed_po_ids": [po.po_id for po in low_priority_pos],
            "protected_po_ids": [po.po_id for po in high_priority_pos],
            "additional_delay_days_for_deprioritized": 5,  # explicit domain assumption
        },
    )
    return RecoveryPlan.new(
        strategy_type="delay_low_priority",
        description=(
            f"Protect {len(high_priority_pos)} high-priority order(s) by absorbing "
            f"available supply first, pushing {len(low_priority_pos)} lower-priority "
            f"order(s) back by an additional ~5 days."
        ),
        actions=[action],
        assumptions=["Assumes lower-priority customers can tolerate additional delay without contract penalty."],
    )