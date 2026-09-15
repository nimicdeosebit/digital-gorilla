"""config.py -- every tunable number in the model lives here."""

RATE = 0.16     # step size: each round closes this fraction of the gap to the contest target. Changes how fast, not where. PLACEHOLDER.
ROUNDS = 200    # length of a run. Must exceed settling time (~28 rounds at RATE=0.16); longer only matters once shocks exist. PLACEHOLDER.

GAIN = 0.0      # epistemic spillover: an actor's epistemic share raises its capability in the OTHER four modalities by this much. 0 = off, flat capability. PLACEHOLDER.
SELF_GAIN = 0.0 # the same boost applied to the epistemic modality itself. Off: self-reinforcement here runs away. Kept as a parameter so the variant can be tested.
