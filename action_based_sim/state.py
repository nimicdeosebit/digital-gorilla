"""Power/legitimacy state for one Environment instance."""

import copy
from typing import Dict, List, Optional

from action_based_sim.tables import (
    ACTORS,
    MODALITIES,
    initial_legitimacy_for,
    initial_power_for,
)


class State:
    def __init__(self, actors: Optional[List[str]] = None):
        self.actors: List[str] = list(actors) if actors else list(ACTORS)
        self.P: Dict[str, Dict[str, float]] = initial_power_for(self.actors)
        self.L: Dict[str, float] = initial_legitimacy_for(self.actors)

    def transfer_share(self, modality: str, frm: str, to: str, amount: float) -> float:
        """Zero-sum share transfer between two actors in one modality."""
        amount = max(0.0, min(amount, self.P[modality][frm]))
        self.P[modality][frm] -= amount
        self.P[modality][to] += amount
        return amount

    def effective_strength(self, actor: str, modality: str,
                           capability=None) -> float:
        """Power discounted by legitimacy, then by capability.

        Capability is 1.0 everywhere unless a policy lever has raised or
        lowered what this actor can do in this modality (see levers.py). It
        affects both the odds of a check this actor makes and the odds of
        resisting one made against it.
        """
        strength = self.P[modality][actor] * self.L[actor]
        if capability is not None:
            strength *= capability[actor][modality]
        return strength

    def hhi(self, modality: str) -> float:
        """Herfindahl-Hirschman index for one modality's shares."""
        return sum(share * share for share in self.P[modality].values())

    def check_columns_sum_to_one(self, tol: float = 1e-9) -> None:
        """The model's one invariant, asserted rather than assumed."""
        for modality in MODALITIES:
            total = sum(self.P[modality].values())
            assert abs(total - 1.0) < tol, f"{modality} sums to {total}, not 1"

    def snapshot(self) -> Dict:
        return {"P": copy.deepcopy(self.P), "L": copy.deepcopy(self.L)}
