# Prototype baseline, rerun with corrected metrics

### Why it was rerun

The first run used `aspiration()` to return `1 - mean HHI`, which measures how
evenly power is spread. The paper calls that stability, not aspiration:
"preserving both human flourishing (aspiration) and balanced power (stability)".
So the concentration measure was sitting under the wrong label, and nothing was
measuring People.

`aspiration()` is now People's mean share across the modalities, normalised so
an even split gives 0.5. `stability()` is now the concentration measure, per
modality and then averaged. Volatility and check success rate used to be folded
into stability; they are now recorded separately as `volatility` and do not
decide the quadrant.

### Configuration

Unchanged from the first run: 100 runs, seeds 0-99, 50 ticks, effect magnitude
0.10, shock probability 0.15, concentration threshold 0.45, volatility window 5.
Only the metric definitions changed.

### Reproducibility check

Seed 42 run twice, identical outputs.

### Aggregated results

| | before the fix | after the fix |
|---|---:|---:|
| Mean aspiration | 0.718 (sd 0.054) | **0.261** (sd 0.056) |
| Mean stability | 0.334 (sd 0.092) | **0.718** (sd 0.054) |
| Quadrant III - Creative Chaos | 95/100 | 0/100 |
| Quadrant I - Surviving not Thriving | 0/100 | **100/100** |

Note that the old aspiration and the new stability are the same number, 0.718
with sd 0.054. That is the check that the fix did what it was supposed to: the
quantity we were calling aspiration was the concentration measure all along, and
it now carries the right name.

### Mean final power shares

Unchanged, since the metrics do not affect the simulation itself.

| Modality | People | State | Enterprises | AI |
|---|---:|---:|---:|---:|
| Economic | 0.063 | 0.268 | 0.666 | 0.003 |
| Epistemic | 0.011 | 0.012 | 0.529 | 0.448 |
| Narrative | 0.212 | 0.074 | 0.104 | 0.610 |
| Authoritative | 0.167 | 0.541 | 0.262 | 0.029 |
| Physical | 0.200 | 0.581 | 0.199 | 0.020 |

### Interpretation

Every run now ends in Quadrant I, high stability and low aspiration, which the
paper calls "Surviving not Thriving". This is a different story from the one the
first run told. The system is not fragmenting; it holds together, but People end
up with roughly a quarter of what an even share would be.

This also agrees with the continuous simulation, which lands in Quadrant I as
well, so the two models now say the same thing about where the system ends up
even though they get there by completely different mechanics.

The caution from the first run still applies, and more strongly. The end states
are still driven by two choices in our own code: ENHANCE takes a share from all
three other actors while CHECK takes from one and only on success, and
Enterprises and AI never abstain while People and the State abstain most of the
time. Enterprises at 0.666 in economic and AI at 0.610 in narrative is what two
actors that grow every single round will produce. Until those are balanced, the
end shares are not a result about the framework.

---
