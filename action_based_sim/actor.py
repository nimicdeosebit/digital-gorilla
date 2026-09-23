"""One agent per societal actor. There are no sub-actor decomposition."""

from dataclasses import dataclass


@dataclass
class Actor:
    name: str
