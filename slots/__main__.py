"""Command line: `python -m slots play|simulate|odds`."""

from __future__ import annotations

import argparse
import random
import sys

from slots.game import play
from slots.machine import DEFAULT_MACHINE
from slots.simulate import average_pulls, simulated_return


def cmd_odds(args: argparse.Namespace) -> int:
    machine = DEFAULT_MACHINE
    print(f"stops per reel        {machine.stops}")
    print(f"jackpot probability   {machine.jackpot_probability()}")
    print(f"expected pulls        {float(machine.expected_pulls_to_jackpot()):,.0f}")
    print(f"hit frequency         {float(machine.hit_frequency()):.2%}")
    print(f"return to player      {float(machine.return_to_player()):.2%}")
    return 0


def cmd_simulate(args: argparse.Namespace) -> int:
    machine, rng = DEFAULT_MACHINE, random.Random(args.seed)
    exact = float(machine.expected_pulls_to_jackpot())
    mean = average_pulls(machine, args.trials, rng)
    print(f"average pulls to jackpot over {args.trials} runs: {mean:,.0f} (exact {exact:,.0f})")
    rtp = simulated_return(machine, args.spins, rng)
    print(
        f"return to player over {args.spins:,} spins: {rtp:.2%} "
        f"(exact {float(machine.return_to_player()):.2%})"
    )
    return 0


def cmd_play(args: argparse.Namespace) -> int:
    play(DEFAULT_MACHINE, args.balance, args.bet, random.Random(args.seed))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="slots", description=__doc__)
    parser.add_argument("--seed", type=int, help="seed the random generator")
    sub = parser.add_subparsers(dest="command", required=True)

    odds = sub.add_parser("odds", help="print the exact odds")
    odds.set_defaults(func=cmd_odds)

    sim = sub.add_parser("simulate", help="estimate the odds by simulation")
    sim.add_argument("--trials", type=int, default=200, help="jackpots to average")
    sim.add_argument("--spins", type=int, default=500_000, help="spins for the return estimate")
    sim.set_defaults(func=cmd_simulate)

    game = sub.add_parser("play", help="play interactively")
    game.add_argument("--balance", type=int, default=100)
    game.add_argument("--bet", type=int, default=1)
    game.set_defaults(func=cmd_play)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
