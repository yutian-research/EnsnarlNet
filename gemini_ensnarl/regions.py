"""Region extraction, graph construction and connected-component diagnostics for the empirical data."""

import numpy as np
import networkx as nx


def extract_region_subgraph(nodes_df, edges_df, region_name):
    """Extract a subgraph for a specific region.
    """
    region_nodes = nodes_df[nodes_df["region_label"] == region_name]
    region_node_ids = set(region_nodes["id"])

    region_edges = edges_df[
        edges_df["node1id"].isin(region_node_ids) &
        edges_df["node2id"].isin(region_node_ids)
    ]

    return region_nodes, region_edges


def build_region_graphs(region_nodes, region_edges, classify=False):
    """Build region graphs from input nodes and edges
    """
    # Full graph
    G_full = nx.Graph()

    # Add nodes with attributes
    for _, row in region_nodes.iterrows():
        G_full.add_node(
            int(row["id"]),
            pos=(row["pos_x"], row["pos_y"], row["pos_z"]),
            # degree=int(row["degree"]),
            is_border=bool(row["isAtSampleBorder"]),
            region=row["region_label"]
        )

    # Add edges with attributes
    for _, row in region_edges.iterrows():
        G_full.add_edge(
            int(row["node1id"]),
            int(row["node2id"]),
            edge_id=int(row["id"]),
            minRadiusAvg=float(row["minRadiusAvg"]),
            minRadiusStd=float(row["minRadiusStd"]),
            hasNodeAtSampleBorder=bool(row["hasNodeAtSampleBorder"]),
            vessel_class=row["vessel_class"]
        )

    if classify:
        # Subgraphs by vessel class of edges -- !! May not be connected
        G_cap = G_full.edge_subgraph(
            [(u, v) for u, v, d in G_full.edges(data=True)
            if d["vessel_class"] == "capillary"]
        ).copy()

        G_av = G_full.edge_subgraph(
            [(u, v) for u, v, d in G_full.edges(data=True)
            if d["vessel_class"] == "arteriole_venule"]
        ).copy()

        G_art = G_full.edge_subgraph(
            [(u, v) for u, v, d in G_full.edges(data=True)
            if d["vessel_class"] == "artery_vein"]
        ).copy()

        return G_full, G_cap, G_av, G_art
    else:
        return G_full


def select_vertices_range(nodes_df, xlim, ylim, zlim):
    """Select vertices in the range
    """
    region_df = nodes_df[
        (nodes_df["pos_x"] > xlim[0]) & (nodes_df["pos_x"] < xlim[1])
    ]
    region_df = region_df[
        (region_df["pos_y"] > ylim[0]) & (region_df["pos_y"] < ylim[1])
    ]
    region_df = region_df[
        (region_df["pos_z"] > zlim[0]) & (region_df["pos_z"] < zlim[1])
    ]

    region_nodes = region_df["id"].values
    region_sum = np.unique(region_df['region_label'].values, return_counts=True)

    return region_nodes, region_sum


def graph_diagnostics(G: nx.Graph):
    """Generate graph statistics
    """
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()

    # connected components
    if n_nodes > 0:
        n_components = nx.number_connected_components(G)
        giant_cc_size = len(max(nx.connected_components(G), key=len))
    else:
        n_components = 0
        giant_cc_size = 0

    # border nodes
    border_nodes = sum(
        1 for _, d in G.nodes(data=True)
        if d.get("is_border", False)
    )

    # border edges
    border_edges = sum(
        1 for _, _, d in G.edges(data=True)
        if d.get("hasNodeAtSampleBorder", False)
    )

    return {
        "n_nodes": n_nodes,
        "n_edges": n_edges,
        "n_components": n_components,
        "giant_component_size": giant_cc_size,
        "border_nodes": border_nodes,
        "border_edges": border_edges,
    }


def get_cc(G):
    """Returns a list of connected components (each as a set of node IDs),
    sorted by decreasing size.
    """
    components = list(nx.connected_components(G))
    components_sorted = sorted(components, key=len, reverse=True)
    return components_sorted


def summarize_cc_topk(G, k=10):
    """Summarize features of top k connected components
    """
    components_sorted = get_cc(G)

    print(f"Total number of connected components: {len(components_sorted)}\n")

    summary = []
    for i, comp in enumerate(components_sorted[:k]):
        comp_size = len(comp)

        # Pick one representative node (first one in the set)
        rep_node = next(iter(comp))
        rep_pos = G.nodes[rep_node].get("pos", None)

        summary.append({
            "rank": i + 1,
            "component_size": comp_size,
            "representative_node": rep_node,
            "representative_position": rep_pos
        })

        print(
            f"Rank {i+1}: size = {comp_size}, "
            f"rep node = {rep_node}, "
            f"rep pos = {rep_pos}"
        )

    return summary
