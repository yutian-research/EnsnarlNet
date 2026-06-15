"""Incomplete Gauss linking integral between line segments."""

import numpy as np


def Gauss_linking_integral(a, b):
    """
    a:tuple; elements are head and tail
    of line segment, each is a (3,) array representing the xyz coordinate.
    """
    # a0, a1 = a[0],a[1]
    # b0, b1 = b[0],b[1]

    R = np.empty((2, 2), dtype=tuple)
    for i in range(2):
        for j in range(2):
            R[i, j] = a[i] - b[j]

    n = []
    cprod = []

    cprod.append(np.cross(R[0, 0], R[0, 1]))
    cprod.append(np.cross(R[0, 1], R[1, 1]))
    cprod.append(np.cross(R[1, 1], R[1, 0]))
    cprod.append(np.cross(R[1, 0], R[0, 0]))

    for c in cprod:
        n.append(c / (np.linalg.norm(c) + 1e-6))

    area1 = np.arcsin(np.dot(n[0], n[1]))
    area2 = np.arcsin(np.dot(n[1], n[2]))
    area3 = np.arcsin(np.dot(n[2], n[3]))
    area4 = np.arcsin(np.dot(n[3], n[0]))

    sign = np.sign(np.cross(a[1] - a[0], b[1] - b[0]).dot(a[0] - b[0]))
    Area = area1 + area2 + area3 + area4

    return (sign * Area)/(4.*np.pi)
