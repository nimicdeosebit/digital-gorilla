"""
metrics.py -- scoring an end state on the paper's Aspiration-Stability matrix
(Parra-Orlandoni et al. 2026, Sec. 4.3, Table 8).

Two questions:
    stability   can the system hold together?      -> is anyone dominating?
    aspiration  is it worth holding together?      -> do People still hold a share?

Both are normalised so that an even split among however many actors there are
maps to a fixed value. That keeps a 3-actor run comparable with a 4-actor one.
"""

import numpy as np


def hhi(P):
    """Herfindahl-Hirschman index per modality: sum of squared shares.

    The paper suggests market concentration indices as a stability measure
    (Sec. 4.6), so this is its own choice rather than ours. Ranges from 1/N
    (perfectly even) to 1 (one actor holds everything).
    """
    return (P ** 2).sum(axis=0)


def stability(P):
    """1 = power evenly spread in every modality, 0 = every modality captured.

    Computed per modality and then averaged, so an actor owning two modalities
    registers even when its overall share looks moderate.
    """
    n = P.shape[0]
    even = 1.0 / n                      # HHI of a perfectly even split
    s = 1.0 - (hhi(P) - even) / (1.0 - even)
    return float(np.clip(s.mean(), 0.0, 1.0))


def aspiration(P, weights=None):
    """People's share of power, scaled so an even split maps to 0.5.

    UNWEIGHTED by default: every modality counts the same. The paper's notion
    of aspiration is wider than this (Sec. 4.3 gives four components, of which
    only opportunity distribution is really about how power is spread), so this
    is a proxy for one part of it and should be described as such.

    Passing `weights` up-weights some modalities over others. That is a value
    judgement about what human agency rests on, so it is off by default and
    belongs in the sensitivity analysis if used.
    """
    n = P.shape[0]
    people = P[0]
    val = float(np.average(people, weights=weights))
    return float(np.clip(val / (2.0 / n), 0.0, 1.0))


def quadrant(P, mid=0.5, weights=None):
    """Which quadrant of Table 8. Numbering follows the paper exactly:

        I    high stability, low  aspiration -- Surviving not Thriving
        II   high stability, high aspiration -- High Potential   (the target)
        III  low  stability, high aspiration -- Creative Chaos
        IV   low  stability, low  aspiration -- Fragile Collapse
    """
    a, s = aspiration(P, weights), stability(P)
    if s >= mid and a >= mid:
        return "II  High Potential (target)"
    if s >= mid and a < mid:
        return "I   Surviving not Thriving"
    if s < mid and a >= mid:
        return "III Creative Chaos"
    return "IV  Fragile Collapse"


def report(P, label=""):
    print(f"{label:<28}aspiration={aspiration(P):.3f}  "
          f"stability={stability(P):.3f}   {quadrant(P)}")


if __name__ == "__main__":
    from state import initial_state, N, M
    from agents import score
    from contest import step
    from config import ROUNDS

    print("Sanity checks -- do the metrics behave as they should?\n")

    even = np.full((N, M), 1.0 / N)
    report(even, "perfectly even split")

    captured = np.zeros((N, M)); captured[3] = 1.0          # AI owns everything
    report(captured, "AI owns everything")

    people_own = np.zeros((N, M)); people_own[0] = 1.0      # People own everything
    report(people_own, "People own everything")

    print()
    P = initial_state()
    report(P, "initial state")
    for _ in range(ROUNDS):
        P = step(P, score())
    report(P, f"after {ROUNDS} rounds")
