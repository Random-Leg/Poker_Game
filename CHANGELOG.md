# Change log: Software Testing portfolio work

Every change made to this folder during the portfolio work, newest last.
Game code changes are marked **[code]**, documents **[doc]**, tests **[test]**.

## 12 Nov 2026: requirements reduced (LO1 groundwork)

### Files

| File | Change |
|---|---|
| `REQUIREMENTS_v1.md` | **New [doc].** Byte-for-byte copy of the original `REQUIREMENTS.md` (544 lines, 20 sections, about 230 bullet points). Kept as the "before" evidence. |
| `REQUIREMENTS.md` | **Rewritten [doc].** Now 8 groups and 61 numbered requirements (108 lines). |
| `CHANGELOG.md` | **New [doc].** This file. |

No game code, tests, README or git history were changed.

### Structure changes in `REQUIREMENTS.md`

1. 20 sections merged into 8 groups: Cards and deck (old s2); Hand flow and progression (s3, s4, s12); Betting and blinds (s5, s6); Pots and payout (s7); Hand evaluation (s8); Bots (s10); Probability estimate (s11, s17); Robustness and state integrity (s9, s13, s14, s15, s16).
2. Every requirement numbered by group (`1.1` ... `8.8`) so tests can say which requirement they check.
3. Each group is a plain bulleted list, one sentence per requirement.
4. An "Out of scope" list added at the end.

### Removed

5. Old s1 (overview) cut to one paragraph; the sentence saying testing would be developed after the core application was removed.
6. Old s18 (future testing requirements) removed: it is a list of test techniques, not a requirement on the software. It moves to the test plan (LO2).
7. Old s19 (development constraints) removed as a section; "Python, standard library only, runs locally from the command line" kept in the overview, and separation of responsibilities kept as 8.8.
8. Old s20 (potential future enhancements) removed; a short "Out of scope" list replaces it.
9. The "Running the game" notes at the end removed (they duplicate the README).
10. Old s9 (player attributes list) removed as a section: its testable content is covered by 3.2, 3.3 and 8.3.
11. Duplicates merged: "chip balance never negative" (old s9, s15) into 8.3; rotation of dealer and blinds (old s3, s6, s12) into 2.6; "bet no more than you have" (old s5, s10, s14) into 3.2; invalid-action lists (old s5, s14) into 3.8 and 8.1.
12. Lists of suits, ranks and the example blind table removed (they are in the code and README).

### Added (not in v1)

13. 1.6: shuffle fairness with a chi-square threshold. v1 only said shuffling "should normally change" the order.
14. 2.4, 2.5: hand ends when all but one fold; board is run out when no more betting is possible. Implemented in `game.py` but not stated in v1.
15. 2.7: heads-up blind and turn order. Implemented but not stated in v1.
16. 2.10: a full bot-only tournament from a fixed seed finishes with one winner and no error (system-level requirement).
17. 3.6: a short all-in does not lower the bet or change the minimum raise. Implemented but not stated in v1.
18. 4.3: unmatched chips are refunded. Implemented but not stated in v1.
19. 4.6: chip conservation across the tournament (9,000 by default).
20. 5.5: the fast evaluator must agree with the brute-force reference evaluator.
21. 6.3: a bot never folds when it can check.
22. 7.5: accuracy threshold (within 2 percentage points of exact at 10,000 simulations, heads-up reference hands).
23. 7.6: speed thresholds (2,000 simulations against eight opponents within 1 s; 10,000 within 5 s). v1 said "reasonable amount of time".
24. 7.7: asking for the estimate does not use the turn or change state.
25. 8.2: quitting ends the game cleanly.
26. 8.5: same seed and same inputs give an identical game. v1 said a fixed seed should "ideally" be supported.

### Changed in meaning

27. Bots: v1 said each of the eight bots must have a distinct strategy. The game has three strategies shared across eight bots, so 6.5 now requires the three strategies to differ measurably (ordering of bet/raise frequency over 2,000 situations).
28. Pot remainder: v1 said odd chips are handled "according to a defined rule"; 4.5 states the rule the game uses (one at a time to winners nearest the dealer's left).
29. Empty deck: v1 said drawing from an empty deck must be "handled appropriately"; 1.5 states it must raise an error.
30. Short blinds: v1 said a player short of the blind is handled "as all-in or otherwise"; 3.9 states they post what they have and are all-in.
31. Probability sum: v1 said win + tie + loss is approximately 100%; 7.1 gives a tolerance of 0.000001.

### Thresholds that need your confirmation

The numbers in 1.6, 6.5, 7.5 and 7.6 are proposals. Timing measured in a cloud sandbox (not your laptop): 2,000 simulations against eight opponents took 0.31 s and 10,000 took 1.17 s, so the 1 s and 5 s limits leave a margin of about three to four times.

## 12 Nov 2026: requirements format simplified

| File | Change |
|---|---|
| `REQUIREMENTS.md` | **Reformatted [doc].** Wording of all 61 requirements is unchanged. Removed: the `R-DECK-1` style IDs (now plain numbers, `1.1` to `8.8`); the Type column (F/Q/L) and Level column (U/I/S); the "How to read this document" legend; the tables (now bulleted lists); the Summary table. File went from 161 to 108 lines. |
| `CHANGELOG.md` | **Edited [doc].** Requirement references renumbered to match (for example `R-PROB-6` is now `7.6`); structure items 2 to 4 in the first entry reworded to describe the simplified format. |

The classification by type (functional, measurable, qualitative) and level (unit, integration, system) is not lost: it will sit in the separate LO1 test-strategy document, where sub-criteria 1.1 and 1.2 are argued, and not in the requirements themselves.

## 12 Nov 2026: shuffle fairness dropped, thresholds confirmed, clutter deleted

| File | Change |
|---|---|
| `REQUIREMENTS.md` | **Edited [doc].** Requirement 1.6 (shuffle fairness, chi-square over 10,000 shuffles) deleted at Sasvata's request. No renumbering was needed because it was the last item in group 1. The document now has 60 requirements. Shuffling is still covered by 1.3 (shuffle only reorders the deck). |
| `CHANGELOG.md` | **Edited [doc].** This entry added. Earlier entries are left as written, so item 13 and the threshold note in the first entry still mention 1.6; this entry supersedes them. |

Thresholds confirmed by Sasvata: 6.5 (bot styles differ), 7.5 (equity accuracy) and 7.6 (equity speed) stand as proposed.

Deleted from the folder (generated files, all already ignored by `.gitignore`):

- `__pycache__/` (11 compiled `.pyc` files, including a stale `hand.cpython-313.pyc` for a module that no longer exists)
- `.pytest_cache/` (cache from the old, discarded test suite)
- `.DS_Store` (macOS Finder file)

Kept on purpose: `REQUIREMENTS_v1.md` (evidence of the original requirements), `.git/`, `.gitignore`.

## 12 Nov 2026: LO1 test strategy written

| File | Change |
|---|---|
| `docs/LO1_test_strategy.md` | **New [doc].** Supports Learning Outcome 1. Four sections matching portfolio sub-criteria 1.1 to 1.4: the kinds of requirement (52 functional, 4 measurable, 4 qualitative); their levels (32 unit, 19 integration, 9 system); the test approach chosen for each of the 8 groups and why; strengths, nine named weaknesses and four deliberate exclusions. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

No game code or requirements were changed.

## 12 Nov 2026: LO1 portfolio section drafted

| File | Change |
|---|---|
| `portfolio/LO1.tex` | **New [doc].** LaTeX text for portfolio section 1 (sub-sections 1.1 to 1.4), 432 words, no tables. Written to stand alone: it states the requirements, numbers and thresholds in the text and does not use requirement numbers. Uses terms from the lecture slides (correctness, robustness, performance, maintainability, verifiable, partition, redundancy, diversity, restriction, sensitivity, optimistic inaccuracy, timeliness, verification and validation). Test-compiled at 11pt with 2.54 cm margins: about 0.53 of a page. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

`docs/LO1_test_strategy.md` is unchanged and stays as the longer supporting document the portfolio text points to.

## 12 Nov 2026: portfolio section moved from LaTeX to Markdown

| File | Change |
|---|---|
| `portfolio/LO1.md` | **New [doc].** The LO1 portfolio text in Markdown. Wording is identical to the LaTeX version; only the markup changed (heading, bold, italics, code font, quotation marks). |
| `portfolio/LO1.tex` | **Deleted [doc].** Sasvata will do the LaTeX conversion himself; everything in this folder is kept in Markdown. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

## 12 Nov 2026: references to the original requirements removed

Sasvata's instruction: the original requirements document belongs to the earlier repo and will not be submitted or referenced.

| File | Change |
|---|---|
| `portfolio/LO1.md` | **Edited [doc].** In 1.1, "I reduced the game's 20-section specification to 60 one-sentence requirements" became "The game is specified by 60 one-sentence requirements". The sentence "These replaced unverifiable wording ("a reasonable time") with verifiable thresholds" became "Each has a numeric threshold so that it is verifiable; "a reasonable time" would not be." |
| `docs/LO1_test_strategy.md` | **Edited [doc].** Removed the paragraph at the end of section 1 that pointed to `REQUIREMENTS_v1.md` and this change log. |
| `REQUIREMENTS.md` | **Edited [doc].** Title changed from "Requirements Specification (v2)" to "Requirements Specification"; removed the opening paragraph that described it as a reduced version of the original. No requirement was changed. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. Earlier entries still describe the reduction, so this file and `REQUIREMENTS_v1.md` should be left out of the final submission. |

## 12 Nov 2026: LO2 test plan written

| File | Change |
|---|---|
| `docs/LO2_test_plan.md` | **New [doc].** First version of the test plan: scope (tested and not tested), assumptions and constraints, seven risks with controls, strategy (bottom-up integration order, critical modules first, seven-state model of a hand with 11 transitions, four pieces of scaffolding, fault-handling rule), pass and fail criteria (coverage and mutation targets), a nine-step schedule, and monitoring. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

No game code was changed.

## 12 Nov 2026: time management and ISO framing removed

Sasvata's instruction: ignore all time-management information in the course PDFs, and treat ISO 29119-3 lightly because it goes well beyond what the portfolio needs.

| File | Change |
|---|---|
| `docs/LO2_test_plan.md` | **Edited [doc].** Removed: the sentence saying the plan follows ISO 29119-3 headings and its agile example; the "People" paragraph about stakeholders; the "about 40 hours" and deadline assumption (replaced by "one person is developer, test designer and tester"); risk 5 "time runs out" (seven risks became six); the schedule table with hour estimates, target dates and the critical-path paragraph (replaced by section 6, an eight-step ordered list with dependencies); the dated fallback in Monitoring. A line was added to "Changes to this plan". Scope, strategy, model, scaffolding and pass/fail criteria are unchanged. |
| `docs/LO1_test_strategy.md` | **Edited [doc].** Two phrases about time reworded: usability and Windows testing are now "Not done" (was "Out of reach in the time available"); shuffle fairness was "judged unnecessary" (was "judged not worth the time"). |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

`portfolio/LO1.md` and `REQUIREMENTS.md` contained no time-management or ISO content and were not changed.

## 19 Nov 2026: instrumentation added (LO2)

Instrumentation is the extra code that lets the game be observed, checked and controlled while it runs. It is added as new files only; no existing game module was edited (each of the ten `.py` modules was compared with the copy before this work and is identical).

| File | Change |
|---|---|
| `invariants.py` | **New [code].** Checks that a game state is consistent: chips in stacks plus the pot equal the starting total; no negative chips or pot; the pot's per-player record adds up to the pot; each player holds 0 or 2 hole cards; the number of community cards matches the state (0, 3, 4, 5); no card appears twice across hands, board and deck; during betting the player to act has not folded, is not all-in and has chips; a player with no chips and a hand is marked all-in. `find_violations` returns the problems as text; `check_invariants` raises `InvariantViolation`. It only reads the game. |
| `simulate.py` | **New [code].** Plays whole tournaments with all nine seats played by bots, checking the invariants after dealing, after every action, after showdown and after each reset. It records every action (the history), counts illegal bot actions instead of hiding them (the real game's `bot_turn` silently falls back to check, call or fold), stops a hand that needs more than 300 actions, and reports the hand number and the last 8 actions when a check fails. A seed makes a tournament repeatable. By default post-flop decisions use a random win probability so a tournament takes about 0.1 s; `--real-equity` uses the real 250-game Monte Carlo (about 3 s). Run with `python simulate.py --seed 1 --tournaments 20`. |
| `tests/test_instrumentation.py` | **New [test].** 23 tests: no violations on fresh and started games; 9 deliberately corrupted states (extra chip, chip missing from pot, negative chips, third hole card, six community cards, card in two hands, card in hand and deck, folded player to act, board not matching state) are each detected; tournaments for seeds 1 to 5 finish with one player holding all 9000 chips; the same seed gives an identical history and different seeds differ; illegal bot actions are counted; an injected chip leak in `Pot.add_bet` is caught with the hand number and recent actions in the message. |
| `pytest.ini` | **New [test].** Minimal: `pythonpath = .` and `testpaths = tests`. Replaces the one deleted earlier. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

Results: 23 of 23 tests pass. 300 seeded tournaments (seeds 100 to 399) raised no invariant violation and no illegal bot action. 297 finished; 3 (seeds 119, 166, 238) hit the 1000-hand limit because two passive bots kept trading chips at the highest blinds. This happens only with the random win probability: seed 119 finishes in 85 hands with the real Monte Carlo. 10 tournaments with the real Monte Carlo (seeds 1 to 10) also raised nothing.

Not done, to be written up as improvements: logging inside `game.py`, timestamps, assertions inside the game itself, and recording each bot's strategy per decision.

No existing game code was changed. Note: `__pycache__` has reappeared in the folder from running the game; it is ignored by `.gitignore`.

## 19 Nov 2026: LO2 portfolio text and plan update

| File | Change |
|---|---|
| `portfolio/LO2.md` | **New [doc].** The LO2 portfolio text (about 455 words, four paragraphs: plan, evaluation of the plan, instrumentation, evaluation of the instrumentation). The sentence in square brackets at the end of 2.2 is a placeholder: it must be replaced with real results (targets met, faults found) once the tests have been run. |
| `docs/LO2_test_plan.md` | **Edited [doc].** The "Bot-only game" scaffold now names `simulate.py` and `invariants.py`. One sentence added to the test design rule: tests of the instrumentation check the tools, not a requirement, and sit in their own file. A 19 Nov line added under "Changes to this plan". Nothing else changed. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

`REQUIREMENTS_v1.md` is kept (Sasvata's instruction). No game code was changed.

## 19 Nov 2026: coverage and mutation testing deferred

Sasvata's instruction: do not do coverage and mutation testing for now, present it as a limitation due to time, and add it when the rest of the project is done.

| File | Change |
|---|---|
| `docs/LO2_test_plan.md` | **Edited [doc].** Tools: `coverage.py` and `mutmut` marked planned but deferred. Section 5: the coverage and mutation bullets moved out of the completion criteria into a "Deferred criteria" paragraph (targets kept, so they can be restored). Section 6 step 6 is now "Fault fixes" with a note. Section 7: monitoring by two numbers (was three). A line added under "Changes to this plan". |
| `portfolio/LO2.md` | **Edited [doc].** 2.1: completion criteria no longer include coverage and mutation; one sentence says they were deferred for lack of time. 2.2: the sentence about thresholds replaced by one saying deferral leaves test strength unmeasured; "every criterion is a number" became "checkable". The bracketed placeholder is still there. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

Still to be changed when coverage and mutation are added back: this plan, `portfolio/LO2.md` and (if it mentions them) the LO3 and LO4 text. No game code was changed.

## 19 Nov 2026: LO3 test suite written

All new files in `tests/` [test]. No game code was changed (the ten modules are identical to before).

| File | Change |
|---|---|
| `tests/helpers.py` | **New [test].** Shared scaffolding: card shorthand (`card("AH")`), a stacked deck (`stack_deck` replaces the shuffle so chosen cards are dealt), game builders (`table`, `full_table`), a state snapshot and small drivers (check/call, fold, play to a state). |
| `tests/test_1_cards_deck.py` | **New [test].** Cards and deck, 5 tests. |
| `tests/test_2_hand_flow.py` | **New [test].** Hand flow and tournament progression, 10 tests: main line of states, fold exit from each betting state, wrong-state operations rejected and changing nothing, fold-around win, board run-out when all are all-in (including one player left with chips), dealer and blinds skipping eliminated seats, heads-up order, nine unique players, game over, bot-only tournaments. |
| `tests/test_3_betting.py` | **New [test].** Betting and blinds, 13 tests: legal actions by state with boundary cases, amount to call, bet and raise minimums at the boundary, short all-in, folded and all-in players, illegal actions leaving state unchanged, big-blind option, blind levels, bad blind configurations, short stacks posting blinds. |
| `tests/test_4_pots.py` | **New [test].** Pots and payout, 8 tests: contributions, main and side pots, refund, best hand per pot, eliminated shortest stack, uncalled chips in a heads-up all-in, odd chip, chip conservation over 25 hands. |
| `tests/test_5_evaluation.py` | **New [test].** Hand evaluation, 9 tests: ten categories, best five of five to seven cards, ordering and kickers, ties, ace-low straight, fewer than five cards, fast evaluator against the brute-force reference on 600 hands. |
| `tests/test_6_bots.py` | **New [test].** Bots, 5 tests: legal actions and amounts, never folds a free check, bad strategy and empty legal list, the three styles over 2,000 decisions, a bot is given only its own hole cards. |
| `tests/test_7_probability.py` | **New [test].** Probability estimate, 5 tests: sums to 1, invalid input, no repeated cards, accuracy against exactly enumerated odds, timing; plus one test that a hand playing the board is a tie. |
| `tests/test_8_robustness.py` | **New [test].** Robustness, 6 tests: bad human input, quitting (q, end of input, Ctrl-C), same seed gives identical games, tournaments with invariants, bot cards hidden before showdown, probability request leaves state unchanged. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

Results in the sandbox (Python 3.13, pytest 9.1.1): the whole suite, including `test_instrumentation.py`, is 149 test cases (about 72 test functions) and all pass in about 5 s. No fault was found in the game.

To check that the tests can fail, 17 hand-made faults were put into a scratch copy of the game one at a time (not in this folder): 16 were caught, 1 survived. The survivor removed the "at least 2 players" check at the start of `start_hand`; the same error is still raised a few lines later by the blind posting, so the fault cannot be seen from outside. The faults were: raise and bet minimums off by one, a short all-in reopening the raise size, a check allowed with one chip owed, a call beyond the stack, no ace-low straight, a four-card straight, no refund of unmatched chips, odd chip to the wrong seat, duplicate names accepted, blinds rising a hand late, no board run-out, a shuffle that loses a card, zero opponents accepted, ties counted as wins, and a bot folding a free check.

Not done: coverage (to be run on the Mac with `pytest --cov`) and mutation testing (deferred).

## 19 Nov 2026: three tests removed, coverage config added

Sasvata's instruction: do not test situations that can never happen in the game.

| File | Change |
|---|---|
| `tests/test_1_cards_deck.py` | **Edited [test].** Removed `test_draw_from_empty_deck_raises` (drawing from an empty deck). The game never draws more than 23 cards from a 52-card deck. |
| `tests/test_5_evaluation.py` | **Edited [test].** Removed `test_fewer_than_five_cards_is_rejected` (3 cases). The game always passes 5 to 7 cards. |
| `tests/test_3_betting.py` | **Edited [test].** Removed `test_invalid_blind_configuration_is_rejected` (5 cases). The game uses fixed blind levels. |
| `.coveragerc` | **New [test].** Two lines: branch coverage on, and the `tests/` folder left out of the coverage figures so they describe the game only. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

The suite is now 140 test cases, all passing. Requirements 1.5, 3.11 and 5.6 now have no test; `REQUIREMENTS.md` has not been changed yet (decision pending with Sasvata).

## 19 Nov 2026: three requirements dropped (60 become 57)

Sasvata's instruction: drop from `REQUIREMENTS.md` the requirements whose tests were removed. Each was the last in its group, so no other number changed.

| File | Change |
|---|---|
| `REQUIREMENTS.md` | **Edited [doc].** Removed 1.5 (drawing from an empty deck raises an error), 3.11 (invalid blind configuration is rejected) and 5.6 (fewer than five cards is rejected). 57 requirements remain. |
| `portfolio/LO1.md` | **Edited [doc].** Numbers only: 60 became 57 requirements; 52 became 49 functional; 32 became 29 unit level (integration 19 and system 9 are unchanged). |
| `docs/LO1_test_strategy.md` | **Edited [doc].** Same numbers: 57 requirements; functional 49; unit 29, with its list now "1.1 to 1.4; 2.1; 3.1 to 3.6; 4.1 to 4.3; 5.1 to 5.5; ...". |
| `portfolio/LO2.md`, `docs/LO2_test_plan.md` | **Edited [doc].** "60 requirements" became "57 requirements" (four places). |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

`REQUIREMENTS_v1.md` and older CHANGELOG entries still say 60; they describe earlier states and were left alone.

## 19 Nov 2026: LO3 write-up, coverage restored in the plan

| File | Change |
|---|---|
| `portfolio/LO3.md` | **New [doc].** The LO3 portfolio text (about 450 words, 3.1 to 3.4). Three coverage figures are in square brackets (`evaluator`, `game`) because they come from a run made before three tests were removed; replace them after a fresh coverage run. |
| `docs/LO3_results.md` | **New [doc].** Supporting results: tests per file and technique, timing, the 17 hand-made faults and which were caught, branch coverage per module with what is not covered, and the unused code found. |
| `docs/LO2_test_plan.md` | **Edited [doc].** Coverage is back as a completion criterion with the original per-module targets (95% for `card`, `deck`, `player`, `pot`, `betting`, `evaluator`; 90% `probability`; 85% `game`; 80% `bot`) and in monitoring (three numbers again). Only mutation testing stays "Deferred", now with a note that hand-made faults are the only check on fault detection. Tools list: `coverage.py` in use. Step 6 is "Coverage run and fault fixes". A line added under "Changes to this plan". |
| `portfolio/LO2.md` | **Edited [doc].** 2.1: coverage targets restored, only the mutation score deferred. 2.2: the bracketed placeholder is gone; it now says that deferring mutation testing leaves fault detection partly measured and that finding no fault may mean sound code or shared assumptions. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

The original coverage targets were set on 12 Nov, before any measurement, so they are kept unchanged for comparison in LO4 (achieved against target). No game code was changed.

## 20 Nov 2026: LO4 write-up

| File | Change |
|---|---|
| `portfolio/LO4.md` | **New [doc].** The LO4 portfolio text (about 460 words, 4.1 to 4.4). Mutation testing is written as a reflection only (Sasvata's choice; allowed by the lecturer's 19 Nov relaxation): not run for lack of time, and what it would add is described in 4.4. Coverage figures are in square brackets until a fresh run replaces them. The 95% interval for the fault-detection rate (16 of 17 caught gives about 71% to 100%) is an exact binomial (Clopper-Pearson) calculation. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

No game code or tests were changed.

## 20 Nov 2026: LO5 review, pipeline and automation (5.4 not yet done)

| File | Change |
|---|---|
| `docs/LO5_review.md` | **New [doc].** Code review record for `evaluator.py` and `pot.py`: criteria, method, seven evaluator issues, six pot issues, the dead code from LO3. No functional bug found; nothing fixed (Sasvata: report only). Two ad hoc checks were run for it and are not part of the suite: 200,000 random hands (fast evaluator against the brute-force oracle) and 30,000 random pots (chip conservation). |
| `ci/tests.yml` | **New [tool].** GitHub Actions workflow (kept in `ci/` because the tools cannot write into `.github/`; move it to `.github/workflows/tests.yml` when pushing): pytest with branch coverage and a 70% total gate on Python 3.10 and 3.13, then 20 seeded `simulate.py` tournaments. Not pushed. The 70% gate is a guess pending a fresh coverage run; adjust it after. Only its YAML syntax was checked. |
| `run_checks.sh` | **New [tool].** Runs the same two steps locally. Only its syntax was checked (`bash -n`); not yet run, because running it is the 5.4 evidence. |
| `portfolio/LO5.md` | **New [doc].** LO5 text (about 340 words). 5.4 is a placeholder. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

No game code or tests were changed.

## 24 Nov 2026: the three removed tests were still in the folder; now removed

Sasvata's coverage run collected 149 tests, not 140. The three tests dropped on 19 Nov (and their requirements) were still in the Mac copy of `tests/`.

| File | Change |
|---|---|
| `tests/test_1_cards_deck.py` | **Edited [test].** Removed `test_draw_from_empty_deck_raises` (1 case). |
| `tests/test_3_betting.py` | **Edited [test].** Removed `test_invalid_blind_configuration_is_rejected` (5 cases). |
| `tests/test_5_evaluation.py` | **Edited [test].** Removed `test_fewer_than_five_cards_is_rejected` (3 cases). |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

149 minus 9 cases leaves 140. The tests were not run here (this shell has no pytest); only syntax was checked. A backup of the old `tests/` folder is in `/tmp` on the sandbox, not in the folder. No game code changed.

## 24 Nov 2026: fresh coverage run, brackets replaced, 5.4 local evidence

Sasvata ran `pytest --cov` (140 passed, 75% total) and `./run_checks.sh` (tests, coverage gate 70% reached at 75.03%, 20 seeded tournaments all finished, 0 illegal bot actions).

| File | Change |
|---|---|
| `portfolio/LO3.md` | **Edited [doc].** Brackets replaced with the fresh figures (evaluator 91%, game 82%), added deck 92%, player 78% and 75% overall; run time "about seven seconds"; 3.4 now says deck, betting and evaluator are within four points. |
| `portfolio/LO4.md` | **Edited [doc].** Same figures in 4.3. `deck` no longer meets 95% (92%; its one missed line is the unreachable empty-deck error, left untested after that test was removed). Removed my unverified claim that excluding dead code would put `bot` and `probability` "close to target"; it now says only that excluding it would raise both. |
| `docs/LO3_results.md` | **Edited [doc].** Coverage table updated (deck, evaluator, game), note added for `invariants.py` 93% and `simulate.py` 82%. |
| `portfolio/LO5.md` | **Edited [doc].** 5.4 filled from the local `run_checks.sh` run; the real GitHub Actions run and screenshot remain to be added after the push. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

No game code or tests changed.

## 24 Nov 2026: requirement 2.8 reworded

| File | Change |
|---|---|
| `REQUIREMENTS.md` | **Edited [doc].** 2.8 now reads "A player with zero chips at the end of a hand must be eliminated: not dealt in and not asked to act in later hands." The phrase "and not able to win a pot" was dropped (Sasvata's decision): an eliminated player is never dealt cards, so it adds nothing a test could check. The count stays at 57. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

Comments in `tests/test_2_hand_flow.py` and `tests/test_4_pots.py` that mention 2.8 were left as they are. `REQUIREMENTS_v1.md` and older entries are unchanged.

## 25 Nov 2026: LO4 reworked; reliability check added

| File | Change |
|---|---|
| `tournament_stats.py` | **New [tool].** Runs many seeded bot-only tournaments (fast mode) through `simulate.play_tournament`, counts failures (any exception: broken invariant, crash, stuck hand) and unfinished tournaments, and prints exact Clopper-Pearson 95% bounds. Game code unchanged. |
| `portfolio/LO4.md` | **Edited [doc].** Rewritten to Sasvata's points. 4.1: bot strength, real users, common-mode risk. 4.2: coverage per module, accuracy and speed, and a reliability target added for this section. 4.3: adds the statistical result. 4.4: delete dead code, property-based tests, second reviewer and usability session. Mutation testing is no longer mentioned in LO4. About 540 words. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

Result of `python3 tournament_stats.py --seed 1 --tournaments 1000` (37 s, Python 3.10, seeds 1 to 1000): 0 failures; 839,685 actions checked; 987 finished (98.7%, 95% interval 97.8% to 99.3%); 13 stopped at the 1,000-hand cap; 0 illegal bot actions; failure-rate upper bound 0.37%. The cap hits are attributed to the fast mode's random equity (consistent with 3 of 300 earlier); not verified by a real-equity run.

## 25 Nov 2026: mutation testing mentioned briefly in LO4

| File | Change |
|---|---|
| `portfolio/LO4.md` | **Edited [doc].** One sentence added to the end of 4.4: mutation testing (not run for lack of time) would measure the detection rate directly, using sampled mutants. About 560 words. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

## 25 Nov 2026: LO5 5.1 rewritten

| File | Change |
|---|---|
| `portfolio/LO5.md` | **Edited [doc].** 5.1 rewritten to be clearer, at Sasvata's request. Kept: scope, criteria, complexity result (26 and 25), the oracle-independence and `Pot` double-record issues, the two ad hoc checks, nothing fixed, sole-reviewer caveat. Dropped: duplicate-card check, `EvaluatedHand` hashing and `<=`, `Pot.award` bypassing `Player`, and the reachability sentence. 5.2 to 5.4 unchanged. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |

`docs/LO5_review.md` still lists all 13 issues; it was not changed.

## 25 Nov 2026: LO5 5.2 rewritten

| File | Change |
|---|---|
| `portfolio/LO5.md` | **Edited [doc].** 5.2 rewritten to be clearer, at Sasvata's request. The workflow path is now given as `.github/workflows/tests.yml` (the file is still in `ci/tests.yml` until Sasvata moves it when pushing). The closing sentence about mutation testing and a coverage trend as next stages was dropped; added that the same steps run locally with `run_checks.sh`. 5.1, 5.3 and 5.4 unchanged. |
| `CHANGELOG.md` | **Edited [doc].** This entry added. |
