import random
from fractions import Fraction

import pytest

from slots.machine import DEFAULT_MACHINE, Machine

M = DEFAULT_MACHINE


def test_default_odds_are_exact():
    assert M.stops == 20
    assert M.jackpot_probability() == Fraction(1, 8000)
    assert M.expected_pulls_to_jackpot() == 8000
    assert M.return_to_player() == Fraction(77, 80)
    assert M.hit_frequency() == Fraction(973, 4000)


def test_outcome_probabilities_sum_to_one():
    assert sum(p for _, p in M._outcomes()) == 1


@pytest.mark.parametrize(
    ("symbols", "multiplier"),
    [
        (("seven",) * 3, 500),
        (("bar",) * 3, 100),
        (("cherry",) * 3, 8),
        (("cherry", "cherry", "lemon"), 1),
        (("cherry", "lemon", "cherry"), 1),
        (("cherry", "lemon", "orange"), 0),
        (("seven", "seven", "bar"), 0),
    ],
)
def test_payouts(symbols, multiplier):
    assert M.payout(symbols) == multiplier


def test_payout_needs_one_symbol_per_reel():
    with pytest.raises(ValueError):
        M.payout(("cherry",))


def test_jackpot_is_three_sevens_only():
    assert M.is_jackpot(("seven",) * 3)
    assert not M.is_jackpot(("bar",) * 3)


def test_spin_is_deterministic_per_seed_and_uses_known_symbols():
    first = [M.spin(random.Random(7)) for _ in range(5)]
    again = [M.spin(random.Random(7)) for _ in range(5)]
    assert first == again
    rng = random.Random(1)
    for _ in range(200):
        assert set(M.spin(rng)) <= set(M.weights)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"weights": {}},
        {"weights": {"seven": 0, "cherry": 1}},
        {"paytable": {"seven": 5, "diamond": 9}},
        {"jackpot_symbol": "bar", "paytable": {"seven": 5}},
        {"jackpot_symbol": "diamond"},
        {"weights": {"seven": 1}, "paytable": {"seven": 5}},
    ],
)
def test_invalid_machines_are_rejected(kwargs):
    with pytest.raises(ValueError):
        Machine(**kwargs)


def test_custom_machine_odds():
    coin = Machine(weights={"seven": 1, "cherry": 1}, paytable={"seven": 8}, two_cherries=0)
    assert coin.jackpot_probability() == Fraction(1, 8)
    assert coin.return_to_player() == 1
