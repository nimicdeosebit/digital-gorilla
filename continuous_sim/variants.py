"""Running the continuous model with a subset of the actors.

The project's original question -- does AI as a fourth actor change the
dynamics -- needs a baseline without AI to compare against. Nothing else in
the model has to change: the contest rule, the spillover mechanism and the
metrics are all written over whatever matrix they are given.

One thing does NOT carry across actor counts: `metrics.aspiration` divides
People's share by 2/n, so a three-actor run and a four-actor run are scored
against different bars. Raw People share is reported alongside it here, and
that is the comparison to quote.
"""

import numpy as np

from state import ACTORS, MODALITIES, normalise, initial_state
from agents import PRIORITIES
from contest import step
from mechanisms import spillover
from metrics import aspiration, stability, quadrant, hhi
from config import ROUNDS, GAIN, SPILLOVER_TARGETS


def subset(actors):
    """Indices of `actors` within the full ACTORS list, in canonical order."""
    return [ACTORS.index(a) for a in actors]


def initial_state_for(actors):
    """The initial matrix restricted to `actors`, columns renormalised to 1.

    Removing an actor and renormalising spreads its share over the others in
    proportion to what they already hold. That keeps the paper's ordering and
    introduces no new claim about who would have held AI's share instead.
    """
    return normalise(initial_state()[subset(actors)])


def priorities_for(actors):
    """Effort priorities restricted to `actors`, rows renormalised to 1."""
    E = PRIORITIES[subset(actors)]
    return E / E.sum(axis=1, keepdims=True)


def run_variant(actors, rule="tullock", gain=GAIN, targets=SPILLOVER_TARGETS,
                rounds=ROUNDS):
    """Run the continuous model with just `actors`. Returns the final matrix."""
    P = initial_state_for(actors)
    E = priorities_for(actors)
    for _ in range(rounds):
        P = step(P, E * spillover(P, gain, targets=targets), rule=rule)
    return P


def report(actors, **kwargs):
    P = run_variant(actors, **kwargs)
    n = len(actors)
    people = float(P[0].mean())
    return {
        "actors": f"{n} actors",
        "names": ", ".join(actors),
        "people_share": people,
        "people_vs_even": people / (1.0 / n),
        "aspiration": aspiration(P),
        "stability": stability(P),
        "leader_share": float(P.max(axis=0).mean()),
        "mean_hhi": float(hhi(P).mean()),
        "quadrant": quadrant(P),
        "P": P,
    }


FOUR = list(ACTORS)
THREE = ["People", "State", "Enterprise"]


if __name__ == "__main__":
    print("Continuous model, with and without AI\n")
    header = (f"{'run':<10}{'People':>9}{'vs even':>9}{'aspir.':>9}"
              f"{'stab.':>8}{'leader':>8}{'HHI':>7}  quadrant")
    print(header)
    print("-" * len(header))

    rows = []
    for actors in (THREE, FOUR):
        for gain in (0.0, 4.0):
            r = report(actors, gain=gain)
            rows.append((gain, r))
            print(f"{r['actors']:<10}{r['people_share']:>9.3f}"
                  f"{r['people_vs_even']:>9.3f}{r['aspiration']:>9.3f}"
                  f"{r['stability']:>8.3f}{r['leader_share']:>8.3f}"
                  f"{r['mean_hhi']:>7.3f}  gain={gain:g}  {r['quadrant']}")

    print("\nNote: `aspiration` normalises by 2/n, so it is NOT comparable")
    print("across actor counts. Compare `People` (raw share) or `vs even`.")
