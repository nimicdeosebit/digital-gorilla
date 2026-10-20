"""Shock engine. Fires at most one from the Table 7 shock per tick, probabilistically."""

import random
from typing import Optional

from action_based_sim.config import SimulationConfig
from action_based_sim.state import State
from action_based_sim.tables import SHOCKS


def maybe_fire_shock(state: State, config: SimulationConfig, rng: random.Random) -> Optional[dict]:
    if rng.random() >= config.shock_probability:
        return None
    # Only shocks whose conflict pair is present in this run can fire, so the
    # three-actor baseline is not handed AI shocks with nobody to receive them.
    eligible = [
        s
        for s in SHOCKS
        if s["favored_actor"] in state.actors and s["disfavored_actor"] in state.actors
    ]
    if not eligible:
        return None
    shock = rng.choice(eligible)
    amount = config.shock_magnitude * state.P[shock["modality"]][shock["disfavored_actor"]]
    state.transfer_share(shock["modality"], shock["disfavored_actor"], shock["favored_actor"], amount)
    return shock
