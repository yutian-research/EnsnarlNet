
import numpy as np
import networkx as nx

def generate_periodic_lattices(n_periods, thres=1., tol=1e-4):
    """Generate two interlaced periodic 3D lattices with a given number of periods
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

### Create spatial networks
num_periods = 1
G1, G2 = generate_periodic_lattices(num_periods)