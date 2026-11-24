# LO3: Test results

Supporting detail for `portfolio/LO3.md`. Run with `python3 -m pytest`; coverage with
`python3 -m pytest --cov --cov-branch --cov-report=term-missing`.

## 1. What was run

All 140 cases pass (sandbox: Python 3.13, about 5 s; the Mac run of the same suite also passed).

| Test file | Requirement group | Technique | Cases |
|---|---|---|---|
| `test_1_cards_deck.py` | Cards and deck | Partition, boundary values (IDs 0 and 51, outside values) | 6 |
| `test_2_hand_flow.py` | Hand flow and progression | State and transition coverage, stacked deck, heads-up and elimination cases | 19 |
| `test_3_betting.py` | Betting and blinds | Partition, boundary values, illegal actions leave state unchanged | 21 |
| `test_4_pots.py` | Pots and payout | Category-partition of side pots, odd chip, chip conservation over 25 hands | 8 |
| `test_5_evaluation.py` | Hand evaluation | Ten categories, kickers, ties, ace-low straight, brute-force reference on 600 hands | 28 |
| `test_6_bots.py` | Bots | Legal actions, statistical comparison of styles over 2,000 decisions | 9 |
| `test_7_probability.py` | Probability estimate | Sum to 1, invalid input, exactly enumerated odds, timing | 18 |
| `test_8_robustness.py` | Robustness | Scripted human input, quitting, same seed same game, hidden cards | 8 |
| `test_instrumentation.py` | Instrumentation | Corrupted states detected, simulator behaviour (see LO2) | 23 |

Measured: 2,000 simulations against eight opponents 0.22 s (limit 1 s); 10,000 simulations 1.12 s (limit 5 s).
No fault was found in the game.

## 2. Do the tests detect faults? (17 faults put in by hand)

Each fault was put into a scratch copy of the game on its own and the suite was run. 16 were caught.

| Fault put in | Caught by |
|---|---|
| Minimum raise off by one | raise minimum test |
| Minimum opening bet off by one | opening bet test |
| Short all-in changes the minimum raise | short all-in test |
| Check allowed with one chip owed | legal actions test |
| Call allowed with a stack one chip short | legal actions test |
| No ace-low straight | reference comparison |
| Four-card straight | reference comparison |
| Unmatched chips not returned | pot refund test |
| Odd chip to the wrong seat | odd chip test |
| Duplicate player names accepted | nine players test |
| Blinds rise one hand late | blind levels test |
| Board not dealt out when one player still has chips | run-out test |
| Shuffle loses a card | shuffle test |
| Zero opponents accepted by the estimate | invalid input test |
| Ties counted as wins | tie test |
| Pre-flop bot may fold a free check | bot test |
| Game starts a hand with one player | **not caught** |

The last fault cannot be seen from outside: a later check in the same method raises the same error.
Six of the faults were missed by the first version of the suite; tests were added for them and they were
re-run, so the figure above is after that improvement.

## 3. Branch coverage (Mac run, 24 Nov, 140 tests, 75% overall)

| Module | Statements | Missed | Cover | What is not covered |
|---|---|---|---|---|
| `deck.py` | 18 | 1 | 92% | empty-deck error (play cannot reach it) |
| `card.py` | 36 | 1 | 97% | text conversion `__str__` |
| `evaluator.py` | 161 | 11 | 91% | text description of hands, length checks, comparing with a non-hand |
| `betting.py` | 131 | 7 | 92% | folded or all-in refusals in five checks; fold twice; bet of zero |
| `game.py` | 576 | 89 | 82% | probability display for the human, unused methods, rarely used display branches |
| `main.py` | 128 | 18 | 81% | parts of the start-up and prompts |
| `player.py` | 27 | 4 | 78% | error paths (negative chips, third card, bet of zero) |
| `pot.py` | 65 | 10 | 77% | error paths of `add_bet` and `add_all_in`, chips with no recorded owner |
| `bot.py` | 246 | 99 | 56% | an older decision method and its helpers, which nothing calls |
| `probability.py` | 203 | 111 | 42% | hand-type probability tables used only by the human's `p` display |

The scaffolding is covered too: `invariants.py` 93%, `simulate.py` 82%. These figures come from a run after the tests for drawing from an empty deck, fewer than five cards and invalid blinds were removed.

Unused code (nothing in the game calls it): `Bot.choose_action` and its helpers, and the `PokerGame` methods
`determine_winners`, `get_bot_probability_report` and `get_probability_report`. Tests for code that never
affects play were not written.
