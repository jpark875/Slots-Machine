"""Monte Carlo estimates to check against the machine's exact odds."""

from __future__ import annotations

import random

from slots.machine import Machine


def pulls_to_jackpot(machine: Machine, rng: random.Random) -> int:
    """Pull until the jackpot lands and return how many pulls it took."""
    pulls = 1
    while not machine.is_jackpot(machine.spin(rng)):
        pulls += 1
    return pulls


def average_pulls(machine: Machine, trials: int, rng: random.Random) -> float:
    """Mean pulls to jackpot over independent runs."""
    if trials < 1:
        raise ValueError("trials must be at least 1")
    return sum(pulls_to_jackpot(machine, rng) for _ in range(trials)) / trials


def simulated_return(machine: Machine, spins: int, rng: random.Random) -> float:
    """Total paid out per unit staked over `spins` one-unit bets."""
    if spins < 1:
        raise ValueError("spins must be at least 1")
    return sum(machine.payout(machine.spin(rng)) for _ in range(spins)) / spins
