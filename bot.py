import math
import random
from betting import BettingAction
from evaluator import HandRank
from card import Rank
from probability import monte_carlo_equity


# Tuning knobs for each playing style.
#   play        - minimum pre-flop hand score (Chen formula) to enter a pot
#   raise_score - pre-flop hand score at which the bot raises
#   aggression  - how often a strong hand is bet/raised rather than slow-played
#   bluff       - chance of betting/raising with a weak hand
#   call_margin - multiplier on the pot odds the bot needs to call
#                 (below 1 means it calls more loosely)
STRATEGY_SETTINGS = {
    "passive": {
        "play": 7.0,
        "raise_score": 11.5,
        "aggression": 0.35,
        "bluff": 0.0,
        "call_margin": 1.15,
    },
    "balanced": {
        "play": 5.5,
        "raise_score": 9.5,
        "aggression": 0.6,
        "bluff": 0.04,
        "call_margin": 1.0,
    },
    "aggressive": {
        "play": 4.0,
        "raise_score": 7.5,
        "aggression": 0.9,
        "bluff": 0.10,
        "call_margin": 0.85,
    },
}


def pre_flop_score(hole_cards):
    """Score a starting hand with the Chen formula.

    Roughly: AA = 20, KK = 16, AKs = 12, 77 = 7, T9s = 6, 72o < 0.
    """
    if len(hole_cards) != 2:
        raise ValueError("Exactly 2 hole cards are required")

    first, second = hole_cards
    high, low = sorted(
        (first.rank.value, second.rank.value),
        reverse=True
    )

    def card_points(value):
        if value == 14:
            return 10.0
        if value == 13:
            return 8.0
        if value == 12:
            return 7.0
        if value == 11:
            return 6.0
        return value / 2

    score = card_points(high)

    if high == low:
        return float(max(5, math.ceil(score * 2)))

    if first.suit == second.suit:
        score += 2

    gap = high - low - 1

    if gap == 1:
        score -= 1
    elif gap == 2:
        score -= 2
    elif gap == 3:
        score -= 4
    elif gap >= 4:
        score -= 5

    if gap <= 1 and high < 12:
        score += 1

    return float(math.ceil(score))


class Bot:
    def __init__(self, strategy="balanced"):
        if strategy not in (
            "passive",
            "aggressive",
            "balanced"
        ):
            raise ValueError("Invalid bot strategy")

        self.strategy = strategy

    def choose_action(
        self,
        legal_actions,
        probabilities=None
    ):
        if not legal_actions:
            raise ValueError("No legal actions available")

        if probabilities is None:
            return self.choose_basic_action(
                legal_actions
            )

        if BettingAction.RAISE in legal_actions:
            raise_probability = self.get_raise_probability(
                probabilities
            )

            if random.random() < raise_probability:
                return BettingAction.RAISE

        if BettingAction.BET in legal_actions:
            bet_probability = self.get_bet_probability(
                probabilities
            )

            if random.random() < bet_probability:
                return BettingAction.BET

        if BettingAction.CALL in legal_actions:
            return BettingAction.CALL

        if BettingAction.CHECK in legal_actions:
            return BettingAction.CHECK

        if BettingAction.ALL_IN in legal_actions:
            return BettingAction.ALL_IN

        return BettingAction.FOLD

    def choose_basic_action(self, legal_actions):
        if BettingAction.CHECK in legal_actions:
            return BettingAction.CHECK

        if BettingAction.CALL in legal_actions:
            return BettingAction.CALL

        if BettingAction.FOLD in legal_actions:
            return BettingAction.FOLD

        return legal_actions[0]

    def choose_pre_flop_action(
        self,
        legal_actions,
        player
    ):
        if not legal_actions:
            raise ValueError(
                "No legal actions available"
            )

        raise_probability = (
            self.get_pre_flop_raise_probability(
                player
            )
        )

        if (
            BettingAction.RAISE in legal_actions
            and random.random() < raise_probability
        ):
            return BettingAction.RAISE

        if (
            BettingAction.BET in legal_actions
            and random.random() < raise_probability
        ):
            return BettingAction.BET

        if BettingAction.CALL in legal_actions:
            return BettingAction.CALL

        if BettingAction.CHECK in legal_actions:
            return BettingAction.CHECK

        if BettingAction.FOLD in legal_actions:
            return BettingAction.FOLD

        return legal_actions[0]

    def get_pre_flop_raise_probability(
        self,
        player
    ):
        if len(player.hand) != 2:
            return 0.0

        card_one = player.hand[0]
        card_two = player.hand[1]

        rank_one = card_one.rank
        rank_two = card_two.rank

        # Pocket pairs
        if rank_one == rank_two:

            if rank_one in (
                Rank.ACE,
                Rank.KING,
                Rank.QUEEN
            ):
                base_probability = 0.80

            elif rank_one in (
                Rank.JACK,
                Rank.TEN,
                Rank.NINE
            ):
                base_probability = 0.60

            elif rank_one in (
                Rank.EIGHT,
                Rank.SEVEN,
                Rank.SIX
            ):
                base_probability = 0.40

            else:
                base_probability = 0.20

        else:
            ranks = {rank_one, rank_two}

            # Premium unpaired hands
            if (
                Rank.ACE in ranks
                and (
                    Rank.KING in ranks
                    or Rank.QUEEN in ranks
                )
            ):
                base_probability = 0.35

            elif (
                Rank.ACE in ranks
                and Rank.JACK in ranks
            ):
                base_probability = 0.30

            elif (
                Rank.KING in ranks
                and Rank.QUEEN in ranks
            ):
                base_probability = 0.25

            # Strong unpaired hands
            elif (
                Rank.ACE in ranks
                or (
                    Rank.KING in ranks
                    and Rank.JACK in ranks
                )
                or (
                    Rank.QUEEN in ranks
                    and Rank.JACK in ranks
                )
            ):
                base_probability = 0.20

            else:
                base_probability = 0.05

        if self.strategy == "aggressive":
            multiplier = 1.0

        elif self.strategy == "balanced":
            multiplier = 0.5

        else:
            multiplier = 0.25

        return base_probability * multiplier

    def get_raise_probability(
        self,
        probabilities
    ):
        strength_score = self.get_strength_score(
            probabilities
        )

        base_probability = 0.10

        if self.strategy == "aggressive":
            multiplier = 1.0

        elif self.strategy == "balanced":
            multiplier = 0.5

        else:
            multiplier = 0.25

        return min(
            strength_score
            * base_probability
            * multiplier,
            0.75
        )

    def get_bet_probability(
        self,
        probabilities
    ):
        strength_score = self.get_strength_score(
            probabilities
        )

        base_probability = 0.15

        if self.strategy == "aggressive":
            multiplier = 1.0

        elif self.strategy == "balanced":
            multiplier = 0.6

        else:
            multiplier = 0.3

        return min(
            strength_score
            * base_probability
            * multiplier,
            0.75
        )

    def get_strength_score(
        self,
        probabilities
    ):
        hand_weights = {
            HandRank.ONE_PAIR: 1.0,
            HandRank.TWO_PAIR: 1.5,
            HandRank.THREE_OF_A_KIND: 2.0,
            HandRank.STRAIGHT: 2.5,
            HandRank.FLUSH: 3.0,
            HandRank.FULL_HOUSE: 3.5,
            HandRank.FOUR_OF_A_KIND: 4.0,
            HandRank.STRAIGHT_FLUSH: 5.0,
            HandRank.ROYAL_FLUSH: 6.0,
        }

        score = 0.0

        for hand_rank, probability in probabilities.items():
            weight = hand_weights.get(
                hand_rank,
                0.0
            )

            score += probability * weight

        return score

    # ------------------------------------------------------------------
    # Decision making used by the game
    # ------------------------------------------------------------------

    def decide(self, legal_actions, situation, equity=None):
        """Choose an action and amount for the current game situation.

        ``situation`` is the dictionary built by
        ``PokerGame.get_bot_situation`` - the bot's own hole cards plus
        public information only. Returns ``(action, amount)`` where
        ``amount`` is None unless the action is a bet or a raise.

        ``equity`` (a win probability between 0 and 1) can be supplied to
        skip the Monte Carlo estimate, e.g. for testing.
        """
        if not legal_actions:
            raise ValueError("No legal actions available")

        if len(situation["community_cards"]) == 0:
            action, amount = self._decide_pre_flop(
                legal_actions, situation
            )
        else:
            action, amount = self._decide_post_flop(
                legal_actions, situation, equity
            )

        return self._make_legal(action, amount, legal_actions)

    def _settings(self):
        return STRATEGY_SETTINGS[self.strategy]

    def _make_legal(self, action, amount, legal_actions):
        if action in legal_actions:
            return action, amount

        for fallback in (
            BettingAction.CHECK,
            BettingAction.CALL,
            BettingAction.FOLD,
        ):
            if fallback in legal_actions:
                return fallback, None

        return legal_actions[0], None

    def _raise_size(self, situation, fraction_low, fraction_high):
        """Pick a legal raise-by amount around a fraction of the pot."""
        pot_after_call = situation["pot"] + situation["to_call"]
        wanted = int(
            pot_after_call * random.uniform(fraction_low, fraction_high)
        )

        return max(
            situation["min_raise"],
            min(wanted, situation["max_raise"])
        )

    def _bet_size(self, situation, fraction_low, fraction_high):
        wanted = int(
            situation["pot"] * random.uniform(fraction_low, fraction_high)
        )

        return max(
            situation["min_bet"],
            min(wanted, situation["chips"])
        )

    def _aggressive_action(self, legal_actions, situation, low, high):
        """Bet or raise with a sensible size, shoving when stacks are short."""
        chips = situation["chips"]

        if BettingAction.RAISE in legal_actions:
            amount = self._raise_size(situation, low, high)
            commits = situation["to_call"] + amount

            if commits >= chips * 0.6 and BettingAction.ALL_IN in legal_actions:
                return BettingAction.ALL_IN, None

            return BettingAction.RAISE, amount

        if BettingAction.BET in legal_actions:
            amount = self._bet_size(situation, low, high)

            if amount >= chips * 0.6 and BettingAction.ALL_IN in legal_actions:
                return BettingAction.ALL_IN, None

            return BettingAction.BET, amount

        return None

    def _decide_pre_flop(self, legal_actions, situation):
        settings = self._settings()
        score = pre_flop_score(situation["hole_cards"])

        big_blind = situation["big_blind"]
        to_call = situation["to_call"]
        chips = situation["chips"]

        # Facing a raise requires a stronger hand than opening does.
        raises_faced = max(0.0, to_call / big_blind - 1)
        penalty = min(7.0, raises_faced * 0.9)

        play_threshold = settings["play"] + penalty
        raise_threshold = settings["raise_score"] + penalty

        short_stacked = chips <= big_blind * 8

        # Short stacks either shove with a playable hand or give up.
        if short_stacked and BettingAction.ALL_IN in legal_actions:
            if score >= settings["play"] + 1 + penalty / 2:
                return BettingAction.ALL_IN, None

        wants_to_raise = (
            score >= raise_threshold
            and random.random() < settings["aggression"]
        ) or random.random() < settings["bluff"] * 0.5

        if wants_to_raise:
            choice = self._aggressive_action(
                legal_actions, situation, 0.6, 1.2
            )
            if choice is not None:
                return choice

        if BettingAction.CHECK in legal_actions:
            return BettingAction.CHECK, None

        if score >= play_threshold:
            if BettingAction.CALL in legal_actions:
                return BettingAction.CALL, None

            # Cannot cover the call: only commit the whole stack with
            # a genuinely strong hand.
            if (
                score >= settings["raise_score"] + 2
                and BettingAction.ALL_IN in legal_actions
            ):
                return BettingAction.ALL_IN, None

        return BettingAction.FOLD, None

    def _decide_post_flop(self, legal_actions, situation, equity):
        settings = self._settings()

        if equity is None:
            result = monte_carlo_equity(
                situation["hole_cards"],
                situation["community_cards"],
                max(1, situation["num_opponents"]),
                simulations=250
            )
            equity = result["win"] + result["tie"] / 2

        opponents = max(1, situation["num_opponents"])
        fair_share = 1 / (opponents + 1)

        # How strong a hand has to be, relative to a fair share of the
        # pot, before the bot starts betting for value.
        strong = fair_share + (1 - fair_share) * 0.30
        strong -= (settings["aggression"] - 0.6) * 0.10
        strong = min(0.85, max(fair_share + 0.05, strong))

        to_call = situation["to_call"]
        pot = situation["pot"]
        chips = situation["chips"]

        if to_call <= 0:
            if BettingAction.CHECK not in legal_actions:
                return BettingAction.CHECK, None

            value_bet = (
                equity >= strong
                and random.random() < settings["aggression"]
            )
            bluff = random.random() < settings["bluff"]

            if value_bet or bluff:
                choice = self._aggressive_action(
                    legal_actions, situation, 0.4, 0.9
                )
                if choice is not None:
                    return choice

            return BettingAction.CHECK, None

        # Facing a bet.
        pot_odds = to_call / (pot + to_call)
        needed = pot_odds * settings["call_margin"]

        # A call that commits the whole stack deserves extra caution.
        if to_call >= chips:
            needed += 0.05

        if (
            equity >= strong + 0.10
            and random.random() < settings["aggression"] * 0.6
        ):
            choice = self._aggressive_action(
                legal_actions, situation, 0.5, 1.0
            )
            if choice is not None:
                return choice

        if equity >= needed:
            if BettingAction.CALL in legal_actions:
                return BettingAction.CALL, None

            if BettingAction.ALL_IN in legal_actions:
                return BettingAction.ALL_IN, None

        if (
            random.random() < settings["bluff"] * 0.5
            and BettingAction.RAISE in legal_actions
        ):
            return BettingAction.RAISE, situation["min_raise"]

        return BettingAction.FOLD, None
