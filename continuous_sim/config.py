"""config.py -- every tunable number in the model lives here."""

RATE = 0.16     # step size: each round closes this fraction of the gap to the contest target. Changes how fast, not where. PLACEHOLDER.
ROUNDS = 200    # length of a run. Must exceed settling time (~28 rounds at RATE=0.16); longer only matters once shocks exist. PLACEHOLDER.

GAIN = 0.0      # epistemic spillover: an actor's epistemic share raises its capability in the targeted modalities by this much. 0 = off, flat capability. PLACEHOLDER.
SELF_GAIN = 0.0 # the same boost applied to the epistemic modality itself. Off by argument, not measurement: it does NOT run away (tested), but it would let the unjustified initial matrix decide every run. Kept as a parameter so the variant is testable.

SPILLOVER_TARGETS = "three"  # where spillover lands. "three" = the modalities the paper enumerates (economic, authoritative, physical). "four" = also narrative, on the looser reading. This choice flips a headline result -- see mechanisms.TARGET_SETS and fig5.
