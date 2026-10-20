# Actor count comparison

### Purpose

The project's stated question -- whether AI as a fourth actor changes the
dynamics -- had never been run, because neither model had a three-actor mode.
Both now do: `SimulationConfig(actors=[...])` in the action model, and
`continuous_sim/variants.py` for the continuous one. Dropping an actor
renormalises each modality back to 1, which spreads its share over the others
in proportion to what they already hold.

### Caveat that has to be quoted with any result

`aspiration` divides People's mean share by `2/n`. A three-actor run and a
four-actor run are therefore scored against different bars (0.333 vs 0.250),
and the aspiration numbers are **not comparable across actor counts**. Compare
raw People share, or People's share relative to an even split.

### Result

Action model, 200 seeds, `per_capita`, ratio 1.0: People hold 0.224 without AI
and 0.197 with it. The confidence intervals do not overlap at any swept ratio.

Continuous model, 200 rounds: People hold 0.316 without AI and 0.236 with it.
Relative to an even split the two are almost identical when spillover is off
(0.949 vs 0.944), and diverge monotonically as spillover strengthens
(0.896 vs 0.846 at gain 10).

So AI's presence costs People absolute share in both models, while leaving them
at roughly the same position relative to parity -- unless epistemic spillover is
switched on, and then AI's presence costs them progressively more.

Figure: `figures/fig7_actor_count.png`. Data: `sweep_actor_count.csv`,
`sweep_threshold_by_actors.csv`.
