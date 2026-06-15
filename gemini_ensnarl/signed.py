"""Signed bipartite graph, signed biclustering analysis."""

import numpy as np
import networkx as nx


def build_sibigraph(B, labels_p1, labels_p2):
    """Build a signed bipartite graph from a matrix B (one - the other parts).
    Params
    ------
        B, np.ndarray (m x n), signed biadjacency matrix
        label_p1, list, labels for row nodes (set 1)
        label_p2, list, labels for column nodes (set 2)
    Returns
    ------
        G, networkx.Graph - with:
            - 'bipartite' node attribute (0 or 1)
            - 'weight' edge attribute (signed)
    """
    m, n = B.shape
    G = nx.Graph()

    # Add nodes in part 1 (rows)
    for i in range(m):
        node = labels_p1[i]
        G.add_node(node, bipartite=0)

    # Add nodes in part 2 (columns)
    for j in range(n):
        node = labels_p2[j]
        G.add_node(node, bipartite=1)

    # Add edges where B[i,j] ≠ 0
    for i in range(m):
        for j in range(n):
            weight = B[i, j]
            if weight != 0:
                u = labels_p1[i]
                v = labels_p2[j]
                G.add_edge(u, v, weight=weight)

    return G


def critical_flip_angles(u1, u2, eps=1e-8, deci=8):
    """Compute the distinct angles in [0, pi) at which some entry of a vector in the subspace spanned by the two eigenvectors,
    x(theta) = cos(theta)*u1 + sin(theta)*u2, changes sign.

    Params
    ------
    u1, u2, array (n,), the two eigenvectors (smallest eigenvalues of signed Laplacian).
    eps, float, threshold for ignoring nodes with (u1_i, u2_i) ~ (0,0).

    Returns
    ------
    flip_angles, ndarray (m,), sorted angles in [0, pi) where at least one coordinate crosses zero.
    nodes_deg, ndarray (k,), indices of nodes whose (u1_i, u2_i) are numerically ~0.
    """
    u1 = np.asarray(u1, dtype=float)
    u2 = np.asarray(u2, dtype=float)
    assert u1.shape == u2.shape

    # store nodes whose (u1_i, u2_i) are numerically ~0: extra attention is needed!
    norm2 = u1**2 + u2**2
    mask = norm2 > eps
    nodes_deg = np.where(norm2 <= eps)[0]
    if len(nodes_deg) > 0:
        print("zero values at:", nodes_deg)

    if not np.any(mask):
        # No flips, return empty array
        return np.array([]), nodes_deg

    psi = np.arctan2(u2[mask], u1[mask]) # choosing the quadrant correctly

    # Flip angle theta_i = psi_i + pi/2, reduced to [0, pi)
    theta = psi + 0.5 * np.pi
    theta = np.mod(theta, np.pi)

    # Deduplicate with some tolerance
    theta = np.unique(np.round(theta, decimals=deci)) # Careful: maybe more than one nodes have zero at the same time!

    return theta, nodes_deg


def candidate_mid_angles(flip_angles):
    """Given sorted flip angles in [0, pi), construct representative angles
    in each interval where the sign pattern is constant.

    Returns:
    ------
    numpy.array, representative angles in [0, pi).
    """
    if flip_angles.size == 0:
        # No flips: any theta works; choose 0.
        return np.array([0.0])

    flip_angles = np.sort(flip_angles)
    thetas = []

    # First interval: [0, flip_angles[0])
    thetas.append(0.5 * flip_angles[0])

    # Middle intervals: (flip_i, flip_{i+1})
    for a, b in zip(flip_angles[:-1], flip_angles[1:]):
        thetas.append(0.5 * (a + b))

    # Last interval: (flip_angles[-1], pi)
    thetas.append(0.5 * (flip_angles[-1] + np.pi))

    return np.array(thetas)


def sign_patterns_from_angles(u1, u2, angles):
    """Compute sign patterns s_i(theta) = sign( cos(theta)*u1_i + sin(theta)*u2_i )
    for a list of angles.

    Params
    -----
    u1, u2, array_like (n,)
    angles, array_like (m,)

    Returns
    ------
    S : ndarray, shape (n, m), S[:, j] is the sign pattern for angles[j].
    """
    u1 = np.asarray(u1, dtype=float)
    u2 = np.asarray(u2, dtype=float)
    angles = np.asarray(angles, dtype=float)

    cos_t = np.cos(angles)[None, :]  # shape (1, m)
    sin_t = np.sin(angles)[None, :]
    x = u1[:, None] * cos_t + u2[:, None] * sin_t  # shape (n, m)

    S = np.sign(x)
    # Treat zeros as +1?
    # S[S == 0] = 1
    return S
