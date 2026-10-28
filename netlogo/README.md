# The spatial model

`digital_gorilla.nlogo` — the action model run on a grid, so that power has a
place as well as a size. This is where **RQ4** is answered: does it matter
where power sits? See `results/rq4_spatial/rq4_spatial.md`.

## Running it

Open it in NetLogo 6.4 (desktop) or drop it into netlogoweb.org. Press
`setup`, then `go`. It stops at `max-ticks`.

NetLogo Web has no BehaviorSpace, so repeated-run experiments need the desktop
version. Reading the monitors by hand works on either.

## The world

A 17x17 torus: 289 localities. Each one owns a full 4x5 power matrix, so the
model holds 5,780 numbers where the Python model holds 20. Every modality's
four shares sum to 1 in every locality.

Legitimacy is global — one value per actor for the whole world, not per
locality. Power is stuck in place and has to spread; standing is treated as a
reputation that is already everywhere.

## One tick

```
local-actions   every actor acts in every locality, same rules as the Python model
diffuse-power   power leaks to the four neighbours, at a rate set per modality
maybe-shock     with probability shock-probability, one event hits ONE locality
recolour        redraw
```

Diffusion is the only phase the aggregate model does not have:

```
new share = (1 - rate) * own share + rate * mean of the four neighbours
```

`new-power` holds the result until every patch has computed it, so the update
is synchronous and the order patches are visited in does not matter.

### Why the rates differ

| Modality | Rate | Why |
|---|---|---|
| Epistemic | 0.30 | A model, a dataset, a method travels at no cost |
| Narrative | 0.30 | So does a framing |
| Economic | 0.15 | Capital moves, but through institutions |
| Authoritative | 0.05 | Jurisdiction stops at the border |
| Physical | 0.03 | Force has to physically be somewhere |

The *ordering* is read off the paper's descriptions of what each kind of power
consists of. The *numbers* are ours — as with every other magnitude in this
project, the framework supplies none. This is why the `uniform-diffusion?`
control matters: it sets all five to 0.17, and if the pattern survives that,
the pattern came from the rates rather than from the mechanism.

## Controls

| Slider | Range | Default | Matches Python |
|---|---|---|---|
| `heterogeneity` | 0 – 1.5 | 0.6 | no equivalent |
| `diffusion-scale` | 0 – 2 | 1.0 | no equivalent |
| `check-ratio` | 0.5 – 6 | 1.0 | 1.0 |
| `enhance-magnitude` | 0.02 – 0.3 | 0.10 | 0.10 |
| `shock-probability` | 0 – 0.6 | 0.15 | 0.15 |
| `shock-magnitude` | 0.02 – 0.3 | 0.10 | 0.10 |
| `concentration-threshold` | 0.2 – 0.8 | 0.45 | 0.45 |
| `max-ticks` | 10 – 300 | 50 | 50 |
| `uniform-diffusion?` | — | off | no equivalent |

`heterogeneity` multiplies each locality's starting matrix by lognormal noise
and renormalises, so the localities begin unequal. At 0 all 289 start
identical.

`check-ratio` is the experimental variable from the threshold sweep, exposed
directly: drag it from 1 to 4 and the quadrant monitor flips.

## Reading the view

`display-modality` picks which of the five matrices is drawn. It changes
nothing in the simulation. It defaults to Physical, the slowest-diffusing one,
which is the lumpiest picture there is — switching it to Narrative mid-run, on
the same tick, shows the result without re-running anything.

Each patch shows whoever holds the most of the chosen modality: a person for
People, a gavel for the State, a dollar for Enterprises, a robot for AI, on a
tint of that actor's colour. Both the tint and the icon size scale with how
much they hold.

It is a plurality map, not a power map. An icon only says who is ahead, so a
locality where People hold 0.27 against three rivals looks much like one where
they hold 0.85. The tint and the size are what separate them.

## Monitors and plots

- per-actor mean share, `aspiration`, `stability`, `quadrant` — the same
  definitions as the Python model, so the numbers are comparable
- `local HHI` — mean concentration inside a locality
- `checks received` — running count per actor
- Aspiration–Stability — the run's path across the quadrant matrix
- Regional structure by modality — `spread-of` per modality over time; 1.0
  means that modality looks the same everywhere

`spread-of` is 1 - (standard deviation / mean) across localities, averaged
over actors.

## Differences from the Python action model

| | Python | NetLogo |
|---|---|---|
| Localities | 1 | 289 |
| Legitimacy | per actor | per actor, global |
| Invariant | asserted every tick | preserved by construction, never checked |
| Shock scope | the whole world | one locality |
| Enhance split | parameter (`per_donor` / `per_capita`) | hard-wired `1 / 3` |
| Actor count | 3 or 4 | 4 only, because of that `1 / 3` |
| Check mechanisms | drawn from a named catalogue and logged | not modelled |

The hard-wired `1 / 3` is why the three-versus-four comparison stays a Python
result. The shock-scope difference is why the two models can only be compared
with shocks switched off.

## Validation

With `heterogeneity` 0, `diffusion-scale` 0 and `shock-probability` 0 the 289
localities become independent copies of the Python action model, and the two
agree: all four power shares to three decimals, aspiration within its
confidence interval, and the 0.007 stability difference fully explained by the
order of averaging.

The write-up is in `results/validation/netlogo_cross_check.md`.

## The experiments that have been run

Seven BehaviorSpace experiments are defined in the model file: an aggregate
baseline, the check-strength threshold with and without the grid,
spread-by-modality (RQ4), a heterogeneity sweep, a diffusion-escape test and a
settling test. `python3 questions/rq4_spatial.py` reduces their CSV output to
the tables in `results/`.
