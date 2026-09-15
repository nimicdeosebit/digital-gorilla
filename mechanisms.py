"""
mechanisms.py - the update rules that make capability depend on the state of the world, rather than being fixed. These are the mechanisms that make the model dynamic, and they are all taken from the paper (Sec. 3.1.1). They are off by default, so that each one can be switched on alone and measured against the flat baseline.


Mechanism 1: EPISTEMIC SPILLOVER  (paper Sec. 3.1.1)
    An actor's share of the epistemic modality raises its capability in the
    other four. Holding the facts, the data and the means of knowing makes an
    actor more effective at converting effort into money, authority, narrative
    and force.
"""

import numpy as np
from state import N, M, EPIS
from config import GAIN, SELF_GAIN


def spillover(P, gain=GAIN, self_gain=SELF_GAIN):
    """Capability matrix (N x M) given the current power shares P.

        capability[i, m] = 1 + gain * P[i, EPIS]        for m != EPIS
        capability[i, EPIS] = 1 + self_gain * P[i, EPIS]

    At gain = self_gain = 0 this returns all ones, i.e. exactly the flat
    baseline, so the wiring can be checked against the old behaviour.

    The paper's Sec. 3.1.1 describes this as "epistemic spillover": an actor's
    share of the epistemic modality raises its capability in the other four.
    Holding the facts, the data and the means of knowing makes an actor more
    effective at converting effort into money, authority, narrative and force.
    """
    edge = P[:, EPIS][:, None]                    # N x 1, each actor's epistemic share
    C = 1.0 + gain * np.tile(edge, (1, M))
    C[:, EPIS] = 1.0 + self_gain * P[:, EPIS]
    return C


if __name__ == "__main__":
    from state import initial_state, ACTORS, MODALITIES
    from agents import show

    P = initial_state()
    show(spillover(P, gain=0.0), "capability at GAIN=0 (must be all ones)")
    show(spillover(P, gain=1.0), "capability at GAIN=1")

    assert np.allclose(spillover(P, 0.0, 0.0), 1.0), "gain=0 must give flat capability"
    assert np.allclose(spillover(P, 1.0, 0.0)[:, EPIS], 1.0), "epistemic column must be unboosted"
    print("\nchecks passed")
