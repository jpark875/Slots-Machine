"""Reel layout, paytable and the exact odds that follow from them."""

from __future__ import annotations

import random
from collections.abc import Mapping
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import product
from types import MappingProxyType

REELS = 3

#: Stops per symbol on every reel.
DEFAULT_WEIGHTS = MappingProxyType(
    {"cherry": 6, "lemon": 5, "orange": 4, "bell": 3, "bar": 1, "seven": 1}
)

#: Payout multiplier of the bet for three matching symbols.
DEFAULT_PAYTABLE = MappingProxyType(
    {"cherry": 8, "lemon": 12, "orange": 20, "bell": 40, "bar": 100, "seven": 500}
)


@dataclass(frozen=True)
class Machine:
    """Independent identical reels. Three of a kind pays per `paytable`; exactly two
    cherries pays `two_cherries`. The jackpot is three of `jackpot_symbol`.
    """

    weights: Mapping[str, int] = field(default_factory=lambda: DEFAULT_WEIGHTS)
    paytable: Mapping[str, int] = field(default_factory=lambda: DEFAULT_PAYTABLE)
    two_cherries: int = 1
    jackpot_symbol: str = "seven"
    _strip: tuple[str, ...] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.weights or any(w < 1 or int(w) != w for w in self.weights.values()):
            raise ValueError("every symbol needs a positive whole-number weight")
        unknown = set(self.paytable) - set(self.weights)
        if unknown:
            raise ValueError(f"paytable has symbols not on the reels: {sorted(unknown)}")
        if self.jackpot_symbol not in self.weights or self.jackpot_symbol not in self.paytable:
            raise ValueError("the jackpot symbol must be on the reels and in the paytable")
        if self.two_cherries and "cherry" not in self.weights:
            raise ValueError("two_cherries needs a cherry on the reels")
        strip = tuple(s for s, w in self.weights.items() for _ in range(w))
        object.__setattr__(self, "_strip", strip)

    @property
    def stops(self) -> int:
        return len(self._strip)

    def spin(self, rng: random.Random) -> tuple[str, ...]:
        """One pull: a symbol per reel."""
        return tuple(self._strip[rng.randrange(self.stops)] for _ in range(REELS))

    def payout(self, symbols: tuple[str, ...]) -> int:
        """Multiplier of the bet won by a result; 0 for a loss."""
        if len(symbols) != REELS:
            raise ValueError(f"expected {REELS} symbols, got {len(symbols)}")
        if len(set(symbols)) == 1:
            return self.paytable.get(symbols[0], 0)
        if symbols.count("cherry") == 2:
            return self.two_cherries
        return 0

    def is_jackpot(self, symbols: tuple[str, ...]) -> bool:
        return symbols == (self.jackpot_symbol,) * REELS

    def _outcomes(self):
        """Every distinct result with its exact probability."""
        for combo in product(self.weights, repeat=REELS):
            probability = Fraction(1)
            for symbol in combo:
                probability *= Fraction(self.weights[symbol], self.stops)
            yield combo, probability

    def jackpot_probability(self) -> Fraction:
        return Fraction(self.weights[self.jackpot_symbol], self.stops) ** REELS

    def expected_pulls_to_jackpot(self) -> Fraction:
        return 1 / self.jackpot_probability()

    def hit_frequency(self) -> Fraction:
        """Chance that a pull pays anything."""
        return sum((p for combo, p in self._outcomes() if self.payout(combo) > 0), Fraction(0))

    def return_to_player(self) -> Fraction:
        """Expected payout per unit bet. Below 1 means the house keeps the difference."""
        return sum((p * self.payout(combo) for combo, p in self._outcomes()), Fraction(0))


DEFAULT_MACHINE = Machine()
