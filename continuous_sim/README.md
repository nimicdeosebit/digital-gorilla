# The contest model

What happens before we let each agent take its own decisions?
This was our initial model. It was mainly used to help design choices such as:

- What should a state look like?
- What power should each actor hold in every modality — our first numeric
  reading of the paper's Table 4
- How should we think of the update rule?
- Which kind of metrics should be used?
- Can we implement a simple spillover mechanism?

It also answers one of our research questions on its own: does adding AI as a
fourth actor change the three-actor power dynamics?

Nobody decides anything in this model. Every round the whole table is
recomputed from scores. That is the point: it shows what the framework does
with no agency in it at all, which is the baseline the action model is
measured against.

## What should a state look like?

One 4x5 matrix. Rows are the four actors, columns are the five modalities, and
**every column sums to 1** — power is relational, so an actor can only gain it
by taking it from someone else.

|  | Economic | Epistemic | Narrative | Authoritative | Physical |
|---|---|---|---|---|---|
| **People** | 0.18 | 0.18 | 0.26 | 0.30 | 0.10 |
| **State** | 0.27 | 0.22 | 0.16 | 0.50 | 0.62 |
| **Enterprise** | 0.45 | 0.30 | 0.28 | 0.13 | 0.20 |
| **AI** | 0.10 | 0.30 | 0.30 | 0.07 | 0.08 |

Every column adds to 1.00. `state.py` renormalises anyway, so the table stays
valid if you edit a cell.

The ordering of the starting values is read off the paper's table 4: Enterprise leads
economic and epistemic, the State leads authoritative and physical, AI leads
narrative and shares the lead in epistemic. The magnitudes are ours. The paper
gives examples per cell, not numbers, so we turned descriptions like “voting, collective action, jury service” into a share.

This matters less than it looks. Every initial matrix we tested — this one, an
even split, random matrices, AI holding everything — converges to the same
fixed point.

Note that the action model uses some different numbers, still inspired by the mentioned table 4.

## How it works

- **effort** — The paper gives the idea that actors choose where to exert power. This is a claim about
  priorities, not about strength: the State putting 0.35 into law means that is
  where it pushes, not that it is effective there. Fixed per actor.

- **capability** — how far that effort goes in a given modality. Effort is
  intent, capability is effectiveness. It is 1 everywhere unless spillover is
  switched on. The paper does note that advantages exist, but does not give additional explanations.

- **score** — effort x capability: how much pressure an actor applies in that
  modality.

Each round, an actor's **target** is its score divided by the sum of all scores
in that modality, and the shares move a fraction `r` of the way towards it. We
set `r` to 0.16, so each round closes 16% of the remaining gap, which is why a
run settles after about 27 rounds.

## Update rules

Does holding power make it easier to gain more?
That would mean the numbers we chose are very important for the model.

To test update dynamics in a model with no agency, we adapt two different update rules, each with different assumptions:

| | `tullock` | `replicator` |
|---|---|---|
| Comes from | the economics of contests | evolutionary game theory |
| What a share is compared against | everyone's total pressure | the average pressure, weighted by who already holds what |
| The rule in words | drift towards your share of the total | grow if you beat the average, shrink if you do not |
| The rule in symbols | `P <- (1-r)P + r (f / sum f)` | `P <- P (1 + r (f - fbar) / fbar)`, renormalised |
| Does holding more help you gain more? | no — your target does not depend on what you already hold | yes — growth is multiplied by the share you already hold |
| Where a run ends | one stable interior point, reached in about 27 rounds from any starting matrix | a corner: whoever is marginally ahead ends up with everything |
| What that says about power | power settles into a balance set by who pushes where | power concentrates unless something stops it |

The last two rows are the point. Under Tullock an actor that is already large
gets no extra help, so the run settles. Under the replicator growth is
proportional to the share already held, so a small lead compounds into total
capture.

Both are implemented and both are reported. They're both using the same score (described above), same inputs but different mathematics, and reach opposite conclusions. This helps show how much the answer depends on
the rule rather than on the framework.

## The metrics, and where they come from

The paper scores an end state on its Aspiration-Stability matrix. We turned
both axes into numbers:

- **stability** — can the system hold together, i.e. is anyone dominating?
  Per-modality HHI (the sum of squared shares), rescaled so an even split is 1
  and one actor holding everything is 0, then averaged across the modalities.
  The paper itself suggests market-concentration indices here, so the choice of
  measure is its own rather than ours. Averaging per modality rather than
  taking one global figure means an actor that owns two modalities outright
  still registers, even when its overall position looks moderate.
- **aspiration** — is it worth holding together, i.e. do People still hold a
  share? People's mean share across the modalities, scaled so an even split
  maps to 0.5 and twice an even share maps to 1.0. **This is a proxy: the paper
  means more by aspiration than "how much do the People hold"**.
- **quadrant** — the two axes cut at 0.5, giving the paper's four cells:
  I Surviving not Thriving, II High Potential, III Creative Chaos,
  IV Fragile Collapse.

Both are normalised by the number of actors, so a three-actor run stays
comparable with a four-actor one. The action model uses these same definitions,
deliberately, so the two simulations can be compared at all.

## Spillover

The one mechanism we added. An actor's capability in the other modalities gets
multiplied by

```
1 + gain x (that actor's own epistemic share)
```

Holding the data and the knowledge makes you more effective everywhere else,
which is the paper's claim that epistemic power is upstream of the rest.
Epistemic does not boost itself: it runs one way. Off by default (`GAIN = 0.0`),
so the flat baseline is what you get unless you ask for it.

Which modalities it reaches is ambiguous in the paper. One sentence names three
(economic, authoritative, physical), the next implies narrative as well. Both
readings are in `TARGET_SETS` and the choice is a parameter rather than a
decision buried in the code, because it changes the result: under the
three-modality reading AI's narrative share does not move at all, whatever the
gain.

Mean share per actor, at convergence:

| gain | People | State | Enterprise | AI |
|---|---|---|---|---|
| 0 | 0.236 | 0.292 | 0.236 | 0.236 |
| 1 | 0.229 | 0.282 | 0.240 | 0.248 |
| 4 | 0.219 | 0.266 | 0.247 | 0.267 |

AI starts level with People and ends clearly ahead, and the State loses most.

## Where to find everything

| File | What it holds |
|---|---|
| `state.py` | the 4x5 matrix, the initial reading of the paper, `normalise` |
| `agents.py` | effort priorities, capability, score |
| `contest.py` | the two update rules |
| `mechanisms.py` | spillover and its two target sets |
| `metrics.py` | aspiration, stability, HHI, quadrant |
| `variants.py` | running with a subset of the actors, for the three-actor baseline |
| `config.py` | every tunable number, each marked PLACEHOLDER where it is our choice |
| `plots.py` | figures 1-5 |

```bash
python3 continuous_sim/plots.py          # figures 1-5
python3 questions/rq2_three_vs_four.py   # three actors against four
```

## What it does not have

No legitimacy, no decisions, and nothing that can fail — no actor in this model
can attempt something and not get it. Those three are exactly what the action
model adds: see [`action_based_sim/`](../action_based_sim/README.md), where each
actor chooses ENHANCE, CHECK or ABSTAIN every tick, and a CHECK is a contest it
can lose.
