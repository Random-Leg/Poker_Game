## 4. Evaluate the Limitations of a Given Testing Process, Using Statistical Methods Where Appropriate, and Summarise Outcomes

### 4.1 Identifying Gaps and Omissions in the Testing Process

Bot strength is untested, the tests only prove bots act legally and that play styles differ, but nothing on how well the bot plays. No user, other than me, has tested this game, so qualitative requirements have had no usability or acceptance testing. There is a common-mode risk as well, since I wrote the code and tests, so a wrong assumption can sit on both sides.

### 4.2 Identifying Target Coverage/Performance Levels for the Different Testing Procedures

I set a branch coverage target of at least 80% for every module, one flat figure high enough to show most branches run but leaving room for code the game cannot reach, as a proxy for adequacy, so it only shows where to look and not whether results are checked. Other targets were a win-probability estimate within 2 percentage points of the exact value, 2,000 simulations under 1 second, and, as a reliability target, no failure in 1,000 bot-only tournaments.

### 4.3 Discussing How the Testing Carried Out Compares with the Target Levels

Player (78%), pot (77%), bot (56%) and probability (42%) are below the 80% target. Much of the bot and probability shortfall is likely due to unsatisfiable obligations: an older bot decision method and display-only tables are never called. The accuracy and speed targets are met. For reliability, there were 0 failures in 1,000 (bot-only) runs, so the one-sided 95% upper bound on the failure rate is about 0.3% (rule of three). I had a hand cap to prevent the simulated game running indefinitely and 13 of the 1,000 games reached it, and the median was 122 hands. It's notable that this is a simulated operational profile with bots, not real behaviour.

### 4.4 Discussion of What Would Be Necessary to Achieve the Target Levels

Delete the unused code and measure coverage again. Add property-based tests on `evaluator.py` and `pot.py`, so thousands of random cases check properties like "chips in equals chips out." Add a second reviewer to reduce the common-mode risk and run a usability session, which could also show bot strength.
