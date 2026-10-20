"""Does modelling AI as a separate fourth actor change anything?

This is the test of the source paper's foundational move. The paper adds AI to
the three societal actors of the older literature; whether that addition does
any work is a question the model can answer, and until now it had never been
run.

THE MERGE HAS TO BE FAIR
------------------------
Removing AI by deleting its row and renormalising the column is not a control.
It takes capability out of the system as well as taking an actor out, so any
difference it produces says only that four actors hold more power between them
than three do. Nothing is learned.

A fair merge folds AI into Enterprise and gives the merged actor what both of
them had: the sum of their shares, and their effort priorities averaged in
proportion to how much power each one brought. The number of actors changes;
the capability and the behaviour in the system do not. Anything that differs
afterwards is caused by the separation itself.

(The idea is taken from `three_vs_four.py` in an earlier prototype of this
project. That prototype's own results are not reusable -- it gave AI an
exogenous logistic capability curve, so AI's rise was assumed rather than
derived -- but this part of its design was right.)

Three conditions, in both models:

    4A          four actors
    3A-merged   Enterprise and AI merged, conserving shares and behaviour
    3A-dropped  AI deleted and columns renormalised -- the unfair control,
                kept so the difference between the two merges is visible

Run:  python3 comparison.py
"""

import math
import sys
from pathlib import Path
from statistics import mean, stdev

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "continuous_sim"))

from state import ACTORS, MODALITIES, initial_state, normalise   # noqa: E402
from agents import PRIORITIES                                     # noqa: E402
from contest import step                                          # noqa: E402
from mechanisms import spillover                                  # noqa: E402
from metrics import aspiration, stability, hhi, quadrant          # noqa: E402
from config import ROUNDS, SPILLOVER_TARGETS                      # noqa: E402

PEOPLE, STATE, ENTERPRISE, AI = range(4)
CONDITIONS = ("4A", "3A-merged", "3A-dropped")


# ===========================================================================
# continuous model
# ===========================================================================
def setup_continuous(condition):
    """Return (P0, effort, actor names) for one condition."""
    P = initial_state()
    E = PRIORITIES / PRIORITIES.sum(axis=1, keepdims=True)

    if condition == "4A":
        return P, E, list(ACTORS)

    if condition == "3A-dropped":
        keep = [PEOPLE, STATE, ENTERPRISE]
        return (normalise(P[keep]),
                E[keep] / E[keep].sum(axis=1, keepdims=True),
                ["People", "State", "Enterprise"])

    if condition == "3A-merged":
        # Shares add, so the merged actor holds exactly what the two held.
        merged_P = np.vstack([P[PEOPLE], P[STATE], P[ENTERPRISE] + P[AI]])

        # Effort priorities are averaged in proportion to the power each actor
        # brought to the merge, so the behavioural mix is conserved too.
        w_ent = float(P[ENTERPRISE].mean())
        w_ai = float(P[AI].mean())
        blended = (w_ent * E[ENTERPRISE] + w_ai * E[AI]) / (w_ent + w_ai)
        merged_E = np.vstack([E[PEOPLE], E[STATE], blended])

        return (normalise(merged_P),
                merged_E / merged_E.sum(axis=1, keepdims=True),
                ["People", "State", "Enterprise+AI"])

    raise ValueError(condition)


def run_continuous(condition, gain=0.0, rule="tullock", rounds=ROUNDS,
                   targets=SPILLOVER_TARGETS):
    P, E, names = setup_continuous(condition)
    for _ in range(rounds):
        P = step(P, E * spillover(P, gain, targets=targets), rule=rule)
    n = len(names)
    people = float(P[PEOPLE].mean())
    return {
        "condition": condition,
        "names": names,
        "n": n,
        "P": P,
        "people": people,
        "people_vs_even": people * n,
        "aspiration": aspiration(P),
        "stability": stability(P),
        "leader": float(P.max(axis=0).mean()),
        "hhi": float(hhi(P).mean()),
        "quadrant": quadrant(P),
    }


# ===========================================================================
# action model
# ===========================================================================
def _action_weights():
    """Enterprise's and AI's share of the merged actor, from Table 4."""
    from action_based_sim.tables import INITIAL_POWER
    ent = mean(INITIAL_POWER[m]["Enterprises"] for m in MODALITIES)
    ai = mean(INITIAL_POWER[m]["AI"] for m in MODALITIES)
    return ent / (ent + ai), ai / (ent + ai)


class _AliasView:
    """Read-only view of a State in which one extra name points at a real
    actor. Used so that policies written against a four-actor world still
    resolve when two of those actors have been merged into one.

    Policies only read, so a shallow view is enough; the real State is what
    the actions are applied to.
    """

    def __init__(self, state, alias, real):
        self._state = state
        self.actors = list(state.actors) + [alias]
        self.P = {m: {**state.P[m], alias: state.P[m][real]}
                  for m in state.P}
        self.L = {**state.L, alias: state.L[real]}

    def __getattr__(self, name):
        return getattr(self._state, name)


def run_action(condition, seed, **overrides):
    """One run of the action model under one condition.

    The merge is done by behaviour rather than by averaging a vector, because
    the policies are discrete: on each tick the merged actor acts as Enterprise
    with probability w_ent and as AI with probability w_ai. Over a run that
    reproduces the same mix of behaviour the two actors would have produced
    separately, which is the discrete equivalent of blending their priorities.
    """
    from action_based_sim import policies
    from action_based_sim.config import SimulationConfig
    from action_based_sim.environment import Environment

    kwargs = dict(enhance_mode="per_capita", **overrides)

    if condition == "4A":
        env = Environment(SimulationConfig(seed=seed, **kwargs))
    elif condition == "3A-dropped":
        env = Environment(SimulationConfig(
            seed=seed, actors=["People", "State", "Enterprises"], **kwargs))
    elif condition == "3A-merged":
        from action_based_sim.actions import ActionType
        from action_based_sim.tables import INITIAL_POWER

        w_ent, _ = _action_weights()
        env = Environment(SimulationConfig(
            seed=seed, actors=["People", "State", "Enterprises"], **kwargs))

        # Fold AI's shares into Enterprises rather than renormalising them
        # away. These still sum to 1 per modality, since nothing left.
        for m in MODALITIES:
            env.state.P[m] = {
                "People": INITIAL_POWER[m]["People"],
                "State": INITIAL_POWER[m]["State"],
                "Enterprises": (INITIAL_POWER[m]["Enterprises"]
                                + INITIAL_POWER[m]["AI"]),
            }

        original_decide = policies.decide

        def merged_decide(actor_name, state, config, rng):
            """Decide against a view of the state in which "AI" names the
            merged actor, so the other actors' Table 6 checks against AI still
            land somewhere, then translate the action back."""
            view = _AliasView(state, alias="AI", real="Enterprises")
            if actor_name == "Enterprises":
                # Act as the firm w_ent of the time and as AI the rest, which
                # reproduces the behavioural mix of the two separate actors.
                pick = "Enterprises" if rng.random() < w_ent else "AI"
                action = policies._POLICIES[pick](view, config, rng)
                action.actor = "Enterprises"
            else:
                action = original_decide(actor_name, view, config, rng)
            if action.target == "AI":
                action.target = "Enterprises"
            if action.target == action.actor:
                # A merged actor cannot check itself.
                return policies.Action(ActionType.ABSTAIN, actor=action.actor)
            return action

        policies.decide = merged_decide
        try:
            env.run()
        finally:
            policies.decide = original_decide
        return _action_result(env, condition)
    else:
        raise ValueError(condition)

    env.run()
    return _action_result(env, condition)


def _action_result(env, condition):
    final = env.history[-1]
    people = mean(final["state"]["P"][m]["People"] for m in MODALITIES)
    n = len(env.state.actors)
    return {
        "condition": condition,
        "people": people,
        "people_vs_even": people * n,
        "aspiration": final["aspiration"],
        "stability": final["stability"],
        "quadrant": final["quadrant"],
    }


def ci95(xs):
    return 1.96 * stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else 0.0


def action_batch(condition, n_seeds=200, **overrides):
    runs = [run_action(condition, s, **overrides) for s in range(n_seeds)]
    out = {"condition": condition, "n": n_seeds}
    for key in ("people", "people_vs_even", "aspiration", "stability"):
        vals = [r[key] for r in runs]
        out[key] = mean(vals)
        out[key + "_ci"] = ci95(vals)
    out["quadrant_II"] = sum(
        r["quadrant"].startswith("II") for r in runs) / n_seeds
    return out


# ===========================================================================
# report
# ===========================================================================
def main():
    print("=" * 76)
    print("CONTINUOUS MODEL")
    print("=" * 76)
    for gain in (0.0, 4.0):
        print(f"\nspillover gain = {gain:g}")
        print(f"{'condition':<13}{'People':>9}{'vs even':>9}{'aspir.':>9}"
              f"{'stab.':>8}{'leader':>8}{'HHI':>7}")
        print("-" * 63)
        for cond in CONDITIONS:
            r = run_continuous(cond, gain=gain)
            print(f"{cond:<13}{r['people']:>9.4f}{r['people_vs_even']:>9.4f}"
                  f"{r['aspiration']:>9.3f}{r['stability']:>8.3f}"
                  f"{r['leader']:>8.3f}{r['hhi']:>7.3f}")

    print()
    print("=" * 76)
    print("ACTION MODEL  (200 seeds, per-capita ENHANCE)")
    print("=" * 76)
    for ratio in (1.0, 3.0):
        print(f"\ncheck / enhance ratio = {ratio:g}")
        print(f"{'condition':<13}{'People':>18}{'vs even':>18}{'High Potential':>16}")
        print("-" * 67)
        for cond in CONDITIONS:
            r = action_batch(cond, check_magnitude=0.10 * ratio)
            print(f"{cond:<13}"
                  f"{r['people']:>11.4f} +/-{r['people_ci']:.4f}"
                  f"{r['people_vs_even']:>11.4f} +/-{r['people_vs_even_ci']:.4f}"
                  f"{r['quadrant_II']:>15.0%}")

    print("\nRead `vs even`, not `People`: with three actors an even split is")
    print("0.333 and with four it is 0.250, so the raw shares are measured")
    print("against different bars. `vs even` is 1.0 when People hold exactly")
    print("an even share whatever the actor count.")


if __name__ == "__main__":
    main()
