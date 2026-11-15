# LO1: Requirements analysis and test strategy

This document supports Learning Outcome 1 of the portfolio. It classifies the
60 requirements in `REQUIREMENTS.md`, chooses a way to test each group, and
says where each choice is weak. Requirement numbers (for example 3.5) refer to
`REQUIREMENTS.md`.

## 1. Range of requirements (portfolio 1.1)

The requirements fall into three kinds.

| Kind | Count | Which | What "passing" means |
|---|---|---|---|
| Functional | 52 | Everything not listed below | The behaviour is correct or it is not |
| Measurable quality | 4 | 6.5, 7.5, 7.6, 8.5 | A number meets a stated threshold |
| Qualitative | 4 | 6.6, 7.8, 8.7, 8.8 | Judged by review, not by a test result |

Within those kinds, the requirements cover several different concerns:

- **Correctness of rules:** dealing, betting, pots and hand ranking (groups 1 to 5).
- **Performance:** the equity estimate must finish within 1 second at the in-game setting (7.6).
- **Statistical accuracy:** the estimate must be within 2 percentage points of the exact value (7.5).
- **Robustness:** bad input never crashes the game or changes its state (3.8, 7.4, 8.1, 8.4).
- **Information hiding:** a bot never receives another player's cards, and the display never shows them before showdown (6.2, 8.6). This is the closest thing the game has to a security requirement.
- **Reproducibility:** the same seed and inputs give the same game (8.5).
- **Maintainability and usability:** separated modules, configurable bots, readable output (6.6, 8.7, 8.8).

## 2. Levels of requirements (portfolio 1.2)

| Level | Count | Which | Example |
|---|---|---|---|
| Unit: one module alone | 32 | 1.1 to 1.5; 2.1; 3.1 to 3.6, 3.11; 4.1 to 4.3; 5.1 to 5.6; 6.3 to 6.6; 7.1, 7.2, 7.4 to 7.6; 8.8 | 5.4: the ace is low only in A-2-3-4-5 |
| Integration: modules together | 19 | 2.2 to 2.8; 3.7 to 3.10; 4.4, 4.5; 6.1, 6.2; 7.3, 7.7; 8.3, 8.4 | 4.4: the engine gives each side pot (`pot.py`) to the best eligible hand (`evaluator.py`) |
| System: the whole game | 9 | 2.9, 2.10; 4.6; 7.8; 8.1, 8.2, 8.5 to 8.7 | 2.10: a full bot-only tournament ends with one winner |

The split follows the code. The small modules (`card`, `deck`, `player`,
`pot`, `betting`, `evaluator`, `probability`) have no knowledge of the game
engine and can be tested alone. `game.py` joins them, so anything about turn
order, hand stages or payout is an integration requirement. Anything that
needs `main.py`, typed commands or many hands in a row is a system requirement.

Some properties appear at more than one level on purpose. Chip handling is
checked at unit level (4.1: the pot equals the contributions), at integration
level (8.3: no balance goes negative after any action) and at system level
(4.6: the table still holds 9,000 chips after every hand). A fault that slips
past one level should be caught at the next.

## 3. Test approach for each group (portfolio 1.3)

| Group | Main approach | Why this approach |
|---|---|---|
| 1. Cards and deck | Example-based unit tests; one property test that any sequence of shuffles and draws never produces a duplicate or lost card | The module is tiny and its rules are counts and uniqueness, which are exact |
| 2. Hand flow | State-based tests: drive `PokerGame` through each stage and check the allowed next stage; scripted hands for fold-out, all-in run-out and heads-up; one seeded bot-only tournament | The engine is a state machine (`GameState`), so the natural test is of states and transitions |
| 3. Betting and blinds | Equivalence partitioning of each action into legal and illegal classes; boundary values at the edges (raise of minimum minus 1, minimum, maximum, maximum plus 1; call with exactly enough chips; blinds at a level change) | Betting rules are numeric ranges, and faults in range rules sit at the edges |
| 4. Pots and payout | Hand-worked side-pot scenarios (two, three and four all-in amounts, with and without folded money); property test that pots plus refunds always equal the money put in | Side pots have a few tricky shapes that need exact expected answers, plus one conservation rule that must hold for every input |
| 5. Hand evaluation | One hand-written example per category and per tie-break rule; property test comparing the fast evaluator with the brute-force one on thousands of random 5 to 7 card sets (5.5); property tests that reordering the cards or swapping suits never changes the result | The input space is about 134 million seven-card hands, far too many for examples; the code already contains a second implementation to compare against |
| 6. Bots | Call `Bot.decide` directly on many generated situations and check the action is legal (6.1); inspect what `get_bot_situation` hands over (6.2); count bets and raises over 2,000 fixed situations per strategy (6.5) | Bot choices are random, so single examples prove little; legality must hold for every situation and style differences only show in frequencies |
| 7. Probability estimate | Unit tests for the sum, ranges and rejected input; accuracy test against exact answers found by enumerating every outcome on the turn and river; timed runs for 7.6; a state snapshot before and after for 7.7 | The estimate is random, so it needs a known right answer and a tolerance, not an exact expected value |
| 8. Robustness and state | Scripted keyboard input fed to `main.py` with captured output (8.1, 8.2, 8.6); invariant checks run after every action of full seeded games (8.3); two runs with one seed compared line by line (8.5); code review for 8.7 and 8.8 | These are properties of the whole program, so they are tested from the outside or across whole games |

Techniques used across the plan: example-based unit testing, equivalence
partitioning, boundary-value analysis, state-based testing, integration
testing, system testing with scripted input, property-based testing,
comparison against a reference implementation, statistical testing with a
tolerance, performance timing, and review.

Three of these go beyond plain example testing and are worth naming because
they do most of the work on the hard requirements:

- **Reference comparison (5.5).** `evaluate_bruteforce` tries all 21 five-card
  choices and is simple enough to trust; `evaluate` is fast but intricate.
  Random hands are fed to both and any disagreement is a fault.
- **Relations that must hold without knowing the answer.** Swapping all hearts
  for spades cannot change a hand's rank; adding an opponent cannot raise the
  win probability; the pot can never pay out more than was put in. These find
  faults in cases nobody thought to write down.
- **Tolerance chosen from the statistics (7.5).** With 10,000 simulations the
  standard error of the win probability is at most 0.5 percentage points, so
  the 2-point tolerance is four standard errors. A correct estimator would
  fail by chance fewer than once in 10,000 runs, and with a fixed seed never.

## 4. How appropriate the approach is (portfolio 1.4)

### Where it is strong

- Every requirement has at least one planned test or, for the four
  qualitative ones, a planned review.
- The riskiest code gets the strongest technique. Side pots, minimum raises
  and heads-up order are where the game has had faults before, and they get
  boundary values and hand-worked scenarios, not just a happy-path test.
- Random behaviour is controlled, not ignored: tests pass their own seeded
  random generator, so a failure can be replayed.

### Where it is weak

| Weakness | Effect | What is done about it |
|---|---|---|
| The reference evaluator is not fully independent: both `evaluate_bruteforce` and the five-card path of `evaluate` call `evaluate_five` | A fault in `evaluate_five` would be shared by both and the comparison would still pass | Five-card hands are checked with hand-written examples for every category and tie-break (5.1, 5.3, 5.4) |
| Exact equity is only enumerated on the turn and river, and only heads-up | Pre-flop and multi-opponent accuracy is not checked against a true value | Pre-flop is checked against two published heads-up figures; multi-opponent is checked only for the sum and for "more opponents never helps" |
| The timing test (7.6) depends on the machine | It could fail on a slow CI runner with no real fault | Limits are three to four times the measured time; the measured figure is reported as well as pass or fail |
| `bot_turn` in `main.py` silently replaces an illegal bot action with a safe one | A system-level game would hide a bot that breaks 6.1 | 6.1 is tested by calling `Bot.decide` directly, not through `main.py` |
| 6.2 is tested by inspecting the data passed to the bot | Python cannot stop code from reaching other objects, so this shows the interface is clean, not that leaking is impossible | Accepted; noted as a limit |
| 6.5 measures how often bots bet, not how well they play | A bot could be legal, distinct and still play badly | Accepted: quality of play is not a requirement |
| State-based tests cover each stage change, not every sequence of actions | A fault needing a rare sequence of raises and all-ins could be missed | The seeded full games with invariant checks exercise many sequences that were not hand-written |
| 8.7 (clear output) and 8.8 (separation) are judged by review | The result depends on the reviewer | A checklist is used in the LO5 review so the judgement is repeatable |
| Tests are written after the existing code | Tests may follow what the code does instead of what the rules say | Expected results are worked out from the requirement and the rules of poker before running the code; new code (instrumentation, fixes) is written test-first |

### Deliberately left out

- **Shuffle fairness.** The game uses Python's own `random.shuffle`. Testing
  the standard library's randomness was judged unnecessary; 1.3 checks
  only that a shuffle keeps the same 52 cards.
- **Security testing.** The game runs locally, has no network, no files and no
  accounts, so there is nothing to attack beyond the information hiding
  already covered by 6.2 and 8.6.
- **Load and stress testing.** There is one user and no concurrency. The only
  heavy computation is the equity estimate, covered by 7.6.
- **Usability testing with real users** and **testing on Windows.** Not done;
  CI will run on Linux and development is on macOS.

Each of these would be a real gap for a different kind of software, for
example an online poker site, and is a valid choice only because of what this
program is.
