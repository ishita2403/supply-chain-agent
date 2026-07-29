# src/supply_chain_agent/graph/graph_utils.py

import networkx as nx


def get_downstream_impact(G: nx.DiGraph, start_node: str) -> dict:
    """
    Returns everything reachable FORWARD from start_node — i.e. everything
    that could be impacted if start_node is disrupted.
    Grouped by node type for easy consumption by Impact Analysis (Phase 5).
    """
    if start_node not in G:
        return {}

    descendants = nx.descendants(G, start_node)  # all reachable nodes, any distance

    grouped: dict[str, list[dict]] = {}
    for node_id in descendants:
        node_data = G.nodes[node_id]
        node_type = node_data["type"]
        grouped.setdefault(node_type, []).append({"node_id": node_id, **node_data})

    return grouped


def get_upstream_dependencies(G: nx.DiGraph, target_node: str) -> dict:
    """
    Returns everything reachable BACKWARD from target_node — i.e. everything
    that target_node depends on. Useful for questions like
    "why is this PO at risk?"
    """
    if target_node not in G:
        return {}

    ancestors = nx.ancestors(G, target_node)

    grouped: dict[str, list[dict]] = {}
    for node_id in ancestors:
        node_data = G.nodes[node_id]
        node_type = node_data["type"]
        grouped.setdefault(node_type, []).append({"node_id": node_id, **node_data})

    return grouped


def shortest_impact_path(G: nx.DiGraph, start_node: str, end_node: str) -> list[str] | None:
    """
    Returns the specific chain of nodes connecting a disruption source to a
    specific downstream node (e.g. a specific PO) — useful for explaining
    'how' the impact reaches that far (Phase 10: Reasoning Engine will use this).
    """
    try:
        return nx.shortest_path(G, start_node, end_node)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None