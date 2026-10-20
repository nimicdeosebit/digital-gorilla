"""
mechanisms.py - the rules that make capability depend on the state of the world,
rather than being fixed. All taken from the paper, all off by default, so each
can be switched on alone and measured against the flat baseline.

Mechanism 1: EPISTEMIC SPILLOVER (Sec. 3.1.1)
    Holding the facts and the data makes an actor more effective elsewhere.

    Which modalities it lands in is a reading of the source, not a fact about
    it, so both readings are kept and selectable (see TARGET_SETS below).
"""

import numpy as np
from state import N, M, ECON, EPIS, NARR, AUTH, PHYS
from config import GAIN, SELF_GAIN, SPILLOVER_TARGETS

# Two readings of where spillover lands.
#
#   "three"  the modalities the paper actually enumerates: "custody of data and
#            knowledge gives economic advantage through market intelligence
#            ... authoritative influence ... and physical capability"
#            (Sec. 3.1.1). Narrative is absent from that list.
#
#   "four"   also narrative, on the looser phrasing in the neighbouring
#            sentences: "spills over into other modalities", "amplifies
#            downstream power across the system".
#
# The choice changes a headline result, so it is a parameter rather than a
# decision buried in the code. See fig5 for the comparison.
TARGET_SETS = {
    "three": [ECON, AUTH, PHYS],
    "four":  [ECON, NARR, AUTH, PHYS],
}


def spillover(P, gain=GAIN, self_gain=SELF_GAIN, targets=SPILLOVER_TARGETS):
    """Capability (N x M) given the current shares P.

        boosted modalities : 1 + gain * P[i, EPIS]
        epistemic          : 1 + self_gain * P[i, EPIS]
        everything else    : 1

    At gain = self_gain = 0 every entry is 1, the flat baseline, whichever
    target set is selected.

    Epistemic does not boost itself. The paper calls it "an upstream modality
    that quietly amplifies downstream power across the system" -- it runs one
    way, out of epistemic. (We also expected self-boost to run away like the
    replicator. Tested: it does not. The feedback is bounded, 1 + s*P with
    P <= 1, and the contest absorbs it.)
    """
    # Shape is taken from P, not from the module constants, so the same
    # mechanism works for a three-actor run with AI removed.
    C = np.ones(P.shape)
    C[:, TARGET_SETS[targets]] = 1.0 + gain * P[:, EPIS][:, None]
    C[:, EPIS] = 1.0 + self_gain * P[:, EPIS]
    return C


if __name__ == "__main__":
    from state import initial_state, MODALITIES
    from agents import show

    P = initial_state()
    for name in TARGET_SETS:
        show(spillover(P, gain=1.0, targets=name), f"capability at GAIN=1, targets={name!r}")

    assert np.allclose(spillover(P, 0.0, 0.0), 1.0), "gain=0 must be flat"
    assert np.allclose(spillover(P, 1.0, 0.0, "three")[:, [EPIS, NARR]], 1.0), \
        "three: epistemic and narrative must be unboosted"
    assert np.allclose(spillover(P, 1.0, 0.0, "four")[:, EPIS], 1.0), \
        "four: epistemic must be unboosted"
    assert not np.allclose(spillover(P, 1.0, 0.0, "four")[:, NARR], 1.0), \
        "four: narrative must be boosted"
    print("\nchecks passed")
