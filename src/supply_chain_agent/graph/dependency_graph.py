# src/supply_chain_agent/graph/dependency_graph.py

"""
Builds an in-memory directed graph representing the entire supply chain
network, from raw materials (suppliers) through to end customers.
"""

import networkx as nx
from sqlalchemy.orm import Session
from ..models import (
    Supplier, SupplierComponent, Component, BOMItem, Product,
    FactoryProduct, Factory, Customer, PurchaseOrder,
)


# --- Node ID helpers -------------------------------------------------
# Every node type gets a distinct string prefix so that, e.g.,
# Supplier(id=1) and Component(id=1) never collide as the same graph node.

def supplier_node(id_: int) -> str: return f"supplier_{id_}"
def component_node(id_: int) -> str: return f"component_{id_}"
def product_node(id_: int) -> str: return f"product_{id_}"
def factory_node(id_: int) -> str: return f"factory_{id_}"
def customer_node(id_: int) -> str: return f"customer_{id_}"
def po_node(id_: int) -> str: return f"po_{id_}"

def build_graph(session: Session) -> nx.DiGraph:
    G = nx.DiGraph()

    # --- Supplier nodes ---
    for s in session.query(Supplier).all():
        G.add_node(supplier_node(s.id), type="supplier", db_id=s.id,
                    name=s.name, reliability_score=s.reliability_score)

    # --- Component nodes ---
    for c in session.query(Component).all():
        G.add_node(component_node(c.id), type="component", db_id=c.id,
                    name=c.name, category=c.category)

    # --- Product nodes ---
    for p in session.query(Product).all():
        G.add_node(product_node(p.id), type="product", db_id=p.id,
                    name=p.name, sku=p.sku)

    # --- Factory nodes ---
    for f in session.query(Factory).all():
        G.add_node(factory_node(f.id), type="factory", db_id=f.id,
                    name=f.name, location=f.location)

    # --- Customer nodes ---
    for cu in session.query(Customer).all():
        G.add_node(customer_node(cu.id), type="customer", db_id=cu.id,
                    name=cu.name, priority_tier=cu.priority_tier)

    # --- Purchase Order nodes ---
    for po in session.query(PurchaseOrder).all():
        G.add_node(po_node(po.id), type="purchase_order", db_id=po.id,
                    quantity=po.quantity, due_date=str(po.due_date),
                    status=po.status)
    # --- Supplier -> Component edges (via SupplierComponent) ---
    for sc in session.query(SupplierComponent).all():
        G.add_edge(
            supplier_node(sc.supplier_id), component_node(sc.component_id),
            relation="supplies", lead_time_days=sc.lead_time_days,
            unit_cost=sc.unit_cost,
        )

    # --- Component -> Product edges (via BOMItem) ---
    for bom in session.query(BOMItem).all():
        G.add_edge(
            component_node(bom.component_id), product_node(bom.product_id),
            relation="used_in", quantity_required=bom.quantity_required,
        )

    # --- Product -> Factory edges (via FactoryProduct) ---
    for fp in session.query(FactoryProduct).all():
        G.add_edge(
            product_node(fp.product_id), factory_node(fp.factory_id),
            relation="made_at", production_rate_per_day=fp.production_rate_per_day,
        )

    # --- Product -> PurchaseOrder edges ---
    for po in session.query(PurchaseOrder).all():
        G.add_edge(
            product_node(po.product_id), po_node(po.id),
            relation="ordered_in",
        )
        # --- PurchaseOrder -> Customer edges ---
        G.add_edge(
            po_node(po.id), customer_node(po.customer_id),
            relation="for_customer",
        )

    return G