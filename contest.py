"""
contest.py - the update rules.
Two candidate rules are implemented so they can be compared. 
The Tullock rule is the one used in the paper. The replicator rule is a
common alternative from evolutionary game theory, which is included for comparison. 
"""

import numpy as np
from state import normalise
from config import RATE, ROUNDS



def tullock(P, F, rate=RATE):
    """Contest success function (Tullock 1980), used in the economics of
    contests and rent-seeking.
        P <- (1 - rate) * P + rate * (F / sum(F))
    """
    target = F / F.sum(axis=0, keepdims=True)
    return (1.0 - rate) * P + rate * target


def replicator(P, F, rate=RATE):
    """Replicator equation from evolutionary game theory (Taylor & Jonker 1978).
    An actor's share grows if its score beats the share-weighted AVERAGE score
    in that modality, and the growth is proportional to the share it already
    holds.
        P <- P * (1 + rate * (F - Fbar) / Fbar)

    This is a common alternative to the Tullock rule, which is included for comparison. It has a stable interior equilibrium, but it is more sensitive
    to small differences in score than the Tullock rule, so it tends to produce more extreme outcomes.
    """
    fbar = (P * F).sum(axis=0, keepdims=True)
    fbar = np.maximum(fbar, 1e-12)
    return normalise(np.maximum(P * (1.0 + rate * (F - fbar) / fbar), 1e-9))


RULES = {"tullock": tullock, "replicator": replicator}


def step(P, F, rule="tullock", rate=RATE):
    """One round of contest, applied to every modality at once."""
    return normalise(RULES[rule](P, F, rate))


if __name__ == "__main__":
    from state import initial_state, check, show, ACTORS, MODALITIES
    from agents import score

    F = score()               # fixed, so any movement comes from the rule alone

    for rule in ("tullock", "replicator"):
        P = initial_state()
        for t in range(ROUNDS):
            P = step(P, F, rule=rule)
            check(P)           # invariant must hold at every single round
        show(P, f"After {ROUNDS} rounds -- {rule}")
        print(f"{'':<12}mean leader share = {P.max(axis=0).mean():.3f}"
              f"   (0.25 = balanced, 1.00 = one actor owns everything)")

    print("\nBoth rules ran the same number of rounds with identical scores and identical")
    print("starting state. The only difference is the update rule.")
