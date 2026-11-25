## 1. Analyze requirements to determine appropriate testing strategies

### 1.1 Range of Requirements, Functional Requirements, Measurable Quality Attributes, Qualitative Requirements

The game has 57 requirements in eight groups (deck, hand flow, betting, pots, hand evaluation, bots, probability and robustness), written in `REQUIREMENTS.md`. 49 are functional correctness requirements, 4 are measurable, and 4 are qualitative (checked by inspection).

### 1.2 Level of Requirements, System, Integration, Unit

There are three levels of requirements. 29 requirements are unit level, 19 integration level and 9 system level. Chip handling is required at all three levels as deliberate redundancy so that pot equals contributions, no balance goes negative and table holds 9,000 chips after every hand.

### 1.3 Identifying Test Approach for Chosen Attributes

Applying the partition principle, betting is tested with equivalence classes of legal and illegal actions and boundary values around the minimum and maximum raise. Hand flow is a state machine, so it gets state-based tests. Hand evaluation has 134 million seven-card inputs, so beyond one example per category, I compare the fast evaluator with brute force reference on random hands, using diversity (back-to-back testing). The estimate is random, so it is testing statistically against exactly enumerated odds with 2-point tolerance. Randomness is seeded (restriction) so a failing test fails every time (sensitivity).

### 1.4 Assess the Appropriateness of Your Chosen Testing Approach

Testing is optimistically inaccurate, so I recorded where it could accept faulty code. The reference evaluator shares its five card routine with the fast one, so a fault there passes the comparison; five-card hands rely on hand-written test cases instead. Exact odds can only be enumerated heads up on the turn and river, so multi-opponent accuracy is unchecked. Tests were written after the code, so expected results are largely derived from the rules of poker, not from running the code. Timing tests depend on the machine; 2,000 simulations took 0.22 s against a 1 s limit and still passed on the CI runner. Shuffle fairness, security and load and validation with real users are not tested.
