import random

import pytest

from slots.machine import DEFAULT_MACHINE, Machine
from slots.simulate import average_pulls, pulls_to_jackpot, simulated_return

COIN = Machine(weights={"seven": 1, "cherry": 1}, paytable={"seven": 8}, two_cherries=0)


def test_pulls_to_jackpot_is_at_least_one():
    assert pulls_to_jackpot(COIN, random.Random(0)) >= 1


def test_average_pulls_tracks_the_exact_expectation():
    mean = average_pulls(DEFAULT_MACHINE, 300, random.Random(2024))
    assert mean == pytest.approx(8000, rel=0.2)
    assert average_pulls(COIN, 2000, random.Random(5)) == pytest.approx(8, rel=0.1)


def test_simulated_return_tracks_the_exact_rtp():
    rtp = simulated_return(DEFAULT_MACHINE, 300_000, random.Random(11))
    assert rtp == pytest.approx(float(DEFAULT_MACHINE.return_to_player()), abs=0.06)


@pytest.mark.parametrize("func", [average_pulls, simulated_return])
def test_counts_must_be_positive(func):
    with pytest.raises(ValueError):
        func(DEFAULT_MACHINE, 0, random.Random(0))
