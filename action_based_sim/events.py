"""Shock engine. Fires at most one from the Table 7 shock per tick, probabilistically."""

import random
from typing import Optional

from action_based_sim.config import SimulationConfig
from action_based_sim.state import State
from action_based_sim.tables import SHOCKS


def maybe_fire_shock(state: State, config: SimulationConfig, rng: random.Random) -> Optional[dict]:
    if rng.random() >= config.shock_probability:
        return None
    shock = rng.choice(SHOCKS)
    amount = config.effect_magnitude * state.P[shock["modality"]][shock["disfavored_actor"]]
    state.transfer_share(shock["modality"], shock["disfavored_actor"], shock["favored_actor"], amount)
    return shock
