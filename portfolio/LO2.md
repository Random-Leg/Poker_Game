## 2. Design and implement comprehensive test plans with instrumented code

### 2.1 Construction of the Test Plan

The plan covers all 57 requirements. It lists six risks with controls, e.g. tests that copy the code instead of the rules (one person wrote both), so expected results are derived by hand from poker rules; and random failures, so every test is seeded. Modules are integrated bottom-up, critical ones (evaluator, pot, betting) first, since they decide who wins and how much. The hand is a finite state machine of 7 states and 11 transitions, each tested. Scaffolding covers a stacked deck, a scripted player, a fixed win probability for bots and bot-only tournament. Testing is complete when every requirements has a passing test and there's no critical fault. Branch coverage must reach 80% per module.

### 2.2 Evaluation of the Quality of the Test Plan

Strengths: Completion is decidable since every criterion is checkable, and the integration order isolates faults. Weaknesses: One person is developer and tester, a conflict of roles. The code existed first, so the new code is only the tests and timeliness is lost. Mutation testing is not done, so efficacy of faults is only partly measured, since coverage shows code run, not code checked. Testing found no fault in the game, which may mean sound code, or shared assumption between code and tests.

### 2.3 Instrumentation of the Code

Control already exists: a seed option and bot decision that accepts a fixed win probability. I added two new files and changed no game module. `invariants.py` checks after every actions that chips plus pot equals 9,000, no balance is negative, players have 0 or 2 cards, no card appears twice. `simulate.py` plays seeded bot-only tournaments, records every actions, counts illegal bot actions and reports failures with the last eight actions. This is justified because the chip, state and tournament requirements can't be check form outside the game.

### 2.4 Evaluation of the Instrumentation

1,000 seeded tournaments raised no violation and no illegal bot action. Limits: checks run after the actions, so a fault repaired within one action is invisible so it tests consistency rather than correctness. The game has no logging or timestamps, and in fast mode, where bots use random win probabilities, 13 of 1,000 tournaments ended at the hand limit without a winner. Improvements not made: logging in the game, timestamps, assertions in the game code and a record of each bots strategy per decision.
