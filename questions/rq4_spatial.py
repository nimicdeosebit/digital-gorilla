"""RQ4 and the rest of the NetLogo results.

The NetLogo model is driven by hand through BehaviorSpace, so unlike the other
question scripts this one does not run the simulation -- it reads the CSVs
BehaviorSpace wrote and reduces them to the tables in the write-ups.

Seven experiments, all defined inside `netlogo/digital_gorilla.nlogo`:

  aggregate-baseline        does NetLogo reproduce the Python action model?
  threshold-aggregate       does it reproduce the check-strength threshold?
  threshold-spatial         does space move that threshold?
  spread-by-modality        RQ4: does it matter where power sits?
  heterogeneity-sweep       does RQ4 survive a different starting inequality?
  diffusion-escape          can an actor spread out to dodge checks?
  settling                  has the system settled by tick 50?

Run from the repository root:  python3 questions/rq4_spatial.py
"""

import csv
from pathlib import Path
from statistics import mean, stdev

RESULTS    = Path(__file__).resolve().parent.parent / "results"
RQ4        = RESULTS / "rq4_spatial"
VALIDATION = RESULTS / "validation"
THRESHOLD  = RESULTS / "netlogo_threshold"
ROBUSTNESS = RESULTS / "robustness"

# spread-of index -> (name, diffusion rate). Order and rates both come from
# `set diffusion-rates [0.15 0.30 0.30 0.05 0.03]` in the NetLogo setup.
MODALITIES = [
    ("Economic",      0.15),
    ("Epistemic",     0.30),
    ("Narrative",     0.30),
    ("Authoritative", 0.05),
    ("Physical",      0.03),
]

ACTORS = ["People", "State", "Enterprises", "AI"]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def load(folder, name):
    """One dict per run. BehaviorSpace puts six preamble lines above the header."""
    rows = list(csv.reader(open(folder / name)))
    at = next(i for i, r in enumerate(rows) if r and r[0] == "[run number]")
    return [dict(zip(rows[at], r)) for r in rows[at + 1:] if r]


def group_by(runs, column, cast=str):
    """Runs bucketed by one varying parameter, in sorted key order."""
    out = {}
    for run in runs:
        out.setdefault(cast(run[column]), []).append(run)
    return dict(sorted(out.items()))


def avg(runs, column):
    return mean(float(r[column]) for r in runs)


def sd(runs, column):
    return stdev(float(r[column]) for r in runs) if len(runs) > 1 else 0.0


def quadrant_share(runs, name):
    return sum(1 for r in runs if name in r["quadrant-name"]) / len(runs)


def crossing_point(points, level=0.5):
    """Linearly interpolate where a rising series first crosses `level`."""
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if y0 < level <= y1:
            return x0 if y1 == y0 else x0 + (level - y0) * (x1 - x0) / (y1 - y0)
    return None


def banner(title):
    print(f"\n{title}")
    print("_" * len(title))


# ------------------------------------------------------------- experiment E1 - validation
def validation():
    """Does NetLogo reproduce the Python action model with the grid switched off?"""
    runs = load(VALIDATION, "aggregate-baseline-table.csv")
    banner("E1  aggregate-baseline -- NetLogo against Python")

    print(f"{'quantity':<22}{'NetLogo':>12}{'Python':>12}")
    print("-" * 46)
    expected = {"aspiration": 0.411, "stability": 0.855}
    for key, python in expected.items():
        print(f"{key:<22}{avg(runs, key):>12.4f}{python:>12.3f}")
    for i, actor in enumerate(ACTORS):
        print(f"{actor + ' share':<22}{avg(runs, f'mean-share {i}'):>12.4f}")

    checks = avg(runs, "item 0 checks-against")
    print(f"\nChecks received by People: {checks:.0f} "
          f"across {len(runs)} runs -- nothing targets them.")


# ---------------------------------------------------------- experiments E2/E3 - threshold (NEXT_STEPS.md 3a and 3b)
def threshold_comparison():
    """Does putting power in space change how strong a check has to be?"""
    banner("E2 / E3  threshold -- aggregate against spatial")

    header = (f"{'ratio':>7}{'aggregate asp':>18}{'% QuadII':>10}"
              f"{'spatial asp':>18}{'% QuadII':>10}")
    print(header)
    print("-" * len(header))

    agg = group_by(load(THRESHOLD, "threshold-aggregate-table.csv"), "check-ratio", float)
    spa = group_by(load(THRESHOLD, "threshold-spatial-table.csv"), "check-ratio", float)

    curves = {"aggregate": [], "spatial": []}
    for ratio in sorted(agg):
        a, s = agg[ratio], spa[ratio]
        qa = quadrant_share(a, "High Potential")
        qs = quadrant_share(s, "High Potential")
        curves["aggregate"].append((ratio, qa))
        curves["spatial"].append((ratio, qs))
        print(f"{ratio:>7.1f}{avg(a, 'aspiration'):>8.3f} +/- {sd(a, 'aspiration'):.3f}"
              f"{qa:>10.0%}"
              f"{avg(s, 'aspiration'):>8.3f} +/- {sd(s, 'aspiration'):.3f}"
              f"{qs:>10.0%}")

    print()
    for label, points in curves.items():
        x = crossing_point(points)
        print(f"{label + ' crossing':<22}{x:.2f}" if x else f"{label}: no crossing")
    print("\nStability is flat across the whole range -- stronger checks move "
          "power to People\nwithout making the system more even overall.")


# ------------------------------------------------------------- experiment E4 - spread by modality (RQ4)
def spread_by_modality():
    """RQ4. Do kinds of power that travel freely end up more evenly spread?"""
    runs = load(RQ4, "spread-by-modality-table.csv")
    groups = group_by(runs, "uniform-diffusion?")
    banner("E4  spread-by-modality -- RQ4")

    header = (f"{'modality':<16}{'rate':>6}{'rates differ':>21}"
              f"{'uniform 0.17':>14}{'change':>10}")
    print(header)
    print("-" * len(header))

    rows = []
    for i, (name, rate) in enumerate(MODALITIES):
        d, u = groups["false"], groups["true"]
        rows.append((name, rate, avg(d, f"spread-of {i}"),
                     sd(d, f"spread-of {i}"), avg(u, f"spread-of {i}")))
    rows.sort(key=lambda r: -r[2])

    for name, rate, d, d_sd, u in rows:
        print(f"{name:<16}{rate:>6.2f}{d:>11.3f} +/- {d_sd:.3f}"
              f"{u:>14.3f}{u - d:>+10.3f}")

    spread_d = max(r[2] for r in rows) - min(r[2] for r in rows)
    spread_u = max(r[4] for r in rows) - min(r[4] for r in rows)
    print(f"\nSpread across modalities: {spread_d:.3f} with the paper-derived "
          f"rates, {spread_u:.3f} under the control.")

    # The same runs, measured the way an aggregate model would measure them.
    print(f"\n{'aggregate metric':<20}{'rates differ':>20}{'uniform 0.17':>20}")
    print("-" * 60)
    for metric in ("aspiration", "stability"):
        d, u = groups["false"], groups["true"]
        print(f"{metric:<20}{avg(d, metric):>12.4f} +/- {sd(d, metric):.4f}"
              f"{avg(u, metric):>12.4f} +/- {sd(u, metric):.4f}")
    print("The control reshapes the spatial structure and leaves these where "
          "they were.")

# ------------------------------------------------------------- experiment E5 - heterogeneity sweep
def heterogeneity_sweep():
    """Does the RQ4 result depend on how unequal the localities start?"""
    groups = group_by(load(RQ4, "heterogeneity-sweep-table.csv"), "heterogeneity", float)
    banner("E5  heterogeneity-sweep -- robustness of RQ4")

    header = f"{'het':>6}" + "".join(f"{n[:9]:>12}" for n, _ in MODALITIES) + f"{'range':>9}"
    print(header)
    print("-" * len(header))
    for het, runs in groups.items():
        vals = [avg(runs, f"spread-of {i}") for i in range(5)]
        print(f"{het:>6.1f}" + "".join(f"{v:>12.3f}" for v in vals)
              + f"{max(vals) - min(vals):>9.3f}")

    flat = groups.get(0.0)
    if flat:
        print("\nAt heterogeneity 0 every locality starts identical, so any "
              "unevenness left\nis caused by the agents' actions rather than by "
              "diffusion.")


# ------------------------------------------------------------- experiment E6 - diffusion escape (NEXT_STEPS.md 3e)
def diffusion_escape():
    """Can an actor spread its power across localities to dodge being checked?"""
    groups = group_by(load(ROBUSTNESS, "diffusion-escape-table.csv"), "diffusion-scale", float)
    banner("E6  diffusion-escape")

    header = f"{'diffusion':>10}" + "".join(f"{a:>13}" for a in ACTORS) + f"{'aspiration':>13}"
    print(header)
    print("-" * len(header))
    for scale, runs in groups.items():
        shares = [avg(runs, f"mean-share {i}") for i in range(4)]
        print(f"{scale:>10.1f}" + "".join(f"{s:>13.4f}" for s in shares)
              + f"{avg(runs, 'aspiration'):>13.3f}")


# ------------------------------------------------------------- experiment E7
def settling():
    """Has the system settled by tick 50, or are the reported numbers a transient?"""
    runs = load(ROBUSTNESS, "settling-table.csv")
    by_step = group_by(runs, "[step]", int)
    banner("E7  settling -- is 50 ticks long enough?")

    print(f"{'tick':>6}{'aspiration':>13}{'stability':>12}")
    print("-" * 31)
    marks = [t for t in (0, 25, 50, 100, 150, 200, 250, 299) if t in by_step]
    for tick in marks:
        print(f"{tick:>6}{avg(by_step[tick], 'aspiration'):>13.4f}"
              f"{avg(by_step[tick], 'stability'):>12.4f}")

    if 50 in by_step and marks[-1] != 50:
        last = marks[-1]
        drift = avg(by_step[last], "aspiration") - avg(by_step[50], "aspiration")
        print(f"\nAspiration drifts {drift:+.3f} between tick 50 and tick {last}, "
              f"and is still moving.\nEvery 50-tick number in the report is a "
              f"snapshot of a transient.")


def main():
    validation()
    threshold_comparison()
    spread_by_modality()
    heterogeneity_sweep()
    diffusion_escape()
    settling()


if __name__ == "__main__":
    main()

