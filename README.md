# Slots-Machine

A three-reel slot machine with exact odds, a simulator that checks them, and a text game.

Each reel has 20 stops: 6 cherry, 5 lemon, 4 orange, 3 bell, 1 bar, 1 seven. Three of a kind
pays a multiple of the bet, exactly two cherries returns the stake, and three sevens is the
jackpot.

| Result | Pays |
|---|---|
| 7 7 7 | 500x |
| BAR BAR BAR | 100x |
| bell x3 | 40x |
| orange x3 | 20x |
| lemon x3 | 12x |
| cherry x3 | 8x |
| exactly two cherries | 1x |

## Usage

```
python -m slots odds                         # exact odds
python -m slots simulate --trials 1000       # average pulls to jackpot, return to player
python -m slots play --balance 100 --bet 5   # interactive
```

Add `--seed N` before the subcommand for repeatable runs. While playing, press Enter to spin,
`b <amount>` to change the bet and `q` to quit.

Exact odds with the default reels:

- jackpot: 1 in 8,000 pulls
- any win: 24.3% of pulls
- return to player: 96.25%

`simulate` repeats pulls until the jackpot lands, averages the count over the requested number
of runs, and compares it and the return against the exact figures.

## Tests

```
pip install -e ".[dev]"
pytest
```

To change the machine, pass a different `weights` or `paytable` to `slots.Machine`; the odds
methods recompute exactly from them.
