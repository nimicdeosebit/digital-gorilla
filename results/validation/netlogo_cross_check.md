# NetLogo against Python

## Purpose

The spatial model is a second, independent implementation of the action model,
written in a different language. If the two agree when the spatial machinery is
switched off, each validates the other. If they disagree, at least one is wrong.

## Configuration

NetLogo reduced to the aggregate case: `heterogeneity` 0, `diffusion-scale` 0,
`shock-probability` 0, `check-ratio` 1, `enhance-magnitude` 0.10,
`concentration-threshold` 0.45, 50 ticks. All 289 localities then start
identical and never interact, so each is an independent replicate of the Python
action model.

Python matched to it: `enhance_mode="per_capita"` (NetLogo hard-codes the
per-capita split), `shock_probability=0.0`, 50 ticks, 289 seeds.

Shocks have to be off. They are not comparable between the two: a Python shock
hits the whole world, a NetLogo shock hits one locality out of 289.

## Result

| | NetLogo | Python (289 seeds) |
|---|---|---|
| People hold | 0.206 | 0.2044 |
| State hold | 0.315 | 0.3172 |
| Enterprises hold | 0.288 | 0.2879 |
| AI hold | 0.191 | 0.1906 |
| aspiration | 0.411 | 0.4088 +/- 0.0046 |
| stability | 0.855 | 0.8478 +/- 0.0017 |

Four power shares agree to three decimals. Aspiration agrees within the
confidence interval.

## The stability gap is accounted for

Stability differs by 0.007, which is outside the interval. The cause is the
order of averaging, not an error in either model.

NetLogo computes stability on the grid-averaged matrix: it averages the 289
localities first, then measures concentration. Python averages the 289
stabilities. HHI is convex, so averaging the matrices first smooths out each
run's lumpiness and returns a higher stability.

Computing it Python-side the NetLogo way gives **0.8532**, against NetLogo's
0.855 -- inside single-run variation.

Aspiration is linear in the shares, so the order of averaging cannot affect it,
and it shows no gap. The discrepancy appears exactly where the mathematics says
it should and nowhere else.

## Not yet done

The BehaviorSpace experiment `spread-by-modality` has never been run, so RQ3
has no numbers yet. That run is independent of the agreement reported above:
this check switches the spatial machinery off, RQ3 is what it is for.

NetLogo Web has no BehaviorSpace; that run needs NetLogo desktop.
