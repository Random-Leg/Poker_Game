from enum import Enum


class BettingRound:
    def __init__(self):
        self.current_bet = 0
        self.minimum_raise = 0

        # Smallest opening bet (the big blind in a real game).
        self.minimum_bet = 1

        # Total pot contribution at the beginning of this betting round.
        # This lets us calculate contribution for the current street only.
        self.starting_contributions = {}

    @property
    def min_raise_amount(self):
        """Smallest legal raise-by amount right now."""
        return max(self.minimum_raise, self.minimum_bet)

    def start_new_round(self, pot):
        self.starting_contributions = {
            player: pot.get_contribution(player)
            for player in pot.contributions
        }

    def get_contribution(self, player, pot):
        starting = self.starting_contributions.get(player, 0)
        return pot.get_contribution(player) - starting

    def can_check(self, player, pot):
        if player.folded:
            return False

        if player.all_in:
            return False

        contribution = self.get_contribution(player, pot)

        return contribution == self.current_bet

    def can_call(self, player, pot):
        if player.folded:
            return False

        if player.all_in:
            return False

        contribution = self.get_contribution(player, pot)

        if self.current_bet <= contribution:
            return False

        call_amount = self.current_bet - contribution

        return call_amount <= player.chips

    def can_bet(self, player, pot):
        if player.folded:
            return False

        if player.all_in:
            return False

        if self.current_bet != 0:
            return False

        return player.chips > 0

    def can_raise(self, player, pot, raise_amount):
        if player.folded:
            return False

        if player.all_in:
            return False

        if self.current_bet == 0:
            return False

        if raise_amount < self.min_raise_amount:
            return False

        new_bet = self.current_bet + raise_amount

        current_contribution = self.get_contribution(player, pot)

        additional_amount = new_bet - current_contribution

        return additional_amount <= player.chips

    def get_amount_to_call(self, player, pot):
        """Chips the player must add to match the current bet."""
        return max(
            0,
            self.current_bet - self.get_contribution(player, pot)
        )

    def get_max_raise(self, player, pot):
        """Largest legal raise-by amount (capped by the player's chips)."""
        contribution = self.get_contribution(player, pot)
        return player.chips + contribution - self.current_bet

    def can_all_in(self, player):
        if player.folded:
            return False

        if player.all_in:
            return False

        return player.chips > 0

    def check(self, player, pot):
        if not self.can_check(player, pot):
            raise ValueError("Player cannot check")

    def fold(self, player):
        if player.folded:
            raise ValueError("Player has already folded")

        player.fold()

    def bet(self, player, pot, amount):
        if not self.can_bet(player, pot):
            raise ValueError("Player cannot bet")

        if amount <= 0:
            raise ValueError("Bet must be greater than zero")

        if amount > player.chips:
            raise ValueError("Player does not have enough chips")

        if amount < self.minimum_bet and amount != player.chips:
            raise ValueError(
                f"Bet must be at least {self.minimum_bet}"
            )

        pot.add_bet(player, amount)

        self.current_bet = amount
        self.minimum_raise = max(self.minimum_raise, amount, self.minimum_bet)

    def call(self, player, pot):
        if not self.can_call(player, pot):
            raise ValueError("Player cannot call")

        current_contribution = self.get_contribution(player, pot)

        call_amount = self.current_bet - current_contribution

        pot.add_bet(player, call_amount)

    def raise_bet(self, player, pot, raise_amount):
        if not self.can_raise(player, pot, raise_amount):
            raise ValueError("Player cannot raise")

        new_bet = self.current_bet + raise_amount

        current_contribution = self.get_contribution(player, pot)

        additional_amount = new_bet - current_contribution

        pot.add_bet(player, additional_amount)

        self.current_bet = new_bet
        self.minimum_raise = raise_amount

    def all_in(self, player, pot):
        if not self.can_all_in(player):
            raise ValueError("Player cannot go all-in")

        amount = player.chips

        pot.add_bet(player, amount)

        current_contribution = self.get_contribution(player, pot)

        if current_contribution > self.current_bet:
            increase = current_contribution - self.current_bet

            # Only a full raise changes the minimum raise size.
            if increase >= self.min_raise_amount:
                self.minimum_raise = increase

            self.current_bet = current_contribution

    def get_legal_actions(self, player, pot):
        actions = []

        if not player.folded and not player.all_in:
            if self.can_check(player, pot):
                actions.append(BettingAction.CHECK)

            if self.can_call(player, pot):
                actions.append(BettingAction.CALL)

            if self.can_bet(player, pot):
                actions.append(BettingAction.BET)

            if self.can_raise(player, pot, self.min_raise_amount):
                actions.append(BettingAction.RAISE)

            if self.can_all_in(player):
                actions.append(BettingAction.ALL_IN)

            actions.append(BettingAction.FOLD)

        return actions


class BettingAction(Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all-in"
