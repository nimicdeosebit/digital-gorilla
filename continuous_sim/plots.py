import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from state import ACTORS, MODALITIES, N, EPIS, AI, initial_state
from agents import score, effort
from contest import step
from mechanisms import spillover, TARGET_SETS
from metrics import aspiration, stability
from config import ROUNDS, SPILLOVER_TARGETS, GAIN

FIGDIR = Path(__file__).resolve().parent.parent / "figures"; FIGDIR.mkdir(exist_ok=True)
BLUE, ORANGE, GREEN, PURPLE = "#2a78d6", "#eb6834", "#1baf7a", "#8c5ec4"
GREY = "#cccccc"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False})


def run(rule, gain=None, targets=SPILLOVER_TARGETS):
    """One run. Scores are recomputed every round: capability depends on the state.
    gain=None uses GAIN from config; pass a number to sweep it."""
    P = initial_state()
    F = (lambda P: score(P)) if gain is None else (lambda P: effort() * spillover(P, gain, targets=targets))
    return np.array([(P := step(P, F(P), rule=rule)) for _ in range(ROUNDS)])


def save(fig, fname):
    fig.tight_layout(); fig.savefig(FIGDIR / fname, dpi=200); plt.close(fig)
    print("wrote figures/" + fname)


def fig_rules(fname="fig1_rule_comparison.png"):
    fig, ax = plt.subplots(figsize=(5, 3))
    for colour, rule in ((BLUE, "tullock"), (ORANGE, "replicator")):
        ax.plot(run(rule).max(axis=1).mean(axis=1), color=colour, lw=2, label=rule)
    ax.axhline(1 / N, color=GREY, ls="--", lw=1)
    ax.set(ylim=(0, 1), xlabel="round", ylabel="leader share")
    ax.legend(frameon=False)
    save(fig, fname)


def fig_quadrant(points, fname="fig2_quadrant.png"):
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.axvline(.5, color=GREY, lw=1); ax.axhline(.5, color=GREY, lw=1)
    for (label, P), colour in zip(points, (BLUE, ORANGE, GREEN)):
        ax.plot(aspiration(P), stability(P), "o", ms=8, color=colour, label=label)
    ax.set(xlim=(0, 1), ylim=(0, 1), xlabel="aspiration", ylabel="stability")
    ax.legend(frameon=False, loc="upper left")
    save(fig, fname)


def fig_matrix(P, fname="fig3_matrix.png"):
    fig, ax = plt.subplots(figsize=(5.6, 2.6))
    ax.imshow(P, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    for (i, j), v in np.ndenumerate(P):
        ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                color="white" if v > .55 else "black")
    ax.set(xticks=range(len(MODALITIES)), xticklabels=MODALITIES,
           yticks=range(len(ACTORS)), yticklabels=ACTORS)
    save(fig, fname)


def fig_spillover(gains=(0, 1, 2, 4, 6, 8), fname="fig4_spillover.png",
                  targets=SPILLOVER_TARGETS):
    """Each actor's mean share across the modalities spillover boosts."""
    cols = TARGET_SETS[targets]
    ends = np.array([run("tullock", gain=g, targets=targets)[-1][:, cols].mean(axis=1)
                     for g in gains])
    fig, ax = plt.subplots(figsize=(5, 3))
    for i, colour in enumerate((BLUE, ORANGE, GREEN, PURPLE)):
        ax.plot(gains, ends[:, i], "o-", ms=4, color=colour, lw=2, label=ACTORS[i])
    ax.axhline(1 / N, color=GREY, ls="--", lw=1)
    ax.set(xlabel="spillover gain", ylabel=f"mean share, {targets} boosted modalities")
    ax.legend(frameon=False, ncol=2, fontsize=8)
    save(fig, fname)


def fig_targets(gains=np.arange(0, 12.01, 0.5), fname="fig5_targets.png"):
    """Does the reading of one sentence change the conclusion?

    AI's mean share across the four non-epistemic modalities, under both
    readings of where spillover lands. Same columns averaged in both curves,
    so the two are comparable.
    """
    cols = [j for j in range(len(MODALITIES)) if j != EPIS]
    fig, ax = plt.subplots(figsize=(5, 3))
    for colour, name, label in ((BLUE, "three", "three targets (paper's list)"),
                                (ORANGE, "four", "four targets (incl. narrative)")):
        ys = [run("tullock", gain=g, targets=name)[-1][AI, cols].mean() for g in gains]
        ax.plot(gains, ys, color=colour, lw=2, label=label)
    ax.axhline(1 / N, color=GREY, ls="--", lw=1)
    ax.set(xlabel="spillover gain", ylabel="AI mean share (non-epistemic)")
    ax.legend(frameon=False, fontsize=8)
    save(fig, fname)


if __name__ == "__main__":
    fig_rules()
    fig_quadrant([("start", initial_state()),
                  ("tullock", run("tullock")[-1]),
                  ("replicator", run("replicator")[-1])])
    fig_matrix(run("tullock")[-1])
    fig_spillover()
    fig_targets()
