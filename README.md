# Texas Hold'em Poker (CLI)

A text-based Texas Hold'em tournament written in Python. You play against eight computer opponents, each using a passive, balanced or aggressive strategy. The game covers the full rules: blinds that rotate and rise over time, four betting rounds, side pots, split pots, hand evaluation and a final showdown. On your turn you can also ask for a Monte Carlo estimate of your chance of winning the hand.

It uses only the Python standard library. You only need `pytest` if you want to run the tests.

## Features

- **Nine players at the table:** you plus eight bots (`Player 2` to `Player 9`). Everyone starts with 1,000 chips.
- **Complete hand flow:** pre-flop, flop, turn, river and showdown. The dealer, small blind and big blind rotate after each hand.
- **Rising blinds:** the blinds go up every 10 hands: 10/20 → 15/30 → 25/50 → 50/100 → 75/150 → 100/200.
- **Betting rules enforced:** fold, check, call, bet, raise and all-in, with minimum raises applied and illegal actions rejected without changing the game state.
- **Pot handling:** side pots for players who are all-in at different amounts. When a pot is split, any odd chips go to the winners seated closest to the dealer's left.
- **Hand evaluator:** picks the best five cards out of seven, covering every hand from high card up to a royal flush. It handles kickers and treats the ace as low in an A-2-3-4-5 straight.
- **Bots:** pre-flop hands are scored with the Chen formula, and after the flop the bots decide using their equity and the pot odds. Their tuning settings are in `STRATEGY_SETTINGS` in `bot.py`.
- **Probability helper:** a Monte Carlo estimate of your win, tie and loss chances against the opponents still in the hand. It also includes exact odds helpers based on outs.
- **Reproducible games:** pass `--seed` to get the same deals every time you run it.

## Requirements

- Python 3.9 or newer
- `pytest` (only for running the tests)

## Getting started

```bash
git clone https://github.com/Random-Leg/Poker_Game.git
cd Poker_Game

# optional: set up a virtual environment for the tests
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install pytest
```

## Playing

```bash
python3 main.py              # start a game
python3 main.py --seed 42    # get the same deals every run
```

### Controls

| Input | Action |
|---|---|
| `f` / `fold` | Fold |
| `c` / `check` / `call` | Check if you can, otherwise call |
| `b 20` / `bet 20` | Bet 20 |
| `r 40` / `raise 40` | Raise by 40 **on top of** the current bet |
| `a` / `all-in` | Go all-in |
| `p` | Show your estimated win, tie and loss chances |
| `q` | Leave the table |

You get another hand after each one finishes, until you're knocked out, you quit, or only one player has chips left.

## Running the tests

```bash
python -m pytest
```

There are around 370 tests in `tests/`, covering cards and the deck, the evaluator, betting, pots and side pots, players, bots, the probability module, the game engine and the CLI. `pytest.ini` puts the project root on the import path, so you run the tests from the project root folder.

## Project structure

```
.
├── main.py           # CLI entry point: table setup, game loop, output
├── game.py           # PokerGame engine: hand states, blinds, dealing, showdown
├── betting.py        # BettingRound: legal actions, minimum raise, round completion
├── pot.py            # Pot: player contributions, main and side pots
├── evaluator.py      # Hand ranking and tie-breaks (best 5 of 7)
├── probability.py    # Monte Carlo equity and exact odds helpers
├── bot.py            # Bot strategies (passive / balanced / aggressive)
├── player.py         # Player state: chips, cards, bets, folded or all-in
├── card.py           # Card, Rank, Suit (unique IDs 0–51)
├── deck.py           # 52-card deck: shuffle and draw
├── pytest.ini
├── REQUIREMENTS.md   # Full project requirements specification
└── tests/
```

## Configuration

The main settings are constants you can edit directly:

- `STARTING_CHIPS`, `HUMAN_NAME` and `BOT_STRATEGIES` (which strategy each bot seat uses) in `main.py`
- `DEFAULT_BLIND_LEVELS` in `game.py`, and the `hands_per_level` argument to `PokerGame` (default 10)
- `STRATEGY_SETTINGS` in `bot.py`, which controls how tight, aggressive or bluff-prone each style is
- The number of Monte Carlo simulations, set with `simulations` on `monte_carlo_equity` / `PokerGame.get_human_equity` (2,000 in game)

## Probability assumptions

The win estimate treats opponents' hole cards as random cards drawn from the deck, leaving out the cards you can see. It doesn't take into account how the opponents have bet. It uses the same evaluator as the game, so the results are consistent with how hands are actually ranked at showdown.

## Requirements specification

The full specification for the project, covering deck, betting, blind, pot, evaluator, bot, probability and testing requirements, is in [REQUIREMENTS.md](REQUIREMENTS.md).