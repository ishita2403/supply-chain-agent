# src/supply_chain_agent/impact/impact_analysis.py

from sqlalchemy.orm import Session
from ..models import Event, Inventory, PurchaseOrder, Product, Customer, Factory, Component
from ..graph.dependency_graph import (
    build_graph, supplier_node, component_node, factory_node,
)
from ..graph.graph_utils import get_downstream_impact
from .delay_estimator import estimate_source_delay_days
from .impact_report import ImpactReport, AffectedPO
from .severity import compute_severity_from_delay_and_priority


def _get_start_node(event: Event) -> str | None:
    """
    Picks the most specific known entity as the traversal starting point.
    Preference order: component > supplier > factory, because a component
    is usually the most precise/actionable point of disruption -- a
    supplier disruption is really "felt" at the component level.
    """
    if event.component_id:
        return component_node(event.component_id)
    if event.supplier_id:
        return supplier_node(event.supplier_id)
    if event.factory_id:
        return factory_node(event.factory_id)
    return None


def _estimate_inventory_buffer_days(session: Session, component_id: int, factory_id: int | None,
                                     daily_consumption_estimate: float) -> float:
    """
    Existing inventory can partially absorb an upstream delay.
    Returns how many days of buffer the current stock provides.
    """
    if daily_consumption_estimate <= 0:
        return 0.0

    query = session.query(Inventory).filter_by(item_type="component", item_id=component_id)
    if factory_id:
        query = query.filter_by(factory_id=factory_id)

    total_on_hand = sum(inv.quantity_on_hand for inv in query.all())
    return total_on_hand / daily_consumption_estimate


def analyze_impact(session: Session, event: Event) -> ImpactReport | None:
    if event.status != "understood":
        raise ValueError("Event must be understood before impact analysis can run.")

    start_node = _get_start_node(event)
    if start_node is None:
        # Entity linking failed in Phase 3 -- we cannot analyze impact.
        return None

    delay_days, method = estimate_source_delay_days(event.raw_text, event.event_type, event.severity)

    G = build_graph(session)
    downstream = get_downstream_impact(G, start_node)

    report = ImpactReport(
        event_id=event.id,
        event_type=event.event_type,
        source_description=event.raw_text,
        source_delay_days=delay_days,
        delay_estimation_method=method,
    )

    report.affected_component_names = [n["name"] for n in downstream.get("component", [])]
    report.affected_product_names = [n["name"] for n in downstream.get("product", [])]
    report.affected_factory_names = [n["name"] for n in downstream.get("factory", [])]

    affected_product_db_ids = {n["db_id"] for n in downstream.get("product", [])}
    affected_po_db_ids = {n["db_id"] for n in downstream.get("purchase_order", [])}

    total_units = 0
    total_revenue = 0.0
    high_priority_count = 0

    for po_db_id in affected_po_db_ids:
        po = session.query(PurchaseOrder).get(po_db_id)
        if po is None or po.product_id not in affected_product_db_ids:
            continue

        product = session.query(Product).get(po.product_id)
        customer = session.query(Customer).get(po.customer_id)

        # --- Apply inventory buffer to soften the raw source delay ---
        # Rough daily consumption estimate: PO quantity / a 30-day fulfillment
        # assumption. This is a simplification -- see "Common Mistakes" below.
        daily_consumption_estimate = po.quantity / 30
        factory_id_for_buffer = None  # simplification: buffer checked across all factories
        buffer_days = 0.0
        if event.component_id:
            buffer_days = _estimate_inventory_buffer_days(
                session, event.component_id, factory_id_for_buffer, daily_consumption_estimate
            )

        effective_delay = max(0, round(delay_days - buffer_days))

        revenue_at_risk = po.quantity * product.unit_price

        report.affected_pos.append(AffectedPO(
            po_id=po.id,
            product_name=product.name,
            customer_name=customer.name,
            customer_priority_tier=customer.priority_tier,
            quantity=po.quantity,
            due_date=str(po.due_date),
            delay_days=effective_delay,
            revenue_at_risk=revenue_at_risk,
        ))

        total_units += po.quantity
        total_revenue += revenue_at_risk
        if customer.priority_tier == 1:
            high_priority_count += 1

    report.total_units_at_risk = total_units
    report.total_revenue_at_risk = round(total_revenue, 2)
    report.high_priority_customers_affected = high_priority_count
    report.overall_severity = _compute_overall_severity(report)
    return report


def _compute_overall_severity(report: ImpactReport) -> str:
    max_delay = max((po.delay_days for po in report.affected_pos), default=0)
    return compute_severity_from_delay_and_priority(max_delay, report.high_priority_customers_affected)


