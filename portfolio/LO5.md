## 5. Conduct Reviews and Inspections and Design and Implement Automated Testing Processes

### 5.1 Identify and Apply Review Criteria to Selected Parts of the Code and Identify Issues in the Code

I reviewed `evaluator.py` and `pot.py`, which decide winners and chip movement, against the lecture checklist (meaningful names, bad data tested, exceptions explicit, consistent types, formatting) plus cyclomatic complexity below 20 and no duplicated logic. Two evaluator functions score 26 and 25, slightly over 20 but still testable. I found two weaknesses: the brute-force reference calls the same five-card routine as the fast evaluator, so five-card hands have no independent check, and `Pot` stores both each player's contribution and the total, so `build_side_pots` would hide any disagreement. 200,000 random hands gave identical results from both evaluators and 30,000 random pots lost no chips, so I found no functional bug. As author and only reviewer, I may share blind spots with the code.

### 5.2 Construct an Appropriate CI Pipeline for the Software

A GitHub Actions workflow runs on every push and pull request, on a clean machine with Python 3.10 and 3.13. It installs `pytest` and `pytest-cov`, runs all 140 tests with branch coverage (failing below 70%, a safety net under the 80% target), then plays 20 seeded bot-only tournaments, which fail if any invariant breaks. `run_checks.sh` runs the same steps locally.

### 5.3 Automate Some Aspects of the Testing

Every test is executable and follows arrange, act, assert with expected values written in the test. Following the test pyramid, most of the 140 cases are unit and integration level, and a few system tests drive whole hands and seeded tournaments with no screen interaction.

### 5.4 Demonstrate the CI Pipeline Functions as Expected

`run_checks.sh` on 25 Nov 2026: 140 tests passed with 75% branch coverage and all 20 seeded tournaments finished. The same workflow passed on GitHub Actions for Python 3.10 and 3.13 (Figure 1).
