# Can diffusion be used to escape a check?

### The question
If power spreads across localities, does that put
it out of reach of a check? If it did, the spatial model would have handed
every concentrated actor a way out, and the check-strength results would mean less.

### Configuration

BehaviorSpace experiment `diffusion-escape`: `diffusion-scale` at 0, 1 and 2, 10 repetitions each, 50 ticks: 30 runs.
Shocks are off. Everything else is pinned in the experiment definition:
heterogeneity 0.6, check-ratio 1, enhance-magnitude 0.1,
concentration-threshold 0.45, uniform-diffusion? false.

Data: `diffusion-escape-table.csv`

Table: `python3 questions/rq3_spatial.py`

### Result

Each number is the actor's mean share across the 289 localities, averaged over
the 10 runs.

| diffusion-scale | People | State | Enterprises | AI | aspiration |
|---|---|---|---|---|---|
| 0 | 0.2025 | 0.3120 | 0.2898 | 0.1957 | 0.405 |
| 1 | 0.2129 | 0.3058 | 0.2885 | 0.1928 | 0.426 |
| 2 | 0.2152 | 0.3045 | 0.2870 | 0.1932 | 0.430 |

As diffusion rises the three largest holders all end up with less, and People
end up with more.

### Interpretation

No actor escapes a check by diffusing. State, Enterprises and AI each hold a smaller share at scale 2 than at scale 0, so a more diffusive world does not protect the actors holding the most.

Checks read the share an actor holds in a locality, and the concentration
threshold is read per locality as well. Diffusion moves power between
localities without reducing it or hiding it, so it changes where power sits
and not whether a check can reach it.

People are the only actor to gain. Diffusion averages each locality toward its
neighbours, which lifts whoever sits below the average, and People hold least.
That is a property of the averaging rule rather than a finding about the
framework.

### What was actually varied

`diffusion-scale` is a single global setting. It scales the diffusion rate for
every modality and every actor at once, and no actor chooses it. So this
experiment tests whether a more diffusive world favours anyone, not whether a
single actor can spread out deliberately. The model has no per-actor
diffusion, so the second question cannot be put to it as written.
