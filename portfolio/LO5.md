## 5. Conduct Reviews and Inspections and Design and Implement Automated Testing Processes

### 5.1 Identify and Apply Review Criteria to Selected Parts of the Code and Identify Issues in the Code

I reviewed evaluator.py and pot.py in detail, which decides winners and chip movement. Criteria comes from the lectures (meaningful names, bad data considered and tested, exceptions explicit, consistent types, formatting) plus function cyclomatic complexity < 20 and no duplicated logic. They were two functions in evaluator.py that had a cyclomatic complexity of slightly over 20, so they are still testable. I found two weaknesses. First, the slow and fast evaluator calls the same five-card function, so the five-card hands have no independent checks. Second, Pot stored players contribution and the total, and if the two disagreed, build_side_pots would hide it. As a check on the review 200,000 random hands gave identical results from fast and slow evaluator and 30,000 random pots lost no chips, so I did not find any functional bug. As the coder and tester, I may have had blind spots.

### 5.2 Construct an Appropriate CI Pipeline for the Software

The pipeline is a GitHub Actions workflow that starts by itself on every push and pull request, on a clean machine, using Python 3.10 and 3.13. It has three steps. It installs test tools (pytest, pytest-cov). It runs all 140 tests while measuring branch coverage, and fails if total coverage falls below 70%. It then plays 20 seeded bot-only tournaments, which fail if any invariant breaks  The 70% gate is a safety net under the current 80% target. The steps run is the same as run_checks.sh.

### 5.3 Automate Some Aspects of the Testing

Every test is executable and follows arrange, act, assert with expected values written in the test. Following the test pyramid, most of the 140 cases are unit and integration level, and a few system tests drive the whole hands and seeded tournaments with no screen interaction. run_checks.sh runs the same two pipeline steps locally with one command.

### 5.4 Demonstrate the CI Pipeline Functions as Expected

Running run_checks.sh on XXX: all 140 tests passed in 7.0s with 75% branch coverage, then all seeded 20 tournaments ran to a winner. TODO: RUn on GithuB.
