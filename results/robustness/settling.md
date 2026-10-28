# Settling: is 50 ticks long enough?

### Purpose
If aspiration and stability are still moving at
300, the 50-tick results are a snapshot of a transient rather than an end
state, and every number in the report needs that caveat.

### Configuration

BehaviorSpace experiment `settling`: 300 ticks,
5 repetitions, metrics logged every step: 1500 rows. Shocks are on at 0.15.
Everything else is pinned in the experiment definition: heterogeneity 0.6,
diffusion-scale 1, check-ratio 1, enhance-magnitude 0.1,
concentration-threshold 0.45, uniform-diffusion? false.

Data: `settling-table.csv`

Note that check-ratio is 1, the weakest setting in the sweep. Nothing is
intervening here.

### Result

| tick | aspiration | stability |
|---|---|---|
| 0 | 0.3918 | 0.8825 |
| 25 | 0.3800 | 0.8829 |
| 50 | 0.4270 | 0.8625 |
| 100 | 0.5072 | 0.8351 |
| 150 | 0.5582 | 0.8147 |
| 200 | 0.5919 | 0.8013 |
| 250 | 0.6162 | 0.7925 |
| 299 | 0.6322 | 0.7858 |

Aspiration drifts 0.205 between tick 50 and tick 299 and is still rising at
the end. Stability falls over the same span, from 0.8625 to 0.7858.

The 400-tick interactive run reads `II High Potential`, with People at 0.327
the largest single holder: State 0.266, Enterprises 0.224, AI 0.182.

### Inference
The grid has not settled by tick 50, and it has not settled by tick 299
either.
Aspiration passes 0.5 between ticks 50 and 100, at check-ratio 1. That is the
weakest check setting in the project, so the model reaches the High Potential
quadrant on its own, with no intervention, given enough ticks.

Which quadrant a run ends in therefore depends on when the run is stopped.
Tick 50 is not a resting point the model arrives at. It is a point partway
along a trajectory that is still climbing.

### What this means for the other results

The baseline result and the check-strength threshold are both measured at tick
50, so both describe the model at 50 ticks rather than where it settles. They
are not wrong, but they need the horizon attached. The threshold in
`netlogo_threshold.md` is the check strength at which 50 ticks is enough, not
the check strength the model needs in the long run.

### The cause is not in this data

This experiment logs only aspiration and stability, so it shows the drift
without showing what produces it.

The candidate is that People are never checked. `item 0 checks-against` reads
0 in every run of both `aggregate-baseline` and `threshold-aggregate`, because
no actor's watchlist names People as a target. Every other actor is capped by
the concentration threshold and People are not. Over 50 ticks that asymmetry
is small. Over 300 it would compound.

Item 1 of `NEXT_STEPS.md` is the experiment that would settle it: if People
become checkable, does the drift stop?

### Caveat

300 ticks is where the data stops, not where the model settles. Aspiration is
still rising at tick 299, so this experiment establishes that tick 50 is a
transient without establishing what the end state is.