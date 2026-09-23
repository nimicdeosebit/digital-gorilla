"""Environment: one self-contained simulation instance (state, actors,
RNG, history), so a second instance later is a new object, not a refactor. This is important for Global-Local env proposed in the paper"""

import random
from collections import deque
from statistics import mean
from typing import List

from action_based_sim import actions as actions_module
from action_based_sim import events, metrics, policies
from action_based_sim.actions import ActionType
from action_based_sim.actor import Actor
from action_based_sim.config import SimulationConfig
from action_based_sim.state import State
from action_based_sim.tables import ACTORS


class Environment:
    def __init__(self, config: SimulationConfig, environment_id: str = None):
        self.id = environment_id or config.environment_id
        self.config = config
        self.rng = random.Random(config.seed)
        self.state = State()
        self.actors: List[Actor] = [Actor(name) for name in ACTORS]
        self.history: List[dict] = []
        self._volatility_window = deque(maxlen=config.volatility_window)
        self._check_outcomes = deque(maxlen=config.volatility_window)

    def tick(self, t: int) -> dict:
        chosen_actions = [
            policies.decide(actor.name, self.state, self.config, self.rng)
            for actor in self.actors
        ]

        total_moved = 0.0
        for action in chosen_actions:
            moved, success = actions_module.resolve_action(action, self.state, self.config, self.rng)
            total_moved += moved
            if action.type == ActionType.CHECK:
                self._check_outcomes.append(1.0 if success else 0.0)

        shock = events.maybe_fire_shock(self.state, self.config, self.rng)
        if shock:
            total_moved += self.config.effect_magnitude

        self._volatility_window.append(total_moved)

        asp = metrics.aspiration(self.state)
        stab = metrics.stability(
            self.state,
            recent_volatility=mean(self._volatility_window),
            recent_check_success_rate=mean(self._check_outcomes) if self._check_outcomes else 0.5,
        )
        quadrant = metrics.classify_quadrant(asp, stab)

        record = {
            "tick": t,
            "actions": [(a.actor, a.type.value, a.modality, a.target, a.mechanism) for a in chosen_actions],
            "shock": shock["id"] if shock else None,
            "aspiration": asp,
            "stability": stab,
            "quadrant": quadrant,
            "state": self.state.snapshot(),
        }
        self.history.append(record)
        return record

    def run(self, ticks: int = None) -> List[dict]:
        ticks = ticks if ticks is not None else self.config.ticks
        for t in range(ticks):
            self.tick(t)
        return self.history
