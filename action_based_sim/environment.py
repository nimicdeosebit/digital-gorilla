"""Environment: one self-contained simulation instance (state, actors, RNG,
history), so a second instance later is a new object, not a refactor. This
matters for the global-local environment proposed in the paper."""

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
from action_based_sim.tables import MODALITIES


class Environment:
    def __init__(self, config: SimulationConfig, environment_id: str = None):
        self.id = environment_id or config.environment_id
        self.config = config
        self.rng = random.Random(config.seed)
        self.state = State(config.actors)
        self.actors: List[Actor] = [Actor(name) for name in config.actors]
        self.history: List[dict] = []
        self._volatility_window = deque(maxlen=config.volatility_window)
        self._check_outcomes = deque(maxlen=config.volatility_window)

    def _update_legitimacy(self) -> None:
        """Relax each actor's legitimacy toward what its own position earns it.

        The target is 1 - (that actor's mean share across the modalities): an
        actor that concentrates power is decreasingly seen as holding it
        rightfully. This is the paper's claim that legitimacy is what
        distinguishes authority from mere power (Sec. 3.2), turned into the
        simplest rule that expresses it.

        Off by default (legitimacy_rate = 0.0), because freezing legitimacy is
        what the original model did and the two need to stay comparable.
        """
        repair = getattr(self.config, "legitimacy_repair", 0.0)
        if repair > 0.0 and "State" in self.state.L:
            # Transparency duties rebuild the STATE's standing specifically:
            # the lever is the State being seen to audit. Applying it to every
            # actor raises the legitimacy of the actors being audited too,
            # which makes them harder to check and inverts the lever.
            self.state.L["State"] = min(
                self.config.legitimacy_ceiling,
                self.state.L["State"] + repair,
            )

        rate = self.config.legitimacy_rate
        if rate <= 0.0:
            return
        for actor in self.state.actors:
            held = mean(self.state.P[m][actor] for m in MODALITIES)
            earned = max(0.0, min(1.0, 1.0 - held))
            updated = self.state.L[actor] + rate * (earned - self.state.L[actor])
            self.state.L[actor] = max(
                self.config.legitimacy_floor,
                min(self.config.legitimacy_ceiling, updated),
            )

    def tick(self, t: int) -> dict:
        chosen_actions = [
            policies.decide(actor.name, self.state, self.config, self.rng)
            for actor in self.actors
        ]

        total_moved = 0.0
        for action in chosen_actions:
            moved, success = actions_module.resolve_action(
                action, self.state, self.config, self.rng
            )
            total_moved += moved
            if action.type == ActionType.CHECK:
                self._check_outcomes.append(1.0 if success else 0.0)

        shock = events.maybe_fire_shock(self.state, self.config, self.rng)
        if shock:
            total_moved += self.config.shock_magnitude

        self._update_legitimacy()
        self.state.check_columns_sum_to_one()

        self._volatility_window.append(total_moved)

        asp = metrics.aspiration(self.state)
        stab = metrics.stability(self.state)
        vol = metrics.volatility(
            recent_volatility=mean(self._volatility_window),
            recent_check_success_rate=mean(self._check_outcomes) if self._check_outcomes else 0.5,
        )
        quadrant = metrics.classify_quadrant(asp, stab)

        record = {
            "tick": t,
            "actions": [
                (a.actor, a.type.value, a.modality, a.target, a.mechanism)
                for a in chosen_actions
            ],
            "shock": shock["id"] if shock else None,
            "aspiration": asp,
            "stability": stab,
            "volatility": vol,
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
