# tests/test_dependency_graph.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from supply_chain_agent.models import SessionLocal
from supply_chain_agent.graph.dependency_graph import build_graph, supplier_node, po_node
from supply_chain_agent.graph.graph_utils import get_downstream_impact, get_upstream_dependencies, shortest_impact_path


def test_graph_builds_with_expected_node_types():
    session = SessionLocal()
    G = build_graph(session)
    node_types = {data["type"] for _, data in G.nodes(data=True)}
    assert {"supplier", "component", "product", "factory", "customer", "purchase_order"} <= node_types
    session.close()


def test_supplier_disruption_reaches_customer():
    session = SessionLocal()
    G = build_graph(session)
    impact = get_downstream_impact(G, supplier_node(1))
    assert "customer" in impact
    assert len(impact["customer"]) >= 1
    session.close()


def test_upstream_dependencies_of_a_po_include_supplier():
    session = SessionLocal()
    G = build_graph(session)
    upstream = get_upstream_dependencies(session and G, po_node(1))
    assert "supplier" in upstream
    session.close()


def test_shortest_path_exists_from_supplier_to_customer():
    session = SessionLocal()
    G = build_graph(session)
    path = shortest_impact_path(G, supplier_node(1), "customer_1")
    assert path is not None
    assert path[0] == supplier_node(1)
    assert path[-1] == "customer_1"
    session.close()