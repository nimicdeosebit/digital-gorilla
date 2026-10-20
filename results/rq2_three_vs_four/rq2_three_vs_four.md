# Three actors against four

### Purpose

The paper's foundational move is adding AI to the three societal actors of the
older literature. Whether that addition does any work is a question the model
can answer, and it had never been run.

### The merge has to be fair

Removing AI by deleting its row and renormalising is not a control: it takes
capability out of the system as well as an actor, so any difference it
produces says only that four actors hold more between them than three do.

A fair merge folds AI into Enterprise and gives the merged actor what both
had. In the continuous model that is the sum of their shares plus their effort
priorities averaged in proportion to the power each brought (weights 0.615
Enterprise, 0.385 AI, from their mean initial shares). In the action model the
policies are discrete, so the merge is done by behaviour: each tick the merged
actor acts as Enterprise with probability 0.615 and as AI otherwise, which
reproduces the same mix of behaviour over a run. Checks aimed at AI by other
actors are redirected to the merged actor; a check the merged actor would have
aimed at itself becomes an abstention, because one actor cannot check itself.

All three conditions are kept: `4A`, `3A-merged`, and `3A-dropped` as the
unfair control.

### Result

Continuous model (no checks, pure contest), People's share relative to an even
split:

| gain | 4A | 3A-merged | 3A-dropped |
|---|---|---|---|
| 0 | 0.944 | 0.938 | 0.949 |
| 4 | 0.877 | 0.884 | 0.910 |

Four actors and a fair three-actor merge are within half a percent of each
other. The unfair control is the outlier. **In a pure contest, separating AI
from Enterprise changes essentially nothing** — and the apparent difference
reported before the fair merge existed was an artefact of deleting the row.

Action model (200 seeds, per-capita ENHANCE), at check/enhance ratio 3:

| condition | People / even | High Potential |
|---|---|---|
| 4A | 0.998 +/- 0.018 | 50% |
| 3A-merged | 0.848 +/- 0.015 | 5% |
| 3A-dropped | 0.862 +/- 0.014 | 9% |

Here the separation matters a great deal, and the confidence intervals do not
overlap. With AI as its own actor People reach parity and half the runs reach
High Potential; merged into Enterprise they reach 0.85 and 5%.

**So the fourth actor earns its place only in the model that contains checks.**
The continuous model is a pure contest and is indifferent to how the same
capability is labelled. The action model has actors acting on each other, and
there two medium actors that each draw checks behave differently from one
large actor that outpaces them.

Figure: `figures/fig8_three_vs_four.png`. Code: `questions/rq2_three_vs_four.py`.

### Caveats

- `aspiration` is normalised by `2/n` and HHI has a floor of `1/n`, so neither
  is comparable across actor counts. Everything above is reported as People's
  share relative to an even split, which is 1.0 at parity whatever the actor
  count.
- The behavioural merge changes the action counts: the four-actor world runs
  more ENHANCE per tick (two actors grab rather than one) and proportionally
  fewer CHECK. The mechanism behind the gap is therefore not simply "more
  checks"; it is that the same capability split between two actors is checked
  more effectively than when it sits in one. That is a claim about this model's
  dynamics, not a general result.
- The fair-merge design predates this model. The earlier version's numbers are
  not reusable, because it gave AI an exogenous logistic capability curve and
  so assumed the conclusion, but that part of its design was right and is kept.
