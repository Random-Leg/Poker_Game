class Pot:
    def __init__(self):
        self.amount = 0
        self.contributions = {}

    def add_bet(self, player, amount):
        if player.folded:
            raise ValueError("Player has folded and cannot bet")

        if amount <= 0:
            raise ValueError("Bet must be greater than zero")

        if amount > player.chips:
            raise ValueError("Player does not have enough chips")

        player.bet(amount)

        self.amount += amount

        if player not in self.contributions:
            self.contributions[player] = 0

        self.contributions[player] += amount

    def get_contribution(self, player):
        return self.contributions.get(player, 0)

    def award(self, player):
        player.chips += self.amount
        self.reset()

    def reset(self):
        self.amount = 0
        self.contributions.clear()

    def add_all_in(self, player):
        if player.folded:
            raise ValueError("A folded player cannot bet")
        if player.all_in:
            raise ValueError("Player is already all-in")
        if player.chips <= 0:
            raise ValueError("Player has no chips")
        amount = player.chips
        player.bet(amount)
        self.amount += amount
        if player not in self.contributions:
            self.contributions[player] = 0
        self.contributions[player] += amount
        return amount

    def build_side_pots(self, eligible_players):
        """Split the pot into a main pot and side pots.

        ``eligible_players`` are the players still contesting the pot
        (everyone who has not folded). Every player's contribution - folded
        players included - is layered by the contribution levels of the
        eligible players, so a short all-in player can only win the part
        of the pot they were able to match.

        Returns ``(pots, refunds)``:
          * pots    - list of ``(amount, [eligible players])`` from the
                      main pot outwards.
          * refunds - ``{player: amount}`` of chips nobody could contest
                      (e.g. an uncalled bet) which go back to their owner.

        Chips in ``self.amount`` that have no recorded contribution (it is
        possible to set the pot directly) are added to the main pot.
        """
        eligible = list(eligible_players)
        contributions = {
            player: amount
            for player, amount in self.contributions.items()
            if amount > 0
        }

        levels = sorted({
            contributions[player]
            for player in eligible
            if player in contributions
        })

        pots = []
        refunds = {}
        previous_level = 0

        for level in levels:
            layer_total = 0
            for amount in contributions.values():
                layer_total += (
                    min(amount, level) - min(amount, previous_level)
                )

            layer_players = [
                player for player in eligible
                if contributions.get(player, 0) >= level
            ]

            if layer_total > 0:
                pots.append((layer_total, layer_players))

            previous_level = level

        # Anything contributed above the highest eligible level cannot be
        # won by anybody - hand it back to whoever put it in.
        for player, amount in contributions.items():
            excess = amount - previous_level
            if excess > 0:
                refunds[player] = refunds.get(player, 0) + excess

        unattributed = self.amount - sum(contributions.values())
        if unattributed > 0:
            if pots:
                first_amount, first_players = pots[0]
                pots[0] = (first_amount + unattributed, first_players)
            elif eligible:
                pots.append((unattributed, eligible))

        return pots, refunds
