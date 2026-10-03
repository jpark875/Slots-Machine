import pytest

from slots.__main__ import main
from slots.game import play
from slots.machine import DEFAULT_MACHINE

# Stops on the default strip: cherry 0-5, lemon 6-10, orange 11-14, bell 15-17, bar 18, seven 19.
SEVEN, CHERRY, LEMON = 19, 0, 6


class Rigged:
    """Feeds fixed stop indices to the machine."""

    def __init__(self, *stops):
        self.stops = iter(stops)

    def randrange(self, n):
        return next(self.stops)


def session(machine_rng, commands, balance=100, bet=10):
    lines = []
    script = iter(commands)
    final = play(
        DEFAULT_MACHINE, balance, bet, machine_rng, ask=lambda _: next(script), say=lines.append
    )
    return final, "\n".join(lines)


def test_jackpot_pays_the_multiple_of_the_bet():
    final, out = session(Rigged(SEVEN, SEVEN, SEVEN), ["", "q"])
    assert final == 100 - 10 + 5000
    assert "JACKPOT" in out


def test_small_win_and_loss():
    final, out = session(Rigged(CHERRY, CHERRY, LEMON, CHERRY, LEMON, LEMON), ["", "", "q"])
    # Two cherries returns the stake; the second spin loses it.
    assert final == 90
    assert "win +10" in out and "no win" in out


def test_bet_command_changes_the_stake_and_validates():
    final, out = session(Rigged(CHERRY, LEMON, LEMON), ["b 25", "b 0", "b x", "b 500", "", "q"])
    assert "Bet is now 25." in out
    assert out.count("Bet must be a whole number") == 3
    assert final == 75


def test_unknown_input_shows_help():
    _, out = session(Rigged(), ["what", "q"])
    assert "spin" in out.splitlines()[1]


def test_session_ends_when_credit_runs_out():
    final, out = session(Rigged(CHERRY, LEMON, LEMON), [""], balance=10, bet=10)
    assert final == 0
    assert "Out of credit." in out


def test_end_of_input_quits_cleanly():
    def eof(_):
        raise EOFError

    lines = []
    assert play(DEFAULT_MACHINE, 50, 5, Rigged(), ask=eof, say=lines.append) == 50


def test_play_rejects_nonpositive_amounts():
    with pytest.raises(ValueError):
        play(DEFAULT_MACHINE, 0, 1, Rigged())


def test_cli_odds_and_simulate(capsys):
    assert main(["odds"]) == 0
    assert "96.25%" in capsys.readouterr().out
    assert main(["--seed", "3", "simulate", "--trials", "5", "--spins", "1000"]) == 0
    assert "average pulls" in capsys.readouterr().out


def test_cli_play_reads_stdin(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "q")
    assert main(["--seed", "1", "play", "--balance", "20", "--bet", "2"]) == 0
    assert "Final balance 20" in capsys.readouterr().out


def test_cli_reports_bad_values(capsys):
    assert main(["play", "--balance", "0"]) == 2
    assert "error" in capsys.readouterr().err
