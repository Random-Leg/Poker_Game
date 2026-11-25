# Poker Game: Requirements Specification

## Overview

A text-based Texas Hold'em tournament written in Python (standard library
only, runs locally from the command line). One human plays against eight
computer-controlled players. The system deals cards, runs the betting,
manages blinds and pots, evaluates hands, eliminates players and declares a
tournament winner. On their turn the human can ask for an estimated
probability of winning the hand.

Requirements are numbered by group (for example 3.5 is the fifth betting
requirement) so that tests can say which requirement they check.

## 1. Cards and deck (`card.py`, `deck.py`)

- **1.1** A new deck must contain exactly 52 cards: every combination of 4 suits and 13 ranks exactly once, each with a unique ID from 0 to 51.
- **1.2** A card's ID, suit and rank must never change; a card ID outside 0 to 51 must be rejected.
- **1.3** Shuffling must only reorder the deck: the same 52 cards must be present afterwards, with none added, removed or duplicated.
- **1.4** Drawing must remove and return one card, reducing the deck size by one; a drawn card must not be drawn again in the same hand.

## 2. Hand flow and tournament progression (`game.py`, `main.py`)

- **2.1** A game must have exactly nine players with unique names (one human, eight bots); any other table must be rejected.
- **2.2** At the start of a hand, every player still in the tournament must receive exactly two hole cards, and no card may be dealt to two places.
- **2.3** A hand must move through pre-flop, flop (3 community cards), turn (4), river (5) and showdown in that order, without skipping a stage, unless all but one player fold.
- **2.4** If all but one player fold, the hand must end immediately and the remaining player must win the pot without a showdown.
- **2.5** When no further betting is possible (at most one player is not all-in), the remaining community cards must be dealt and the hand taken to showdown.
- **2.6** The dealer, small blind and big blind positions must move one seat clockwise between hands, skipping eliminated players.
- **2.7** With two players left (heads-up), the dealer must post the small blind and act first pre-flop; the big blind must act first after the flop.
- **2.8** A player with zero chips at the end of a hand must be eliminated: not dealt in and not asked to act in later hands.
- **2.9** The game must continue while more than one player has chips and must end when one player holds all the chips; that player is declared the winner.
- **2.10** A complete tournament played by bots alone from a fixed seed must finish with a single winner and without an unhandled error.

## 3. Betting and blinds (`betting.py`, `game.py`)

- **3.1** The legal actions offered to a player (fold, check, call, bet, raise, all-in) must depend on the betting state: check only when nothing is owed; call only when something is owed and affordable; bet only when there is no bet; raise only when there is a bet.
- **3.2** A player must never put in more chips than they hold.
- **3.3** A folded player and an all-in player must not be able to take any further betting action in the hand.
- **3.4** The amount to call must equal the current highest bet minus the player's contribution in this betting round, and never be negative.
- **3.5** An opening bet below the big blind, or a raise below the minimum raise (the size of the last full bet or raise), must be rejected unless it puts the player all-in.
- **3.6** An all-in for less than a full raise must not lower the current bet and must not change the minimum raise.
- **3.7** A betting round must end only when every player still in the hand has folded, is all-in, or has matched the current bet after having had a chance to act.
- **3.8** An illegal action must be rejected with an error and must leave chips, pot, bets and turn order exactly as they were.
- **3.9** Every hand must start with a small blind and a big blind posted by the correct seats; a player who cannot cover a blind posts what they have and is all-in.
- **3.10** Blind levels and the number of hands per level must be configurable; the blinds must rise to the next level after that number of hands and stay at the last level once it is reached.

## 4. Pots and payout (`pot.py`, `game.py`)

- **4.1** The pot total must always equal the sum of all players' contributions in the hand; a folded player's contribution stays in the pot.
- **4.2** When players are all-in for different amounts, the pot must be split into a main pot and side pots so that each player can only win the part they matched.
- **4.3** Chips that no other player could match (for example an uncalled bet) must be returned to the player who put them in.
- **4.4** At showdown each pot must go to the best hand among the players eligible for that pot.
- **4.5** Players with identical best hands must split the pot equally; chips that cannot be divided go one at a time to the winners nearest the dealer's left.
- **4.6** Chips must be conserved: at the end of every hand, the chips held by all players must total the same as at the start of the tournament (9,000 by default).

## 5. Hand evaluation (`evaluator.py`)

- **5.1** The evaluator must recognise all ten hand categories and rank them: royal flush, straight flush, four of a kind, full house, flush, straight, three of a kind, two pair, one pair, high card.
- **5.2** From five, six or seven cards, the evaluator must return the best possible five-card hand, using zero, one or two of the hole cards.
- **5.3** Hands in the same category must be ordered correctly by the ranks that make the hand and then by kickers; hands that are equal on all five cards must tie.
- **5.4** The ace must count high in general and low in an A-2-3-4-5 straight, which is the lowest straight.
- **5.5** The fast evaluator (`evaluate`) must give the same result as the reference evaluator (`evaluate_bruteforce`) for every set of five to seven distinct cards.

## 6. Bots (`bot.py`, `game.py`)

- **6.1** A bot must only ever return an action that is legal in the current state, with an amount within its chips and within the legal bet or raise range.
- **6.2** A bot must decide using only its own hole cards and public information (community cards, pot, bets, chip counts); it must never be given another player's hole cards.
- **6.3** A bot must not fold when it can check for free.
- **6.4** An unknown strategy name, or an empty list of legal actions, must be rejected with an error.
- **6.5** The three strategies (passive, balanced, aggressive) must behave measurably differently: over 2,000 identical decision situations, the share of bets and raises must be highest for aggressive, then balanced, then passive.
- **6.6** Bot settings must be changeable in `STRATEGY_SETTINGS` without editing the game engine.

## 7. Probability estimate (`probability.py`, `game.py`)

- **7.1** The estimate must return win, tie and loss probabilities, each between 0 and 1, that sum to 1 (within 0.000001).
- **7.2** Simulated cards must never repeat a card that is already known (the player's hole cards and the visible community cards) or another simulated card.
- **7.3** The estimate must use the same hand evaluator as the showdown, and the number of opponents still in the hand.
- **7.4** Invalid input must be rejected with an error: not exactly two hole cards, more than five community cards, duplicate known cards, fewer than one opponent, zero or negative simulations, or more opponents than the remaining cards allow.
- **7.5** Accuracy: with 10,000 simulations, the estimated win probability must be within 2 percentage points of the exact value for heads-up reference hands whose exact odds are known.
- **7.6** Speed: an estimate of 2,000 simulations against eight opponents (the in-game setting) must finish within 1 second, and 10,000 simulations within 5 seconds.
- **7.7** Asking for the estimate must not use up the player's turn or change the game state.
- **7.8** The assumptions of the estimate (opponents hold random cards, nobody folds) must be documented for the user.

## 8. Robustness and state integrity (`player.py`, `game.py`, `main.py`)

- **8.1** Invalid input from the human (unknown command, non-numeric, negative or too-large amount, illegal action) must produce a clear message and a new prompt, never a crash or a change of state.
- **8.2** Quitting (`q`, Ctrl-C or end of input) must end the game cleanly and print the final standings.
- **8.3** State invariants must hold after every action: no chip balance is negative; no player has more than two hole cards; there are at most five community cards; no card appears in two places; a folded or eliminated player is never the player to act.
- **8.4** An operation attempted in the wrong game state (for example acting outside a betting round, or completing a hand before showdown) must raise an error and not change the state.
- **8.5** Reproducibility: two games started with the same `--seed` and given the same inputs must produce identical deals, actions and results.
- **8.6** The display must show the human their hole cards, the community cards, chip counts, pot, blinds, amount to call, minimum raise and legal actions, and must not show a bot's hole cards before showdown.
- **8.7** Game output must be clear enough for a player to follow each hand's events and result.
- **8.8** Game logic must stay separated by responsibility (cards, betting, pot, evaluation, bots, probability, engine, interface) so that each part can be tested on its own.

## Out of scope

Graphical interface, network play, saving and loading games, cash-game mode,
opponent modelling and hand-history replay are not required and are not
tested.
