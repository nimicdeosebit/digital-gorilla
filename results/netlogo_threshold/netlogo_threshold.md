# The check-strength threshold, in NetLogo

### Purpose

1. Does the spatial model reproduce RQ1's check-strength threshold when the grid is switched off? 
2. Does putting power in space move that threshold? This has no answer in the aggregate models, because they have no notion of where power sits.

### Configuration

Two BehaviorSpace experiments, `threshold-aggregate` and `threshold-spatial`,
seven check ratios at 10 repetitions each, 50 ticks, shocks off. Every other
control is pinned inside the experiment definition. The two differ only in
whether the grid is active:

| | heterogeneity | diffusion-scale |
|---|---|---|
| aggregate | 0 | 0 |
| spatial | 0.6 | 1.0 |

With heterogeneity and diffusion at zero the 289 localities are independent
copies of the aggregate model, so the first experiment is directly comparable
with Python. 

Data: `threshold-aggregate-table.csv`, `threshold-spatial-table.csv`

Table: `python3 questions/rq4_spatial.py`

Figure: `figures/fig10_netlogo_threshold.png` 

### Check-ratio 

Each tick every actor makes one move: ENHANCE (grow my own power, taking a
slice from each of the other three — always works) or CHECK (try to push one
other actor down, and it can fail). A check is the paper's checks and
balances: a court striking down a law, a regulator fining a firm.

`check-ratio` sets how hard a successful check bites, as a multiple of
`enhance-magnitude`, which is pinned at 0.1. At ratio 1 a successful check
takes 10% of what the target holds; at ratio 3, 30%. It is a ratio because
ENHANCE drains three opponents at once and never fails while CHECK hits one
and only when it wins — so at equal magnitudes growing beats checking, which
is why the original model at ratio 1 ended in Quadrant I every time.


### Result

| ratio | aggregate aspiration | % Quad II | spatial aspiration | % Quad II |
|---|---|---|---|---|
| 1.0 | 0.413 +/- 0.002 | 0% | 0.430 +/- 0.006 | 0% |
| 2.0 | 0.484 +/- 0.002 | 0% | 0.492 +/- 0.006 | 10% |
| 2.5 | 0.503 +/- 0.002 | 90% | 0.508 +/- 0.004 | 100% |
| 3.0 | 0.517 +/- 0.003 | 100% | 0.521 +/- 0.003 | 100% |
| 3.5 | 0.528 +/- 0.003 | 100% | 0.530 +/- 0.005 | 100% |
| 4.0 | 0.537 +/- 0.003 | 100% | 0.536 +/- 0.004 | 100% |
| 5.0 | 0.562 +/- 0.004 | 100% | 0.553 +/- 0.005 | 100% |

The percentage is the share of the 10
runs that landed in Quad II.

### Does NetLogo reproduce the threshold?
Partly. NetLogo behaves the way Python does: aspiration rises as checks get stronger, from 0.413 at ratio 1 to 0.562 at ratio 5, and the quadrant flips partway through the range — 9 of 10 runs reach High Potential at ratio 2.5 and all 10 from ratio 3. The values are not the same, though. `rq1_check_threshold.md` puts the Python flip at about 3; NetLogo flips between 2 and 2.5.
#### Against the Python numbers

| ratio | Python | NetLogo | within the interval |
|---|---|---|---|
| 1 | 0.409 +/- 0.005 | 0.413 | yes |
| 2 | 0.474 +/- 0.006 | 0.484 | no |
| 2.5 | 0.486 +/- 0.007 | 0.503 | no |
| 3 | 0.500 +/- 0.007 | 0.517 | no |
| 3.5 | 0.521 +/- 0.007 | 0.528 | borderline |
| 4 | 0.525 +/- 0.007 | 0.537 | no |
| 5 | 0.549 +/- 0.009 | 0.562 | no |

NetLogo is higher at all seven ratios, clearly outside the interval at five of
them, on the boundary at one, and overlapping only at ratio 1. So NetLogo
agrees with Python about what happens when checks get stronger and disagrees
about the numbers. The difference runs the same way at every ratio, so it is
not random variation between runs. The cause is not established. The most likely candidate is
decision order: Python collects all four actors' decisions and then applies
them, so everyone decides against the same board, while NetLogo resolves each
actor's move before the next one decides.

## Does it matter where power sits?

Yes, slightly. With the grid on, 1 of 10 runs reaches High Potential at ratio
2 and all 10 at ratio 2.5. Grid off, it is 0 of 10 and 9 of 10.

The grid-on line is flatter. It starts higher, 0.430 against 0.413 at ratio 1,
and ends lower, 0.553 against 0.562 at ratio 5. It covers 0.123 across the
range where the grid-off line covers 0.149. The two cross at about ratio 4.

A line that starts higher and rises more slowly crosses 0.5 earlier, so the
flip comes at a lower check-ratio.

Putting power in space weakens the effect of check strength in both
directions: weak checks do better than the aggregate model predicts, strong
checks do worse.

We did not test why the line flattens. One possible cause is that diffusion
moves power between neighbouring localities every tick, so the effect of any
single check or growth move is partly spread out.

### Caveat

The flip is reported as an interval between two sampled ratios, not a precise
crossing point. The sweep leaves a 0.5-wide gap between ratios 2 and 2.5,
exactly where the flip happens, and the percentage column is one run of ten
per step, so neither supports more precision than that.