"""Power/legitimacy state for one Environment instance."""

import copy
from typing import Dict

from gorilla_sim.tables import INITIAL_LEGITIMACY, INITIAL_POWER


class State:
    def __init__(self):
        self.P: Dict[str, Dict[str, float]] = copy.deepcopy(INITIAL_POWER)
        self.L: Dict[str, float] = copy.deepcopy(INITIAL_LEGITIMACY)

    def transfer_share(self, modality: str, frm: str, to: str, amount: float) -> float:
        """Zero-sum share transfer between two actors in one modality."""
        amount = max(0.0, min(amount, self.P[modality][frm]))
        self.P[modality][frm] -= amount
        self.P[modality][to] += amount
        return amount

    def effective_strength(self, actor: str, modality: str) -> float:
        """Power discounted by legitimacy; used for CHECK success odds."""
        return self.P[modality][actor] * self.L[actor]

    def hhi(self, modality: str) -> float:
        """Herfindahl-Hirschman index for one modality's shares."""
        return sum(share * share for share in self.P[modality].values())

    def snapshot(self) -> Dict:
        return {"P": copy.deepcopy(self.P), "L": copy.deepcopy(self.L)}
