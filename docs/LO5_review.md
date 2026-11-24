# LO5: code review record (20 Nov 2026)

**Scope.** `evaluator.py` (326 lines) and `pot.py` (118 lines). Chosen because they decide who wins and how many chips move. The two evaluator functions have the highest cyclomatic complexity in the game (26 and 25; the slides call above 20 complex and above 50 very hard to test). No function in the game reaches 50.

**Criteria** (from the lecture checklist, plus two of my own): meaningful names; bad data considered and tested; exceptions explicit; consistent types; formatting; cyclomatic complexity of 20 or less per function; no duplicated logic or double sources of truth.

**Method.** Read both modules against the criteria. Cyclomatic complexity counted with a short script (decisions plus one). Two ad hoc checks, not part of the test suite: 200,000 random hands of 5, 6 and 7 cards, `evaluate` against `evaluate_bruteforce`; 30,000 random pots, checking that main pot, side pots and refunds add up to the chips put in.

**Result: no functional bug found.** All 200,000 hands agreed; every one of the 30,000 pots conserved its chips. The issues below are risks and design weaknesses. Nothing was fixed (review is report only).

## evaluator.py

| # | Issue | Does the game reach it? |
|---|---|---|
| E1 | `evaluate` (26) and `evaluate_five` (25) are over the complexity threshold of 20, with many early returns. | Yes, but both are exhaustively checked by oracle and boundary tests. |
| E2 | Two implementations repeat the ranking logic. The oracle `evaluate_bruteforce` calls `evaluate_five`, and `evaluate` hands 5-card hands to `evaluate_five`, so for 5 cards there is no independent oracle, only hand-written expected values. | Yes: limits what the oracle proves. |
| E3 | No check for duplicate cards. Five copies of one card are not rejected and are ranked as high card. | No: the deck has unique cards, and the simulation invariant check would flag duplicates. |
| E4 | `EvaluatedHand` defines `==` and `<` only. Instances cannot go in sets or dict keys, and `<=` and `>=` do not work. | No: the game only compares with `<` and `==`. |
| E5 | Magic numbers: 14 (ace high), the ace-as-1 trick in `_straight_high`, and the counts 4, 3 and 2, with no named constants. | Readability only. |
| E6 | The flush loop in `evaluate` overwrites `flush_ranks` for each suit with five or more cards. Correct up to 9 cards, wrong beyond. | No: at most 7 cards. |
| E7 | `describe_hand` treats any unknown rank as high card, and the functions have almost no type hints. | Readability only. |

## pot.py

| # | Issue | Does the game reach it? |
|---|---|---|
| P1 | Two sources of truth: `amount` and `contributions`. `build_side_pots` patches over the gap with "unattributed" chips, and if `amount` is below the sum of contributions the gap is silently ignored. | No: the invariant check confirms they agree after every action. |
| P2 | `add_bet` and `add_all_in` repeat the same bookkeeping, with inconsistent messages ("Player has folded and cannot bet" and "A folded player cannot bet"). | Readability only. |
| P3 | `award` adds chips with `player.chips += ...`, bypassing the `Player` API (which has no method to receive chips). | Works; weak encapsulation. |
| P4 | `add_bet` accepts non-integer amounts (for example 2.5) and does not check the type. | No: amounts come from the betting round. |
| P5 | An all-in player calling `add_bet` gets "does not have enough chips" instead of "already all-in", which misleads. | No: the betting round blocks it first. |
| P6 | If no contesting player has contributed, `build_side_pots` refunds everything, including folded players' chips, without a warning. | No: the last player standing has always put chips in. |

## Also from LO3

Dead code, found by coverage: `Bot.choose_action` and its helpers, and the three unused `PokerGame` methods `determine_winners`, `get_bot_probability_report` and `get_probability_report`. Not deleted (too large an edit); reported as a finding.

## Not done

Review of the other eight modules; a second reviewer (all review was by me, the author, so issues from shared assumptions are likely missed).
