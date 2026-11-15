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
