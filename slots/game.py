"""Interactive text game. Input and output are injected so it can be tested."""

from __future__ import annotations

import random
from collections.abc import Callable

from slots.machine import Machine

HELP = "[enter] spin   b <amount> change bet   q quit"


def play(
    machine: Machine,
    balance: int,
    bet: int,
    rng: random.Random,
    ask: Callable[[str], str] | None = None,
    say: Callable[[str], None] = print,
) -> int:
    """Run a session until the player quits or cannot cover the bet. Returns the balance."""
    ask = ask or input
    if balance < 1 or bet < 1:
        raise ValueError("balance and bet must be positive")
    say(f"Balance {balance}, bet {bet}. {HELP}")

    while balance >= bet:
        try:
            command = ask(f"[{balance}] > ").strip().lower()
        except EOFError:
            break
        if command in ("q", "quit"):
            break
        if command.startswith("b"):
            balance_bet = _parse_bet(command[1:], balance)
            if balance_bet is None:
                say(f"Bet must be a whole number from 1 to {balance}.")
            else:
                bet = balance_bet
                say(f"Bet is now {bet}.")
            continue
        if command:
            say(HELP)
            continue

        symbols = machine.spin(rng)
        won = machine.payout(symbols) * bet
        balance += won - bet
        line = " | ".join(symbols)
        if machine.is_jackpot(symbols):
            say(f"{line}  JACKPOT! +{won}")
        elif won:
            say(f"{line}  win +{won}")
        else:
            say(f"{line}  no win")

    if balance < bet:
        say("Out of credit.")
    say(f"Final balance {balance}.")
    return balance


def _parse_bet(text: str, balance: int) -> int | None:
    text = text.strip()
    if not text.isdigit():
        return None
    value = int(text)
    return value if 1 <= value <= balance else None
