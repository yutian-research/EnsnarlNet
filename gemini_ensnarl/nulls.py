"""Spatial, radius null models for the empirical vascular networks."""

import numpy as np
import networkx as nx
import pandas as pd
from typing import Optional, Tuple


def generate_spatial_null_model(n_nodes: int, m_edges: int, df_edges_sel: pd.DataFrame,
    xyz_ranges: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]],
    directed: bool = False, seed: Optional[int] = None, node_ids: Optional[np.ndarray] = None,
                                p_dist = True):
    """
    Generate a spatial null model:
      - n_nodes nodes with uniform random (x,y,z) in given ranges
      - m_edges random edges among nodes (no self-loops; no multi-edges) [simplest case]
      - edge attribute 'minRadiusAvg' sampled from empirical distribution in df_edges_sel['minRadiusAvg']

    Parameters
    ----------
    n_nodes : int
        Number of nodes.
    m_edges : int
        Number of edges to generate (will error if too large for simple graph).
    df_edges_sel : pd.DataFrame
        Empirical edges dataframe containing column 'minRadiusAvg'.
    xyz_ranges : ((xmin, xmax),(ymin, ymax),(zmin, zmax))
        Ranges for uniform sampling of coordinates.
    directed : bool
        If True, generate directed edges (u->v). If False, undirected edges.
    seed : int or None
        RNG seed.
    node_ids : array or None
        Optional explicit node IDs. If None, uses 0..n_nodes-1.

    Returns
    -------
    nodes_null_df : pd.DataFrame
        Columns: id, pos_x, pos_y, pos_z
    edges_null_df : pd.DataFrame
        Columns: id, node1id, node2id, minRadiusAvg
    G_null : nx.Graph or nx.DiGraph
        NetworkX graph with node positions and edge radii.
    """
    rng = np.random.default_rng(seed)

    # Node IDs
    if node_ids is None:
        node_ids = np.arange(n_nodes, dtype=np.int64)
    else:
        node_ids = np.asarray(node_ids)
        if len(node_ids) != n_nodes:
            raise ValueError("node_ids length must equal n_nodes")

    # 1) Random locations
    (xmin, xmax), (ymin, ymax), (zmin, zmax) = xyz_ranges
    xs = rng.uniform(xmin, xmax, size=n_nodes)
    ys = rng.uniform(ymin, ymax, size=n_nodes)
    zs = rng.uniform(zmin, zmax, size=n_nodes)

    nodes_null_df = pd.DataFrame({
        "id": node_ids,
        "pos_x": xs,
        "pos_y": ys,
        "pos_z": zs,
    })

    # 2) Random connections (simple graph, no self-loops, no duplicates)
    # Maximum edges possible in simple graphs:
    if directed:
        max_edges = n_nodes * (n_nodes - 1)  # ordered pairs excluding self-loops
    else:
        max_edges = n_nodes * (n_nodes - 1) // 2  # unordered pairs

    if m_edges > max_edges:
        raise ValueError(f"Requested m_edges={m_edges} exceeds max_edges={max_edges} for a simple graph.")

    edges_set = set()
    u_list = []
    v_list = []

    # Efficient batching: oversample candidate pairs and keep uniques until full
    # This avoids O(m) python random draws for large m.
    while len(edges_set) < m_edges:
        remaining = m_edges - len(edges_set)
        # Oversample factor to reduce loops; tuneable
        batch = int(min(max(5 * remaining, 10_000), 2_000_000))

        u = rng.integers(0, n_nodes, size=batch, dtype=np.int64)
        v = rng.integers(0, n_nodes, size=batch, dtype=np.int64)

        mask = (u != v)
        u = u[mask]
        v = v[mask]

        if not directed:
            a = np.minimum(u, v)
            b = np.maximum(u, v)
            pairs = np.stack([a, b], axis=1)
        else:
            pairs = np.stack([u, v], axis=1)

        # sort by distance
        if p_dist:
            # obtain the nodes
            starts = pairs[:, 0]
            ends = pairs[:, 1]

            # Coordinate differences
            dx = xs[starts] - xs[ends]
            dy = ys[starts] - ys[ends]
            dz = zs[starts] - zs[ends]

            # Squared Euclidean distances (avoid sqrt for speed)
            dist2 = dx*dx + dy*dy + dz*dz

            # Sorting indices (ascending distance)
            order = np.argsort(dist2)

            # Sorted pairs -- we can add randomization if needed
            pairs_sorted = pairs[order]
        else:
            pairs_sorted = pairs.copy()

        # Add to set until filled
        for uu, vv in pairs_sorted:
            if len(edges_set) >= m_edges:
                break
            key = (int(uu), int(vv))
            if key not in edges_set:
                edges_set.add(key)
                u_list.append(node_ids[uu])
                v_list.append(node_ids[vv])

    u_arr = np.asarray(u_list, dtype=node_ids.dtype)
    v_arr = np.asarray(v_list, dtype=node_ids.dtype)

    # 3) Random radii from empirical distribution
    if "minRadiusAvg" not in df_edges_sel.columns:
        raise ValueError("df_edges_sel must contain column 'minRadiusAvg'")

    radii = df_edges_sel["minRadiusAvg"].to_numpy()
    radii = radii[np.isfinite(radii)]
    if radii.size == 0:
        raise ValueError("No finite values found in df_edges_sel['minRadiusAvg'].")

    if m_edges == len(radii):
        print("shuffle the values")
        sampled_radii = rng.permutation(radii)
        # print(sampled_radii)
    else:
        sampled_radii = rng.choice(radii, size=m_edges, replace=True) # choose from the list without replacement

    edges_null_df = pd.DataFrame({
        "id": np.arange(m_edges, dtype=np.int64),
        "node1id": u_arr,
        "node2id": v_arr,
        "minRadiusAvg": sampled_radii,
    })

    # Build NetworkX graph (optional but convenient)
    G_null = nx.DiGraph() if directed else nx.Graph()

    # Add nodes with positions
    # (using tuples for Plotly + downstream analysis)
    for nid, x, y, z in zip(nodes_null_df["id"].values, xs, ys, zs):
        G_null.add_node(int(nid), pos=(float(x), float(y), float(z)))

    # Add edges with radius attribute
    for uu, vv, rr in zip(edges_null_df["node1id"].values, edges_null_df["node2id"].values, sampled_radii):
        G_null.add_edge(int(uu), int(vv), minRadiusAvg=float(rr))

    return nodes_null_df, edges_null_df, G_null


def generate_radii_null_model(m_edges: int, df_edges_sel: pd.DataFrame, df_nodes_sel: pd.DataFrame,
                              directed: bool = False, seed: Optional[int] = None):
    """
    Generate a spatial null model:
      - edge attribute 'minRadiusAvg' sampled from empirical distribution in df_edges_sel['minRadiusAvg']

    Parameters
    ----------
    m_edges : int
        Number of edges to generate (will error if too large for simple graph).
    df_edges_sel : pd.DataFrame
        Empirical edges dataframe containing column 'minRadiusAvg'.
    df_nodes_sel : pd.DataFrame
        Nodes nodes dataframe.
    directed : bool
        If True, generate directed edges (u->v). If False, undirected edges.
    seed : int or None
        RNG seed.

    Returns
    -------
    edges_null_df : pd.DataFrame
        Columns: id, node1id, node2id, minRadiusAvg
    G_null : nx.Graph or nx.DiGraph
        NetworkX graph with node positions and edge radii.
    """
    rng = np.random.default_rng(seed)

    # shuffle the radius 
    if "minRadiusAvg" not in df_edges_sel.columns:
        raise ValueError("df_edges_sel must contain column 'minRadiusAvg'")

    radii = df_edges_sel["minRadiusAvg"].to_numpy()
    radii = radii[np.isfinite(radii)]
    if radii.size == 0:
        raise ValueError("No finite values found in df_edges_sel['minRadiusAvg'].")

    if m_edges == len(radii):
        print("Shuffle the values")
        sampled_radii = rng.permutation(radii)
        # print(sampled_radii)
    else:
        print("Sample {} values from {} radii".format(m_edges, len(radii)))
        sampled_radii = rng.choice(radii, size=m_edges, replace=True) # choose from the list without replacement

    edges_null_df =  df_edges_sel.copy()
    edges_null_df["minRadiusAvg"] = sampled_radii

    # Build NetworkX graph (optional but convenient)
    G_null = nx.DiGraph() if directed else nx.Graph()

    # Add nodes with positions
    # (using tuples for Plotly + downstream analysis)
    for nid, x, y, z in zip(df_nodes_sel["id"].values,
                            df_nodes_sel["pos_x"].values, df_nodes_sel["pos_y"].values, df_nodes_sel["pos_z"].values):
        G_null.add_node(int(nid), pos=(float(x), float(y), float(z)))

    # Add edges with radius attribute
    for uu, vv, rr in zip(edges_null_df["node1id"].values, edges_null_df["node2id"].values, sampled_radii):
        G_null.add_edge(int(uu), int(vv), minRadiusAvg=float(rr))

    return edges_null_df, G_null
