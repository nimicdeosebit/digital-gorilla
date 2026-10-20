# Prototype baseline / validation run (SUPERSEDED - see below)

> The numbers in this run were produced with the old metric definitions, in
> which `aspiration()` returned the concentration measure and `stability()`
> did not use concentration at all. They are kept here as a record, but the
> quadrant result is not meaningful. See the rerun below.

### Purpose

Establish the default behaviour of the action-based simulation and measure how much results vary due to stochasticity alone.

### Configuration

- Number of runs: 100
- Seeds: 0-99
- Ticks per run: 50
- Effect magnitude: 0.10
- Shock probability: 0.15
- Concentration threshold: 0.45
- Volatility window: 5

Only the random seed was changed between runs.

### Reproducibility check

Seed 42 was run twice using identical parameters.

Result: both runs produced identical outputs, confirming reproducibility under a fixed seed.

### Aggregated results

- Mean aspiration: 0.718
- Aspiration standard deviation: 0.054
- Mean stability: 0.334
- Stability standard deviation: 0.092

Final quadrant frequencies:

- Quadrant III - Creative Chaos: 95/100 runs (95%)
- Quadrant II - High Potential: 5/100 runs (5%)

### Mean final power shares

| Modality | People | State | Enterprises | AI |
|---|---:|---:|---:|---:|
| Economic | 0.063 | 0.268 | 0.666 | 0.003 |
| Epistemic | 0.011 | 0.012 | 0.529 | 0.448 |
| Narrative | 0.212 | 0.074 | 0.104 | 0.610 |
| Authoritative | 0.167 | 0.541 | 0.262 | 0.029 |
| Physical | 0.200 | 0.581 | 0.199 | 0.020 |

### Preliminary interpretation

The default discrete model most often ends in Quadrant III. Across runs, Enterprises tend to dominate Economic power, Enterprises and AI dominate Epistemic power, AI tends to dominate Narrative power, and the State retains the largest shares of Authoritative and Physical power.

These patterns should not yet be treated as robust conclusions, because several simulation parameters and actor policies are manually specified. Sensitivity analysis is required to determine how dependent the outcomes are on those assumptions.


---
