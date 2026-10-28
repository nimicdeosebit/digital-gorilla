# Experiments

Every experiment has its own folder under `results/`, with the write-up beside
the data it was computed from. [`results/README.md`](results/README.md) is the
index to those folders.

## The research questions

**RQ1 — How strong does a check have to be?**
The paper says checks and balances restrain whoever grows too strong, but never
says how hard a check has to push. So: how strong must checking be, relative to
a move that simply grows an actor's own power, before the People end up in the
paper's High Potential quadrant?
→ action model · [`results/rq1_check_threshold/`](results/rq1_check_threshold/rq1_check_threshold.md)

**RQ2 — Does AI as a fourth actor change anything?**
The framework separates AI from Enterprises. Does that separation do any work,
or is it the same system with one actor relabelled?
→ both Python models · [`results/rq2_three_vs_four/`](results/rq2_three_vs_four/rq2_three_vs_four.md)

**RQ3 — Do the policy levers help?**
The paper proposes interventions. Do they change who holds power, and can
policy substitute for raw check strength?
→ action model · [`results/rq3_levers/`](results/rq3_levers/rq3_levers.md)

**RQ4 — Does it matter where power sits?**
The aggregate models hold one number per kind of power, so power spread thinly
everywhere looks identical to the same total piled into a few places. Do kinds
of power that travel easily end up more evenly spread across localities than
kinds that are bound to a place?
→ NetLogo spatial model · [`results/rq4_spatial/`](results/rq4_spatial/rq4_spatial.md)

## Supporting runs

These are not research questions. They establish what the models do before
anything is varied, and test whether a simplification drives a result.

| Run | Write-up |
|---|---|
| Baseline, corrected metrics | [`results/baseline/baseline.md`](results/baseline/baseline.md) |
| Actor count, first pass | [`results/rq2_three_vs_four/actor_count_comparison.md`](results/rq2_three_vs_four/actor_count_comparison.md) |
| Legitimacy robustness | [`results/robustness/legitimacy.md`](results/robustness/legitimacy.md) |
| NetLogo against Python | [`results/validation/netlogo_cross_check.md`](results/validation/netlogo_cross_check.md) |
| First prototype run (superseded) | [`results/baseline/superseded_first_run.md`](results/baseline/superseded_first_run.md) |
