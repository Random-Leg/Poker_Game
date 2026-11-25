## 3. Apply a Wide Variety of Testing Techniques and Compute Test Coverage and Yield According to a Variety of Criteria

### 3.1 Range of Techniques

140 automated test cases, mostly black-box. Partition and boundary-values tests cover the betting rules (minimum bet, minimum raise and short all-in), blind levels and hand categories. Side pots use category partition: cases vary the number of all-in levels, a folded contributor, unmatched chips and an odd chip. The hand is a FSM, tested for state and transition coverage. Two oracles check calculations: a brute force evaluator against the fast one on 600 random hands, and exactly enumerated odds against the win-probability estimate. Statistical tests compare bot styles over 2,000 identical decisions, timing tests the estimates speed. System tests run seeded bot-only tournaments with invariant checks and scripted human input.

### 3.2 Evaluation Criteria for the Adequacy of the Testing

Each technique has its own adequacy criteria. Partition: Every class and boundary of a rule has a case. FSM: All seven states, all eleven transitions and illegal moves are rejected. Oracles: No disagreement. Estimate: Within 2 percentage points and under 1s for 2,000 simulations. Structural: Branch coverage per module at least 80%.

### 3.3 Results of Testing

All 140 cases pass in about 7 seconds and no faults found in the game. Timing is 0.22s for 2,000 simulations and 1.1s for 10,000. To test the tests, I put 17 faults in a scratch copy of the game one at a time, such as, a raise minimum off by one, a missing ace low straight etc. 16 were caught, but the survivor was unobservable. Branch coverage: card 97%, deck 92%, betting 92%, evaluator 91%, game 82%, main 81%, player 78%, pot 77%, bot 56%, probability 42% (75% overall).

### 3.4 Evaluation of the Results

Bot and Probability fall well short on coverage (56% and 42%), and Pot and Player slightly short (77% and 78%). But for Bot and Probability this is more likely dead code than weak tests. The gaps remaining are error paths in pot and each betting check refusing a folded or all-in player. Since I wrote both the code and the tests, the injected faults matter more since they show the tests can fail. The faults were chosen by me, so there is some bias.
