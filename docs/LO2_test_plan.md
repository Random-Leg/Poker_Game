# LO2: Test plan

This plan says what will be tested, in what order, with what tools, how
results are judged, and what could go wrong. The plan is expected to change;
changes are recorded at the end.

## 1. Context and scope

**Item under test:** a command-line Texas Hold'em tournament in Python, ten
modules, about 3,960 lines, one human against eight bots.

**Features to be tested:** all 60 requirements, in eight groups: cards and
deck, hand flow, betting and blinds, pots and payout, hand evaluation, bots,
probability estimate, robustness and state integrity.

**Features not to be tested:** fairness of the shuffle (Python's library is
trusted), security, load, behaviour on Windows, and how well the bots play.

## 2. Assumptions and constraints

- One person is developer, test designer and tester.
- The game code already exists, so tests for existing code are written after
  it. New code (instrumentation and fault fixes) is written test-first.
- Changes to the game code must stay small.
- Tools: `pytest` to run tests, `coverage.py` for statement and branch
  coverage, `hypothesis` for property-based tests, `mutmut` for mutation
  testing, GitHub Actions for continuous integration.

## 3. Risks and what is done about them

1. **Tests copy what the code does instead of what the rules say** (the same
   person wrote both). *Control:* every expected result is worked out by hand
   from the requirement or the rules of poker before the test is run.
2. **Random behaviour makes tests fail only sometimes.** *Control:* every test
   that involves chance sets a fixed seed; statistical tests use a tolerance
   of four standard errors.
3. **The timing test fails on a slow machine.** *Control:* limits are three to
   four times the measured time; the measured time is reported.
4. **A tool cannot be installed or does not work.** *Control:* property tests
   can fall back to seeded loops with Python's `random`; mutation testing can
   fall back to a small set of hand-made faults.
5. **Testing finds many faults.** *Control:* faults are graded critical,
   severe, moderate or cosmetic; critical and severe are fixed, the rest are
   recorded.
6. **Instrumentation changes how the game behaves.** *Control:* the same
   seeded game is run before and after each instrumentation change and the
   output compared.

## 4. Test strategy

### Order of work

Modules are integrated **bottom-up**, following which module uses which:

1. `card`, `deck`, `player` (use nothing else)
2. `evaluator`, `pot`, `betting`
3. `probability`, `bot`
4. `game` (uses all of the above)
5. `main` (the whole program)

Bottom-up needs no stubs, because everything a module uses has already been
tested. The tests themselves act as the drivers. Within each step the
**critical modules** go first: `evaluator`, `pot` and `betting` decide who
wins and how much, and they contain the trickiest rules (side pots, minimum
raises, the ace-low straight). Unit testing is finished for a module before
it is used in integration tests, so that a failure in an integration test
points at the interaction and not at the module.

### Model of the hand

The engine is a finite state machine with seven states:

`NEW_HAND -> PRE_FLOP -> FLOP -> TURN -> RIVER -> SHOWDOWN -> HAND_COMPLETE -> NEW_HAND`

and one extra transition from each of the four betting states straight to
`HAND_COMPLETE` when all but one player fold. That is 11 legal transitions.
The integration tests cover every one of them, and check that each illegal
move (for example flop to river) is rejected. The model leaves out the
betting inside each state, which has too many combinations to list; that is
covered by the betting unit tests and by full seeded games.

### Scaffolding

- **Stacked deck:** a test replaces the shuffle so that chosen cards are dealt
  in a chosen order. Needed for any test about who wins.
- **Scripted player:** typed input is replaced by a list of commands, and
  printed output is captured.
- **Fixed equity:** `Bot.decide` already accepts a win probability, so bot
  tests do not have to run the simulation.
- **Bot-only game:** nine bots play a whole tournament from a seed with no
  human. This is the driver for the system tests.

### Test design rule

Each test names the requirement it checks in its first line. There is one
test file per requirement group, eight in total, so the file list shows at a
glance which groups are covered.

### What happens when a test fails

1. Decide whether the test or the code is wrong, using the requirement.
2. If the code is wrong, record the fault: what, where, severity, and which
   kind of test found it.
3. Fix critical and severe faults. The failing test stays as the regression
   test for that fault.

## 5. Pass and fail criteria

A requirement **passes** when all tests naming it pass. Testing as a whole is
**complete** when:

- every one of the 60 requirements has at least one passing test (or a
  completed review, for the four qualitative ones);
- no critical or severe fault is open;
- branch coverage is at least 95% for `card`, `deck`, `player`, `pot`,
  `betting` and `evaluator`, 90% for `probability`, 85% for `game` and 80%
  for `bot`;
- the mutation score is at least 80% for `evaluator`, `pot` and `betting`.

`main.py` has no coverage target: it is mostly printing, and is covered by
the system tests.

## 6. Order of activities

1. Instrumentation and scaffolding.
2. Unit tests for `card`, `deck`, `player`, then `evaluator`, `pot`, `betting`.
3. Unit tests for `probability` and `bot`.
4. Integration tests: hand flow, payout, state rules. Needs step 2.
5. System tests: scripted games and bot-only tournaments. Needs steps 1 and 4.
6. Coverage and mutation runs; fault fixes. Needs steps 2 to 5.
7. Code review and continuous integration. Needs only some tests to exist, so
   it does not have to wait for step 6.
8. Evaluation of the results.

## 7. Monitoring

Progress is judged after each step from three numbers: how many of the 60
requirements have a passing test, branch coverage per module, and the number
of open faults by severity.

## 8. Changes to this plan

- 12 Nov: first version.
- 12 Nov: simplified. Removed hours, dates and the stakeholder section; the
  schedule became an ordered list of activities.
