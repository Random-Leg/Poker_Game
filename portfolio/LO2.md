## 2. Design and implement comprehensive test plans with instrumented code

### 2.1 Construction of the Test Plan

The plan covers all 57 requirements. It lists six risks with controls, e.g. tests that copy the code instead of the rules (one person wrote both), so expected results are derived from poker rules. Modules are integrated bottom-up, critical ones (evaluator, pot, betting) first, since they decide who wins and how much. The hand is a finite state machine (FSM) of 7 states and 11 transitions. Scaffolding covers a stacked deck, a scripted player, a fixed win probability for bots and bot-only tournaments. Testing is complete when every requirement has a passing test and there is no critical fault. Branch coverage must reach 80% per module. Full plan is in `docs/LO2_test_plan.md`.

### 2.2 Evaluation of the Quality of the Test Plan

Strengths: Completion is decidable since every criterion is checkable, and the integration order isolates faults. Weaknesses: One person is developer and tester, a conflict of roles. The code existed first, so the tests are new code and timeliness is lost. Mutation testing is not done, so the effectiveness of the tests at catching faults is only partly measured, since coverage shows code run, not code checked. Testing found no fault in the game, which may mean sound code, or shared assumption between code and tests.

### 2.3 Instrumentation of the Code

Controllability already exists: a seed option and bot decision that accepts a fixed win probability. I added two new files and changed no game module. `invariants.py` checks after every action that chips plus pot equals 9,000, no balance is negative, players have 0 or 2 cards, no card appears twice. `simulate.py` plays seeded bot-only tournaments, records every action, counts illegal bot actions and reports failures with the last eight actions. This is justified because the chip, state and tournament requirements can't be checked from outside the game.

### 2.4 Evaluation of the Instrumentation

Across 1,000 seeded tournaments, every action was followed by an invariant check, and none failed. The limit is that the checks show consistency, not correctness: a pot paid to the wrong player still conserves chips, and a fault repaired within one action is never seen. The game also has no logging or timestamps, so a failure is reconstructed from the last eight recorded actions. Suggested Improvements: logging and timestamps in the game, assertions in the game code, and a record of each bot's reasoning per decision.
