Poker Game — Project Requirements

1. Project Overview

The project is a text-based Texas Hold’em poker game implemented in Python.

The game will consist of one human player and eight computer-controlled players (bots), for a total of nine players at the table.

The system will implement the rules of Texas Hold’em, including card dealing, betting, blinds, hand evaluation, pot management, player elimination, and showdown.

The system will also provide the human player with an estimated probability of winning the current hand.

The project will initially focus on implementing the poker game itself. Software testing, test automation, coverage analysis, mutation testing, performance testing, and other testing activities will be developed after the core application is functional.

⸻

2. Card and Deck Requirements

2.1 Card Identification

* The game must use a standard 52-card deck.
* Every card must have a unique ID.
* Card IDs must range from 0 to 51.
* No two cards may have the same ID.
* A card’s ID must remain constant throughout the game.
* Shuffling must change the order of cards, not their identities.

2.2 Card Composition

The deck must contain:

* 4 suits:
    * Hearts
    * Diamonds
    * Clubs
    * Spades
* 13 ranks:
    * 2
    * 3
    * 4
    * 5
    * 6
    * 7
    * 8
    * 9
    * 10
    * Jack
    * Queen
    * King
    * Ace
* Every combination of rank and suit must occur exactly once.

2.3 Deck Creation

* A new deck must contain exactly 52 cards.
* All 52 cards must be unique.
* The deck must contain exactly 13 cards of each rank.
* The deck must contain exactly 13 cards of each suit.
* No cards may be missing from a newly created deck.

2.4 Shuffling

* The deck must support random shuffling.
* After shuffling, all 52 cards must still be present.
* Shuffling must not create duplicate cards.
* Shuffling must not remove cards.
* The order of cards should normally change after shuffling.
* The shuffled deck should be represented as an ordered collection from which cards can be drawn.

2.5 Drawing Cards

* Cards must be drawn from the top of the deck.
* Drawing a card must remove it from the available deck.
* A card that has been drawn must not be available for drawing again during the same hand.
* Drawing one card must reduce the number of cards in the deck by one.
* Attempting to draw from an empty deck must be handled appropriately.

⸻

3. Game Setup Requirements

* Each game must contain exactly nine players.
* There must be exactly one human player.
* There must be exactly eight bot players.
* Every player must have a unique identifier or name.
* Each player must begin with a defined number of chips.
* The dealer position must be tracked.
* The small blind position must be tracked.
* The big blind position must be tracked.
* Dealer, small blind and big blind positions must rotate between hands.
* Players with insufficient chips to continue must be handled appropriately.

⸻

4. Texas Hold’em Requirements

4.1 Hole Cards

* Each active player must receive exactly two private hole cards.
* Hole cards must be dealt face down from the perspective of other players.
* No two players may receive the same physical card.
* The human player must be able to view their own hole cards.
* A bot’s hole cards must not be revealed to the human player before showdown.

4.2 Community Cards

The game must use five community cards.

The community cards must be revealed in the following stages:

Flop

* Three community cards are revealed.

Turn

* One additional community card is revealed.

River

* One additional community card is revealed.

The final board must therefore contain exactly five community cards.

4.3 Game Phases

A hand must progress through the following stages:

1. Pre-flop
2. Flop
3. Turn
4. River
5. Showdown

The game must not skip required stages.

⸻

5. Betting Requirements

5.1 General Betting

The game must support the following player actions where legally permitted:

* Fold
* Check
* Call
* Bet
* Raise
* All-in

The available actions must depend on the current game state.

5.2 Betting Restrictions

* A player must not be able to bet more chips than they possess.
* A folded player must not be able to place further bets.
* A player who is all-in must not be required to make further betting decisions.
* A player must not be able to check when there is an outstanding bet they must match.
* A player must be able to call when sufficient chips are available.
* A player must be able to go all-in when legally permitted.
* Invalid betting actions must be rejected without corrupting the game state.

5.3 Minimum Raises

* The game must enforce a minimum legal raise amount.
* A raise below the minimum raise amount must be rejected unless it constitutes a legal all-in.
* The current highest bet must be tracked.
* The amount required for a player to call must be calculated correctly.

5.4 Betting Rounds

A betting round must continue until all remaining players have either:

* folded,
* gone all-in, or
* contributed the required amount and had the opportunity to act.

A new betting round must begin after the appropriate community cards are revealed.

⸻

6. Blinds Requirements

* Every hand must begin with a small blind and big blind.
* The small blind must be smaller than or equal to the big blind.
* The blind positions must rotate around the table.
* The dealer position must rotate between hands.
* The initial blind amounts must be configurable.
* Blind levels must increase as the game progresses.
* The number of hands/rounds required before a blind increase must be configurable.
* The system must prevent invalid blind configurations.
* Players with fewer chips than the required blind must be handled as all-in or otherwise according to the rules of the game.

Example blind structure:

Level	Small Blind	Big Blind
1	10	20
2	15	30
3	25	50
4	50	100
5	75	150
6	100	200

⸻

7. Pot Requirements

* The system must track the total pot.
* Each player’s contribution to the current hand must be tracked.
* Bets must be added to the appropriate pot.
* The pot must be awarded to the winner(s) at showdown.
* A player who folds must forfeit their contribution to the pot.
* Ties must be handled correctly.
* If multiple players have identical winning hands, the pot must be split appropriately.
* Any indivisible remainder from a split pot must be handled according to a defined rule.
* The system must support side pots when players have different amounts of chips and go all-in.

⸻

8. Hand Evaluation Requirements

The system must correctly identify all standard Texas Hold’em poker hands.

The hand rankings, from highest to lowest, are:

1. Royal Flush
2. Straight Flush
3. Four of a Kind
4. Full House
5. Flush
6. Straight
7. Three of a Kind
8. Two Pair
9. One Pair
10. High Card

8.1 Best Five Cards

* A player may have up to seven available cards:
    * two hole cards
    * five community cards.
* The evaluator must determine the best possible five-card poker hand.
* The player is not required to use both hole cards.
* The player may use zero, one, or two hole cards when forming their best five-card hand.

8.2 Tie Breaking

The evaluator must correctly distinguish between hands of the same category.

Examples include:

* Higher pair beats lower pair.
* Higher three-of-a-kind beats lower three-of-a-kind.
* Higher full house beats lower full house.
* Higher flush beats lower flush.
* Higher straight beats lower straight.
* Appropriate kickers must be considered.
* Identical hands must result in a tie.

8.3 Ace Handling

The system must correctly handle the Ace as:

* the highest card in normal circumstances;
* the lowest card when forming an A-2-3-4-5 straight.

⸻

9. Player Requirements

Each player must have:

* Unique identifier/name
* Chip balance
* Hole cards
* Current bet
* Total contribution to the current hand
* Folded status
* All-in status
* Active/inactive status

The system must correctly update these values as the game progresses.

A player’s chip balance must never become negative.

⸻

10. Bot Requirements

The game must contain eight computer-controlled players.

Each bot must have a distinct playing strategy.

The different strategies should produce recognisably different behaviour.

Each bot must:

* make only legal actions;
* respect its available chips;
* respond to the current betting state;
* have access to information that would be available to a real player;
* not access another player’s private hole cards;
* continue playing until it folds, goes all-in, or the hand ends.

Bot behaviour should be configurable independently from the main game engine.

⸻

11. Probability Calculator Requirements

The system must calculate an estimated probability of the human player’s hand winning.

The probability calculator must consider:

* the player’s hole cards;
* known community cards;
* number of remaining opponents;
* cards already known to be unavailable;
* possible future community cards.

The probability calculator must return, where appropriate:

* estimated win probability;
* estimated tie probability;
* estimated loss probability.

The probabilities should satisfy:

win probability + tie probability + loss probability ≈ 100%

The calculator should initially use Monte Carlo simulation.

The number of simulations should be configurable.

For example:

* 1,000 simulations
* 10,000 simulations
* 100,000 simulations

The system should prevent known cards from appearing again in simulated outcomes.

The probability calculator must use the same hand evaluation rules as the main poker game.

The assumptions used by the probability calculator must be clearly defined.

For example, opponent hole cards may initially be assumed to be randomly distributed among the remaining cards.

⸻

12. Game Progression Requirements

* A new hand must begin after the previous hand has concluded.
* The dealer position must rotate.
* Blinds must rotate.
* Eliminated players must no longer participate.
* A player with zero chips must be eliminated from the game.
* The game must continue while more than one player remains.
* The game must end when only one player remains.
* The final remaining player must be declared the tournament winner.

⸻

13. User Interface Requirements

The game will initially use a text-based command-line interface.

The interface should display:

* player’s hole cards;
* visible community cards;
* player’s chip balance;
* current pot;
* current blind level;
* current betting amount;
* legal actions;
* amount required to call;
* minimum legal raise;
* probability estimate where appropriate;
* relevant game events.

The interface must clearly communicate invalid user input.

The program should request another input after an invalid action rather than terminating unexpectedly.

The game should provide clear information about the result of each hand.

⸻

14. Error Handling Requirements

The system must handle invalid user input without crashing.

Examples include:

* entering a non-numeric betting amount;
* entering a negative betting amount;
* attempting to bet more chips than available;
* attempting an invalid action;
* attempting to raise below the minimum;
* attempting to act when folded;
* attempting to act when all-in;
* attempting to check when checking is not permitted.

Internal game errors should not silently corrupt the game state.

⸻

15. Game State Requirements

The game must maintain a consistent state throughout a hand.

At any point, the system should be able to determine:

* current phase;
* current player;
* dealer;
* small blind;
* big blind;
* community cards;
* remaining deck;
* current pot;
* current highest bet;
* each player’s contribution;
* each player’s chip balance;
* each player’s status.

The system must prevent impossible game states.

Examples:

* The same card appearing in two places.
* A player having more than two hole cards.
* More than five community cards.
* A player having a negative chip balance.
* A folded player taking an action.
* A player being both active and eliminated.

⸻

16. Randomness Requirements

The system must use randomisation for:

* deck shuffling;
* dealing cards;
* generation of unknown cards for probability simulations;
* random bot decisions where applicable.

Randomness should be designed so that it can be controlled or replaced during testing.

The game should ideally support the use of a fixed random seed for reproducible simulations and debugging.

⸻

17. Performance Requirements

The probability calculator should complete a configurable number of simulations within a reasonable amount of time.

The system should be capable of performing a sufficiently large number of simulations to produce useful probability estimates.

Performance should be measured rather than assumed.

Potential performance measurements include:

* simulations per second;
* time required for 1,000 simulations;
* time required for 10,000 simulations;
* time required for 100,000 simulations.

⸻

18. Future Testing Requirements

The application will subsequently be tested using multiple testing approaches.

Potential testing areas include:

* unit testing;
* integration testing;
* system testing;
* boundary-value testing;
* equivalence partitioning;
* state-based testing;
* property-based testing;
* statistical testing;
* performance testing;
* mutation testing;
* regression testing;
* robustness testing.

Testing will be developed after the core application has been implemented.

⸻

19. Development Constraints

* The application will be implemented in Python.
* The application will initially be text-based.
* The application will not require a graphical user interface.
* The application will initially run locally.
* External databases are not required for the core game.
* Internet connectivity is not required for normal gameplay.
* The implementation should prioritise clear separation of responsibilities between components.
* The implementation should avoid unnecessary complexity that does not contribute to the objectives of the project.

⸻

20. Potential Future Enhancements

These features are not part of the initial core requirements but may be considered if time permits:

* Multiple poker table configurations.
* Different starting chip amounts.
* Custom blind structures.
* Tournament mode.
* Cash-game mode.
* Different bot difficulty levels.
* More sophisticated opponent modelling.
* Expected value calculations.
* Pot odds calculations.
* Implied odds calculations.
* Hand history logging.
* Replay of previous hands.
* Statistics across multiple games.
* Graphs of player chip balances.
* Exact probability calculation.
* Comparison of exact probability against Monte Carlo estimates.
* Configurable number of Monte Carlo simulations.
* Configurable bot strategies.
* Save/load game state.

---

Running the game

    python main.py            # play
    python main.py --seed 42  # reproducible deal
    python -m pytest          # run the tests

On your turn: fold, check, call, bet, raise, all-in (or f / c / b / r / a).
"raise 40" and "bet 20" work on one line. "raise" is the amount ON TOP of the
current bet. "c" checks if possible, otherwise calls. "p" shows probabilities
(Monte Carlo win/tie/lose estimate), "q" quits.