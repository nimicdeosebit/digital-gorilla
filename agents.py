"""
agents.py -- what each actor chooses, and how much it is worth.

Two quantities, kept deliberately separate:

  effort      what the actor CHOOSES. One unit of resource split across the
              five modalities, so each row sums to 1. This is the only
              decision in the model.

  capability  how effective that actor IS in that modality, independent of
              what it chose. Not a decision.

  score = effort * capability

Nothing here updates the state. This file only produces the inputs to movement.
"""

import numpy as np
from state import N, M, ACTORS, MODALITIES, PEOPLE, STATE, ENTERPRISE, AI
from mechanisms import spillover

# ---------------------------------------------------------------------------
# EFFORT
# ---------------------------------------------------------------------------
# Each actor has institutional priorities -- where it naturally puts its
# resources. These are read off the paper's account of who manifests power
# where (Sec. 3.1.1, Table 4): People act through voice and consent, the State
# through law and force, Enterprise through markets, AI through information.
#
# NOTE this is a claim about INTERESTS, not about ability. Giving actors
# different priorities is theory-grounded. Giving one actor a growing
# capability advantage would not be -- see the capability section below.

PRIORITIES = np.array([
    # Econ  Epis  Narr  Auth  Phys
    [0.20, 0.15, 0.30, 0.30, 0.05],   # People      -- voice and consent
    [0.15, 0.15, 0.10, 0.35, 0.25],   # State       -- law and force
    [0.40, 0.25, 0.20, 0.10, 0.05],   # Enterprise  -- markets
    [0.15, 0.35, 0.30, 0.15, 0.05],   # AI          -- information
], dtype=float)


def effort(P=None, rng=None, noise=0.0):
    """Effort allocation for every actor: an N x M array, each row summing to 1.

    For now this is fixed: actors do not react to the state of the world.
    `P` is accepted but unused, so that a responsive rule can be swapped in
    later without changing any call site.
    """
    E = PRIORITIES.copy()
    if noise > 0 and rng is not None:
        E = E + noise * rng.random((N, M))
    return E / E.sum(axis=1, keepdims=True)


# ---------------------------------------------------------------------------
# CAPABILITY
# ---------------------------------------------------------------------------
def capability(P=None, t=0):
    """How effective each actor is in each modality: an N x M array.

    With no state passed, or with GAIN = 0 in config.py, everyone is equally
    capable everywhere: all ones.

    That flat baseline is on purpose. The previous prototype gave AI a
    capability that grew over time and was extra high in the information
    modalities, then reported as a finding that AI rises, in information
    first. That is circular. Any asymmetry has to be switched on explicitly
    and tested against the flat case.

    Given a state P, capability comes from mechanisms.spillover: an actor's
    epistemic share raises its capability in the other four modalities. This
    is the paper's claim (Sec. 3.1.1), not an assumption about any one actor.
    """
    if P is None:
        return np.ones((N, M))
    return spillover(P)


def score(P=None, t=0, rng=None, noise=0.0):
    """score = effort * capability."""
    return effort(P, rng, noise) * capability(P, t)


def show(A, title="", rowsum=False):
    print(f"\n{title}")
    print(f"{'':<12}" + "".join(f"{m:>14}" for m in MODALITIES))
    for i, a in enumerate(ACTORS):
        line = f"{a:<12}" + "".join(f"{v:>14.3f}" for v in A[i])
        if rowsum:
            line += f"{A[i].sum():>10.3f}"
        print(line)


if __name__ == "__main__":
    E = effort()
    C = capability()
    F = score()

    show(E, "Effort (what each actor chooses; rows sum to 1)", rowsum=True)
    show(C, "Capability (how effective each actor is)")
    show(F, "Score = effort x capability")

    assert np.allclose(E.sum(axis=1), 1.0), "effort rows must sum to 1"
    print("\ncheck passed: every actor spends exactly one unit of effort")
