"""
This module defines the state of the model as a 4x5 matrix of power shares. The rows are actors (People, State, Enterprise, AI) and the columns are modalities (Economic, Epistemic, Narrative, Authoritative, Physical). The values are taken from Parra-Orlandoni et al. (2026, Sec. 3.1.1). The module also provides functions to normalise the matrix, check its validity, and display it in a readable format.
"""

import numpy as np

ACTORS = ["People", "State", "Enterprise", "AI"]
MODALITIES = ["Economic", "Epistemic", "Narrative", "Authoritative", "Physical"]

N = len(ACTORS)       # 4
M = len(MODALITIES)   # 5

# Define constants for indexing actors and modalities
PEOPLE, STATE, ENTERPRISE, AI = range(N)
ECON, EPIS, NARR, AUTH, PHYS = range(M)


def normalise(P):
    """Force every column to sum to 1. This is the model's one invariant."""
    return P / P.sum(axis=0, keepdims=True)


def initial_state():
    """Return the initial state of the model, as a 4x5 matrix of power shares. The rows are actors and the columns are modalities. The values are taken from Parra-Orlandoni et al. (2026, Sec. 3.1.1). """
    P = np.array([
        # Econ  Epis  Narr  Auth  Phys
        [0.18, 0.18, 0.28, 0.30, 0.10],   # People
        [0.27, 0.22, 0.17, 0.50, 0.62],   # State
        [0.45, 0.30, 0.30, 0.13, 0.20],   # Enterprise
        [0.10, 0.30, 0.25, 0.07, 0.08],   # AI
    ], dtype=float)
    return normalise(P)


def check(P):
    """Check that the matrix is the right shape, non-negative, and every column sums to 1."""
    assert P.shape == (N, M), f"expected {N}x{M}, got {P.shape}"
    assert (P >= 0).all(), "negative power share"
    sums = P.sum(axis=0)
    assert np.allclose(sums, 1.0), f"columns must sum to 1, got {sums}"


def show(P, title=""):
    """Display the matrix in a readable way, with actors as rows and modalities as columns."""
    if title:
        print(f"\n{title}")
    print(f"{'':<12}" + "".join(f"{m:>14}" for m in MODALITIES))
    for i, a in enumerate(ACTORS):
        print(f"{a:<12}" + "".join(f"{v:>14.3f}" for v in P[i]))
    print(f"{'sum':<12}" + "".join(f"{s:>14.3f}" for s in P.sum(axis=0)))


if __name__ == "__main__":
    P = initial_state()
    check(P)
    show(P, "Initial state")
    print("\nchecks passed: 4x5, non-negative, every column sums to 1")
