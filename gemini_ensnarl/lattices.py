"""Generators for the synthetic ensnarled lattices used in the paper."""

import numpy as np
import networkx as nx
from itertools import combinations


def generate_periodic_lattices(n_periods, thres=1., tol=1e-4):
    """Generate two ensnarled periodic 3D lattices with a given number of periods
    along the (1, 0, 1) direction.
    Params
    ------
        n_periods, int, number of periods to generate

    Returns:
        G_A, networkx.Graph for lattice A
        G_B, networkx.Graph for lattice B
    """
    from itertools import combinations

    # Define base units
    unit_A_base = np.array([[0, 0, 0], [0, 1, 0]])
    unit_A = np.array([
        [1, 0, 0],
        [1, 1, 0],
        [1, 0, 1],
        [1, 1, 1],
    ])
    unit_B_base = np.array([[0.5, 0.5, -0.5], [0.5, 1.5, -0.5]])
    unit_B = np.array([
        [0.5, 0.5, 0.5],
        [0.5, 1.5, 0.5],
        [1.5, 0.5, 0.5],
        [1.5, 1.5, 0.5]
    ])

    period_vec = np.array([1, 0, 1])

    G_A = nx.Graph()
    G_B = nx.Graph()

    pos_A = []
    node_id = 0
    # Add base vertices
    for point in unit_A_base:
        pos = tuple(point)
        G_A.add_node(node_id, pos=pos)
        pos_A.append((node_id, np.array(pos)))
        node_id += 1
    # Add unit vertices
    for i in range(n_periods):
        shift = i * period_vec
        for point in unit_A:
            pos = tuple(point + shift)
            G_A.add_node(node_id, pos=pos)
            pos_A.append((node_id, np.array(pos)))
            node_id += 1
    # Add edges in A based on distance
    for (i, pi), (j, pj) in combinations(pos_A, 2):
        if np.linalg.norm(pi - pj) <= thres+tol:
            G_A.add_edge(i, j)

    pos_B = []
    node_id = 0
    # Add base vertices
    for point in unit_B_base:
        pos = tuple(point)
        G_B.add_node(node_id, pos=pos)
        pos_B.append((node_id, np.array(pos)))
        node_id += 1
    # Add unit vertices
    for i in range(n_periods):
        shift = i * period_vec
        for point in unit_B:
            pos = tuple(point + shift)
            G_B.add_node(node_id, pos=pos)
            pos_B.append((node_id, np.array(pos)))
            node_id += 1

    # Add edges in A based on distance
    for (i, pi), (j, pj) in combinations(pos_B, 2):
        if np.linalg.norm(pi - pj) <= thres+tol:
            G_B.add_edge(i, j)

    return G_A, G_B


def generate_ladder_lattices(num_periods):
    """Generate the two ensnarled "catenation" ladder lattices.

    Self-contained replacement for the kirchhoff/goflow dual-circuit stack
    (``NetworkxDualCatenation``): builds a (``num_periods`` x 1) square grid,
    rotates it 90 degrees about the x-axis and offsets it by [0.5, 0.5, -0.5]
    (lattice ``G1``), and interlaces it with a flat (``num_periods`` + 1 x 1)
    square grid (lattice ``G2``). Nodes are integer-labelled in grid-insertion
    order; each carries a ``pos`` (x, y, z) attribute.

    This reproduces the original generator exactly (verified node-for-node and
    edge-for-edge against ``initialize_dual_from_catenation`` for
    ``num_periods`` in {1, 2, 3}).

    Params
    ------
        num_periods, int

    Returns
    ------
        G1, G2 : networkx.Graph
    """
    theta = np.pi / 2.
    rot = np.array([[1, 0, 0],
                    [0, np.cos(theta), -np.sin(theta)],
                    [0, np.sin(theta),  np.cos(theta)]])
    offset = np.array([0.5, 0.5, -0.5])

    def square_grid(nx_p, ny_p, transform=None):
        raw = {}
        G = nx.Graph()
        for x in range(nx_p + 1):
            for y in range(ny_p + 1):
                raw[(x, y)] = np.array([x, y, 0.], dtype=float)
                G.add_node((x, y))
        nodes = list(G.nodes())
        for i, n in enumerate(nodes):
            for m in nodes[i + 1:]:
                if np.linalg.norm(raw[n] - raw[m]) <= 1.:
                    G.add_edge(n, m)
        for n in G.nodes():
            p = raw[n]
            G.nodes[n]['pos'] = transform(p) if transform is not None else p
        return nx.relabel_nodes(G, {n: i for i, n in enumerate(G.nodes())})

    G1 = square_grid(num_periods, 1, transform=lambda p: rot.dot(p) + offset)
    G2 = square_grid(num_periods + 1, 1, transform=None)
    return G1, G2
