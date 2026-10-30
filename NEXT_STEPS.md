# Open items

## 1. Can People be checked? (new experiment, ~20 min)

The checks-received monitor reads `[0 6636 11330 3521]` — People receive ZERO
checks in 50 ticks over 289 localities, because no actor's watchlist names
People as a target.

  action_based_sim/policies.py   _state_policy, _enterprises_policy, _ai_policy
  netlogo/digital_gorilla.nlogox  decide-state, decide-enterprises, decide-ai

The paper does list mechanisms running against People (law enforcement,
surveillance, targeted marketing, manipulating choices); they sit unused in
CHECK_MECHANISMS. Since aspiration IS People's share, this biases the headline
metric.

Run it both ways and report. If aspiration barely moves, the result is robust;
if it collapses, better we find out.

## 2. NetLogo runs

Diya has run these: aggregate baseline, threshold with and without the grid,
spread-by-modality (RQ4), heterogeneity sweep, diffusion escape, settling.
`python3 questions/rq4_spatial.py` rebuilds every table from the CSVs. What is
listed below is what each run was for, and what is left. 

NetLogo Web has no BehaviorSpace, so anything needing repetitions must be run
in NetLogo desktop. The monitors can be read by hand on either, and each patch
is already its own replicate, so a single run averages 289 localities.

### a. Replicate the threshold (highest value, five slider drags) -> check `results/netlogo_threshold`

Keep `heterogeneity` 0, `diffusion-scale` 0, `shock-probability` 0. Drag
`check-ratio` and press setup + go each time. Python, matched settings, 289
runs, says to expect:

| check-ratio | aspiration | stability |
|---|---|---|
| 1 | 0.409 +/- 0.005 | 0.848 |
| 2 | 0.474 +/- 0.006 | 0.852 |
| 2.5 | 0.486 +/- 0.007 | 0.850 |
| 3 | 0.500 +/- 0.007 | 0.849 |
| 3.5 | 0.521 +/- 0.007 | 0.848 |
| 4 | 0.525 +/- 0.007 | 0.847 |
| 5 | 0.549 +/- 0.009 | 0.838 |

Ratio 1 is already confirmed (0.411 against 0.409). The quadrant monitor should
flip to High Potential at about 3. This replicates the headline result in a
second implementation, in a different language.

Note stability barely moves across the whole range: stronger checks shift power
TO People without making the system more even overall. Worth a sentence in the
report.

### b. Does space move the threshold? (genuinely new result) -> check `results/netlogo_threshold`

Repeat (a) with `diffusion-scale` 1 and `heterogeneity` 0.6. If the crossing
moves away from 3, then where power sits changes how hard checks must push --
which no aggregate model can tell you, and would be the strongest argument for
having built the spatial model at all. If it does not move, that is also worth
reporting: the threshold is a property of the contest, not of the geography.

### c. RQ4: spread by modality -> check `results/rq4_spatial`

BehaviorSpace, experiment `spread-by-modality`, 10 repetitions, both settings
of `uniform-diffusion?`. This is what regenerates the numbers in
`results/rq4_spatial/`.

### d. The control, by hand -> https://docs.google.com/document/d/1iOd3UPx1ok26bfX96LDmdXgY8LNWvHWDreems6bDRwI/edit?usp=sharing 

`heterogeneity` 0.6, `diffusion-scale` 1, 50 ticks, then flip
`uniform-diffusion?` on and rerun. The fan of lines in "Regional structure by
modality" should collapse, and Physical should go from the lumpiest to nearly
uniform. Screenshot both -- side by side they make the argument visually.

### e. Can diffusion be used to escape a check? -> claude says the python bit doesn't make sense because power can not be spread across since there are no localities. check `results/robustness/diffusion_escape.md`

The Python version said no: spreading an actor's power across localities
equalises it without lowering it, so it does not help the actor evade checks
(-1% to -6%). Re-test here by comparing an actor's mean share at
`diffusion-scale` 0 against 2, all else equal. A negative result, but one that
closes an obvious objection.

### f. Does the grid settle? -> check `results/robustness/settling.md`

`max-ticks` 300 with diffusion on. If aspiration and stability are still moving
at 300, the 50-tick results are a snapshot of a transient rather than an end
state, and every number in the report needs that caveat.

### g. Confirm the zero -> is zero for all runs

The `checks received` monitor reads `[0 ...]` for People. Confirm it stays zero
across settings -- it is the visible symptom of item 1 above.

## 3. Smaller

- continuous_sim says "Enterprise", action_based_sim says "Enterprises".
- All 48 mechanism weights are 1.0, so the mechanism draw has no numerical
  effect. Declare it.
- NetLogo hard-codes `let scale 1 / 3`, so it can only run four actors.
- NetLogo legitimacy is global, not per locality. Declare it.
- NetLogo shocks hit ONE patch; Python shocks hit the whole world. Not
  comparable — this is why the cross-validation needs shocks off.
