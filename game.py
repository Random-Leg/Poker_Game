from enum import Enum

from deck import Deck
from evaluator import evaluate, HandRank, describe_hand
from pot import Pot
from betting import BettingRound, BettingAction
from probability import probability_report, monte_carlo_equity


DEFAULT_BLIND_LEVELS = [
    (10, 20),
    (15, 30),
    (25, 50),
    (50, 100),
    (75, 150),
    (100, 200),
]


class GameState(Enum):
    NEW_HAND = "new_hand"
    PRE_FLOP = "pre_flop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"
    HAND_COMPLETE = "hand_complete"


BETTING_STATES = (
    GameState.PRE_FLOP,
    GameState.FLOP,
    GameState.TURN,
    GameState.RIVER,
)


class QuitGame(Exception):
    """Raised when the human asks to leave the game."""


class PokerGame:
    def __init__(
        self,
        players,
        human_name="You",
        blind_levels=None,
        hands_per_level=10
    ):
        if len(players) != 9:
            raise ValueError("A poker game must have exactly 9 players")

        if len(set(player.name for player in players)) != 9:
            raise ValueError("Players must have unique names")

        if blind_levels is None:
            blind_levels = DEFAULT_BLIND_LEVELS

        if not blind_levels:
            raise ValueError("At least one blind level is required")

        for small, big in blind_levels:
            if small <= 0 or big <= 0 or small > big:
                raise ValueError(
                    "Blinds must be positive and the small blind "
                    "cannot exceed the big blind"
                )

        if hands_per_level < 1:
            raise ValueError("hands_per_level must be at least 1")

        self.players = players
        self.human_name = human_name
        self.state = GameState.NEW_HAND
        self.current_player = None

        self.deck = Deck()
        self.community_cards = []

        self.dealer_position = 0

        self.blind_levels = list(blind_levels)
        self.hands_per_level = hands_per_level
        self.blind_level = 0
        self.small_blind, self.big_blind = self.blind_levels[0]
        self.hand_number = 0

        self.pot = Pot()
        self.betting_round = BettingRound()
        self.acted_players = set()

        # Filled in when a hand finishes (see complete_hand and
        # end_hand_by_fold) so a front-end can report what happened.
        self.last_result = None

    # ------------------------------------------------------------------
    # Players
    # ------------------------------------------------------------------

    def get_human_player(self):
        return next(
            (
                player
                for player in self.players
                if player.name == self.human_name
            ),
            None
        )

    def get_active_players(self):
        """Players who still have chips and are therefore still in the game."""
        return [
            player for player in self.players
            if player.chips > 0
        ]

    def _is_seated(self, player):
        # A player who is all-in has no chips left but is still playing
        # the current hand.
        return player.chips > 0 or player.all_in

    def get_players_who_can_act(self):
        return [
            player
            for player in self.get_active_players()
            if not player.folded and not player.all_in
        ]

    def get_players_remaining_in_hand(self):
        """Players still contesting the pot (not folded, not eliminated)."""
        return [
            player
            for player in self.players
            if not player.folded and self._is_seated(player)
        ]

    def get_remaining_player(self):
        players = self.get_players_remaining_in_hand()

        if len(players) != 1:
            raise ValueError(
                "There is not exactly one remaining player"
            )

        return players[0]

    def is_game_over(self):
        return len(self.get_active_players()) <= 1

    # ------------------------------------------------------------------
    # Hand set-up
    # ------------------------------------------------------------------

    def start_hand(self):
        if self.state != GameState.NEW_HAND:
            raise ValueError("A new hand can only be started from NEW_HAND")
        if len(self.get_active_players()) < 2:
            raise ValueError(
                "At least 2 active players are required to start a hand"
            )

        self.hand_number += 1
        self.last_result = None

        self.deck = Deck()
        self.deck.shuffle()
        self.pot = Pot()
        self.betting_round = BettingRound()
        self.betting_round.minimum_bet = self.big_blind
        self.acted_players = set()
        self.community_cards.clear()

        for player in self.players:
            player.clear_hand()
            player.folded = False
            player.all_in = False

        self.deal_hole_cards()
        self.post_blinds()
        self.state = GameState.PRE_FLOP
        self.start_pre_flop_betting()

    def deal_hole_cards(self):
        active_players = self.get_active_players()
        for _ in range(2):
            for player in active_players:
                player.add_card(self.deck.draw())

    def move_dealer(self):
        if len(self.get_active_players()) < 2:
            raise ValueError("At least 2 active players are required")
        for offset in range(1, len(self.players) + 1):
            position = (self.dealer_position + offset) % len(self.players)
            if self.players[position].chips > 0:
                self.dealer_position = position
                return
        raise ValueError("No active players found")

    def get_dealer(self):
        return self.players[self.dealer_position]

    def get_next_active_player(self, position):
        for offset in range(1, len(self.players) + 1):
            next_position = (
                position + offset
            ) % len(self.players)

            if self._is_seated(self.players[next_position]):
                return self.players[next_position]

        raise ValueError("No active players found")

    def get_small_blind(self):
        seated = [
            player for player in self.players
            if self._is_seated(player)
        ]
        dealer = self.get_dealer()

        # Heads-up the dealer posts the small blind.
        if len(seated) == 2 and dealer in seated:
            return dealer

        return self.get_next_active_player(self.dealer_position)

    def get_big_blind(self):
        small_blind_player = self.get_small_blind()
        small_blind_position = self.players.index(small_blind_player)
        return self.get_next_active_player(small_blind_position)

    def get_blind_amounts(self):
        return self.small_blind, self.big_blind

    def get_blind_level(self):
        """Current blind level, starting from 1."""
        return self.blind_level + 1

    def _post_blind(self, player, amount):
        if player.chips <= amount:
            self.pot.add_all_in(player)
        else:
            self.pot.add_bet(player, amount)

    def post_blinds(self):
        if len(self.get_active_players()) < 2:
            raise ValueError("At least 2 active players are required")

        small_blind_player = self.get_small_blind()
        big_blind_player = self.get_big_blind()

        self._post_blind(small_blind_player, self.small_blind)
        self._post_blind(big_blind_player, self.big_blind)

        self.betting_round.current_bet = max(
            self.pot.get_contribution(small_blind_player),
            self.pot.get_contribution(big_blind_player),
        )

        self.betting_round.minimum_raise = self.big_blind

    def get_first_to_act_pre_flop(self):
        big_blind = self.get_big_blind()
        big_blind_position = self.players.index(big_blind)

        return self.get_next_player_after(big_blind_position)

    def set_first_player_pre_flop(self):
        self.current_player = self.get_first_to_act_pre_flop()

    def start_pre_flop_betting(self):
        """Hand the action to the first player, or run the board out.

        If the blinds left nobody with a decision to make (everyone is
        all-in, or the only player with chips has already matched the
        bet) there is no betting and the hand goes straight to showdown.
        """
        can_act = self.get_players_who_can_act()

        owes_chips = [
            player for player in can_act
            if self.betting_round.get_contribution(player, self.pot)
            < self.betting_round.current_bet
        ]

        if len(can_act) >= 2 or owes_chips:
            self.set_first_player_pre_flop()
        else:
            self.advance_after_betting_round()

    # ------------------------------------------------------------------
    # Streets
    # ------------------------------------------------------------------

    def move_to_flop(self):
        if self.state != GameState.PRE_FLOP:
            raise ValueError("Cannot move to flop from current state")
        self.deck.draw()  # burn card
        for _ in range(3):
            self.community_cards.append(self.deck.draw())
        self.state = GameState.FLOP

    def move_to_turn(self):
        if self.state != GameState.FLOP:
            raise ValueError("Cannot move to turn from current state")
        self.deck.draw()  # burn card
        self.community_cards.append(self.deck.draw())
        self.state = GameState.TURN

    def move_to_river(self):
        if self.state != GameState.TURN:
            raise ValueError("Cannot move to river from current state")
        self.deck.draw()  # burn card
        self.community_cards.append(self.deck.draw())
        self.state = GameState.RIVER

    def move_to_showdown(self):
        if self.state != GameState.RIVER:
            raise ValueError("Cannot move to showdown from current state")

        self.state = GameState.SHOWDOWN

    def advance_state(self):
        if self.state == GameState.NEW_HAND:
            self.start_hand()

        elif self.state == GameState.PRE_FLOP:
            self.move_to_flop()

        elif self.state == GameState.FLOP:
            self.move_to_turn()

        elif self.state == GameState.TURN:
            self.move_to_river()

        elif self.state == GameState.RIVER:
            self.move_to_showdown()

        elif self.state == GameState.SHOWDOWN:
            self.complete_hand()

        else:
            raise ValueError("Hand is already complete")

    def get_next_player_after(self, position):
        for offset in range(1, len(self.players) + 1):
            next_position = (
                position + offset
            ) % len(self.players)

            player = self.players[next_position]

            if (
                player.chips > 0
                and not player.folded
                and not player.all_in
            ):
                return player

        raise ValueError("No player available to act")

    def get_next_player(self):
        current_position = self.players.index(self.current_player)
        return self.get_next_player_after(current_position)

    def get_first_to_act_post_flop(self):
        dealer_position = self.dealer_position
        return self.get_next_player_after(dealer_position)

    def start_new_betting_round(self):
        self.betting_round = BettingRound()
        self.betting_round.minimum_bet = self.big_blind
        self.betting_round.start_new_round(self.pot)
        self.acted_players = set()
        self.current_player = self.get_first_to_act_post_flop()

    def advance_after_betting_round(self):
        if self.state == GameState.PRE_FLOP:
            self.move_to_flop()
        elif self.state == GameState.FLOP:
            self.move_to_turn()
        elif self.state == GameState.TURN:
            self.move_to_river()
        elif self.state == GameState.RIVER:
            self.move_to_showdown()
        else:
            raise ValueError(
                "Cannot advance after betting round from current state"
            )

        if self.state == GameState.SHOWDOWN:
            return

        # With fewer than two players able to bet there is nobody to bet
        # against, so the remaining cards are simply dealt out.
        if len(self.get_players_who_can_act()) < 2:
            self.advance_after_betting_round()
        else:
            self.start_new_betting_round()

    # ------------------------------------------------------------------
    # Betting
    # ------------------------------------------------------------------

    def perform_action(self, action, amount=None):
        if self.state not in BETTING_STATES:
            raise ValueError("No betting is possible in the current state")

        player = self.current_player

        if player is None or player.folded or player.all_in:
            raise ValueError("The current player cannot act")

        previous_bet = self.betting_round.current_bet

        if action == BettingAction.FOLD:
            self.betting_round.fold(player)

        elif action == BettingAction.CHECK:
            self.betting_round.check(player, self.pot)

        elif action == BettingAction.CALL:
            self.betting_round.call(player, self.pot)

        elif action == BettingAction.BET:
            if amount is None:
                raise ValueError("Bet amount is required")

            self.betting_round.bet(
                player,
                self.pot,
                amount
            )

        elif action == BettingAction.RAISE:
            if amount is None:
                raise ValueError("Raise amount is required")

            self.betting_round.raise_bet(
                player,
                self.pot,
                amount
            )

        elif action == BettingAction.ALL_IN:
            self.betting_round.all_in(
                player,
                self.pot
            )

        else:
            raise ValueError("Unknown betting action")

        # Any increase of the bet re-opens the action for everyone else.
        if self.betting_round.current_bet > previous_bet:
            self.acted_players = {player}
        else:
            self.acted_players.add(player)

        remaining_players = self.get_players_remaining_in_hand()
        if len(remaining_players) == 1:
            self.end_hand_by_fold()
        elif self.is_betting_round_complete():
            self.advance_after_betting_round()
        else:
            self.current_player = self.get_next_player()

    def is_betting_round_complete(self):
        if self.state == GameState.HAND_COMPLETE:
            return True

        players_who_can_act = self.get_players_who_can_act()

        if not players_who_can_act:
            return True

        if len(players_who_can_act) == 1:
            # Everybody else is all-in (or folded). The last player still
            # has to answer any bet they have not matched yet, but there
            # is nobody left to bet against once they have.
            only_player = players_who_can_act[0]
            return (
                self.betting_round.get_contribution(only_player, self.pot)
                >= self.betting_round.current_bet
            )

        for player in players_who_can_act:
            if player not in self.acted_players:
                return False

            if (
                self.betting_round.get_contribution(player, self.pot)
                != self.betting_round.current_bet
            ):
                return False

        return True

    # ------------------------------------------------------------------
    # Hand completion
    # ------------------------------------------------------------------

    def end_hand_by_fold(self):
        winner = self.get_remaining_player()
        amount = self.pot.amount

        self.pot.award(winner)

        self.last_result = {
            "showdown": False,
            "hands": {},
            "pots": [
                {
                    "amount": amount,
                    "winners": [winner],
                    "hand": None,
                    "label": "Pot",
                }
            ],
            "refunds": {},
        }

        self.state = GameState.HAND_COMPLETE

        return winner

    def determine_winners(self):
        """Players holding the best hand among those still in the hand."""
        players = self.get_players_remaining_in_hand()

        if not players:
            raise ValueError("No players remain in the hand")

        if len(self.community_cards) != 5:
            raise ValueError(
                "There must be 5 community cards for showdown"
            )

        results = {}

        for player in players:
            cards = player.hand + self.community_cards
            results[player] = evaluate(cards)

        best_hand = max(results.values())

        winners = [
            player
            for player, hand in results.items()
            if hand == best_hand
        ]

        return winners

    def _order_from_dealer(self, players):
        """Order players clockwise starting left of the dealer."""
        count = len(self.players)

        return sorted(
            players,
            key=lambda player: (
                self.players.index(player) - self.dealer_position - 1
            ) % count
        )

    def complete_hand(self):
        if self.state != GameState.SHOWDOWN:
            raise ValueError("Can only complete a hand from showdown")

        contenders = self.get_players_remaining_in_hand()

        if not contenders:
            raise ValueError("No players remain in the hand")

        if len(self.community_cards) != 5:
            raise ValueError(
                "There must be 5 community cards for showdown"
            )

        hands = {
            player: evaluate(player.hand + self.community_cards)
            for player in contenders
        }

        pots, refunds = self.pot.build_side_pots(contenders)

        pot_results = []
        all_winners = set()

        for index, (amount, eligible) in enumerate(pots):
            best_hand = max(hands[player] for player in eligible)

            winners = [
                player for player in eligible
                if hands[player] == best_hand
            ]

            share = amount // len(winners)
            remainder = amount % len(winners)

            # Indivisible chips go one at a time to the winners closest
            # to the left of the dealer.
            for position, winner in enumerate(
                self._order_from_dealer(winners)
            ):
                winner.chips += share + (1 if position < remainder else 0)

            all_winners.update(winners)

            pot_results.append({
                "amount": amount,
                "winners": [
                    player for player in self.players
                    if player in winners
                ],
                "hand": best_hand,
                "label": "Main pot" if index == 0 else f"Side pot {index}",
            })

        for player, amount in refunds.items():
            player.chips += amount

        if len(pot_results) == 1:
            pot_results[0]["label"] = "Pot"

        self.last_result = {
            "showdown": True,
            "hands": hands,
            "pots": pot_results,
            "refunds": refunds,
        }

        self.pot.reset()
        self.state = GameState.HAND_COMPLETE

        return [
            player for player in self.players
            if player in all_winners
        ]

    def _maybe_increase_blinds(self):
        target_level = min(
            self.hand_number // self.hands_per_level,
            len(self.blind_levels) - 1
        )

        if target_level > self.blind_level:
            self.blind_level = target_level
            self.small_blind, self.big_blind = self.blind_levels[
                target_level
            ]
            return True

        return False

    def reset_hand(self):
        if self.state != GameState.HAND_COMPLETE:
            raise ValueError("Can only reset a completed hand")

        self.community_cards.clear()
        self.acted_players = set()

        for player in self.players:
            player.clear_hand()
            player.folded = False
            player.all_in = False

        self._maybe_increase_blinds()
        self.move_dealer()

        self.state = GameState.NEW_HAND

    # ------------------------------------------------------------------
    # Bots
    # ------------------------------------------------------------------

    def get_bot_situation(self, player):
        """Everything a bot is allowed to know when it makes a decision.

        This deliberately contains only the bot's own hole cards and
        public information - never anybody else's cards.
        """
        betting_round = self.betting_round

        opponents = [
            other for other in self.get_players_remaining_in_hand()
            if other is not player
        ]

        return {
            "state": self.state,
            "hole_cards": list(player.hand),
            "community_cards": list(self.community_cards),
            "num_opponents": len(opponents),
            "pot": self.pot.amount,
            "to_call": betting_round.get_amount_to_call(player, self.pot),
            "current_bet": betting_round.current_bet,
            "min_raise": betting_round.min_raise_amount,
            "max_raise": betting_round.get_max_raise(player, self.pot),
            "min_bet": betting_round.minimum_bet,
            "chips": player.chips,
            "big_blind": self.big_blind,
        }

    def get_bot_probability_report(self, player):
        if self.state not in (
            GameState.FLOP,
            GameState.TURN,
            GameState.RIVER,
        ):
            return None

        known_cards = (
            player.hand
            + self.community_cards
        )

        return probability_report(known_cards)

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    @staticmethod
    def format_cards(cards):
        return "  ".join(card.short() for card in cards) if cards else "-"

    def display_game_state(self):
        print("\n" + "=" * 44)
        print(f"State: {self.state.value}")
        print(
            f"Blinds: {self.small_blind}/{self.big_blind} "
            f"(level {self.get_blind_level()}), "
            f"hand #{self.hand_number}"
        )
        print(f"Pot: {self.pot.amount}")
        print(f"Current bet: {self.betting_round.current_bet}")

        print("\nCommunity cards:")
        if self.community_cards:
            print(f"  {self.format_cards(self.community_cards)}")
        else:
            print("  None")

        in_hand = self.state in BETTING_STATES
        dealer = self.get_dealer()
        small_blind = big_blind = None
        if in_hand:
            small_blind = self.get_small_blind()
            big_blind = self.get_big_blind()

        print("\nPlayers:")
        for player in self.players:
            status = []

            if player.chips <= 0 and not player.all_in:
                status.append("out")

            if player is dealer and player.chips > 0:
                status.append("dealer")

            if player is small_blind:
                status.append("SB")

            if player is big_blind:
                status.append("BB")

            if player.folded:
                status.append("folded")

            if player.all_in:
                status.append("all-in")

            if in_hand and player == self.current_player:
                status.append("TO ACT")

            status_text = f" ({', '.join(status)})" if status else ""

            print(
                f"  {player.name}: "
                f"{player.chips} chips"
                f"{status_text}"
            )

        print("=" * 44)

    def display_player_hand(self, player):
        if player.name == self.human_name:
            print("\nYour hand:")
        else:
            print(f"\n{player.name}'s hand:")

        for card in player.hand:
            print(f"  {card.short():<5} ({card})")

    def display_action_summary(self, player):
        betting_round = self.betting_round
        to_call = betting_round.get_amount_to_call(player, self.pot)
        legal_actions = betting_round.get_legal_actions(player, self.pot)

        print(f"\nYour chips: {player.chips}   Pot: {self.pot.amount}")
        if to_call > 0:
            print(f"To call: {min(to_call, player.chips)}")

        print("\nLegal actions:")

        for action in legal_actions:
            if action == BettingAction.CALL:
                print(f"  call  (costs {to_call})")
            elif action == BettingAction.BET:
                low = min(betting_round.minimum_bet, player.chips)
                print(f"  bet   (min {low}, max {player.chips})")
            elif action == BettingAction.RAISE:
                high = betting_round.get_max_raise(player, self.pot)
                low = betting_round.min_raise_amount
                print(
                    f"  raise (raise BY {low} to {high}; "
                    f"bet becomes {betting_round.current_bet + low}+)"
                )
            elif action == BettingAction.ALL_IN:
                print(f"  all-in ({player.chips})")
            else:
                print(f"  {action.value}")

    def display_hand_result(self):
        """Print who won the last hand and with what."""
        result = self.last_result

        if result is None:
            return

        if result["showdown"]:
            print("\n=== SHOWDOWN ===")
            print(f"Board: {self.format_cards(self.community_cards)}")

            for player, hand in result["hands"].items():
                print(
                    f"  {player.name:<10} "
                    f"{self.format_cards(player.hand):<10} "
                    f"{describe_hand(hand)}"
                )

        print()
        for pot in result["pots"]:
            names = ", ".join(winner.name for winner in pot["winners"])
            verb = "wins" if len(pot["winners"]) == 1 else "split"
            line = f"{pot['label']} ({pot['amount']}): {names} {verb}"
            if pot["hand"] is not None:
                line += f" with {describe_hand(pot['hand'])}"
            print(line)

        for player, amount in result["refunds"].items():
            print(f"{player.name} gets {amount} back (uncalled bet)")

    # ------------------------------------------------------------------
    # Human interaction
    # ------------------------------------------------------------------

    def parse_action(self, command):
        command = command.strip().lower()

        action_names = {
            "fold": BettingAction.FOLD,
            "f": BettingAction.FOLD,

            "check": BettingAction.CHECK,
            "c": BettingAction.CHECK,

            "call": BettingAction.CALL,

            "bet": BettingAction.BET,
            "b": BettingAction.BET,

            "raise": BettingAction.RAISE,
            "r": BettingAction.RAISE,

            "all-in": BettingAction.ALL_IN,
            "allin": BettingAction.ALL_IN,
            "all in": BettingAction.ALL_IN,
            "a": BettingAction.ALL_IN,
        }

        if command not in action_names:
            raise ValueError("Invalid action")

        return action_names[command]

    def parse_command(self, command):
        command = command.strip().lower()

        if command in ("p", "probability"):
            return "probability"

        raise ValueError("Invalid command")

    def _read_amount(self, action, player, amount_text=None):
        """Ask for (and validate) a bet or raise amount."""
        betting_round = self.betting_round

        if action == BettingAction.BET:
            low = min(betting_round.minimum_bet, player.chips)
            high = player.chips
            prompt = f"Bet how much? ({low}-{high}): "
        else:
            low = betting_round.min_raise_amount
            high = betting_round.get_max_raise(player, self.pot)
            prompt = (
                f"Raise BY how much? ({low}-{high}, "
                f"on top of the current bet of "
                f"{betting_round.current_bet}): "
            )

        if amount_text is None:
            amount_text = input(prompt)

        try:
            amount = int(amount_text.strip())
        except ValueError:
            raise ValueError("Please enter a whole number")

        if amount < low or amount > high:
            raise ValueError(f"Amount must be between {low} and {high}")

        return amount

    def human_turn(self):
        """Run one decision for the current (human) player.

        Keeps asking until a legal action has been performed, so mistakes
        in the input never crash the game or lose the player's turn.
        Raises QuitGame if the player asks to leave.
        """
        player = self.current_player

        self.display_game_state()
        self.display_player_hand(player)
        self.display_action_summary(player)

        while True:
            legal_actions = self.betting_round.get_legal_actions(
                player,
                self.pot
            )

            command = input(
                "\nEnter action, 'p' for probability or 'q' to quit: "
            ).strip().lower()

            if command in ("q", "quit", "exit"):
                raise QuitGame()

            if command in ("p", "probability"):
                self.display_probability_report()
                continue

            if command in ("h", "help", "?"):
                self.display_action_summary(player)
                continue

            amount_text = None

            try:
                # "c" means check when that is possible, otherwise call.
                if (
                    command == "c"
                    and BettingAction.CHECK not in legal_actions
                    and BettingAction.CALL in legal_actions
                ):
                    action = BettingAction.CALL
                else:
                    try:
                        action = self.parse_action(command)
                    except ValueError:
                        # Allow "raise 40" / "bet 20" on a single line.
                        parts = command.rsplit(None, 1)
                        if len(parts) != 2:
                            raise
                        action = self.parse_action(parts[0])
                        amount_text = parts[1]

                if action not in legal_actions:
                    raise ValueError(
                        f"{action.value} is not currently a legal action"
                    )

                amount = None

                if action in (BettingAction.BET, BettingAction.RAISE):
                    amount = self._read_amount(action, player, amount_text)

                self.perform_action(action, amount)
                return

            except ValueError as error:
                message = str(error)
                if message == "Invalid action":
                    message = (
                        "Invalid action. Use fold, check, call, bet, "
                        "raise, all-in, p (probability) or q (quit)"
                    )
                print(f"\n*** {message} ***")

    # ------------------------------------------------------------------
    # Probability (human)
    # ------------------------------------------------------------------

    def get_probability_report(self):
        if self.state not in (
            GameState.FLOP,
            GameState.TURN,
            GameState.RIVER,
        ):
            raise ValueError(
                "Probability calculations are available "
                "from the flop onwards"
            )

        if self.current_player is None:
            raise ValueError(
                "There is no current player"
            )

        known_cards = (
            self.current_player.hand
            + self.community_cards
        )

        return probability_report(known_cards)

    def get_human_probability_report(self):
        if self.state not in (
            GameState.FLOP,
            GameState.TURN,
            GameState.RIVER,
        ):
            raise ValueError(
                "Probability calculations are available "
                "from the flop onwards"
            )

        human_player = self.get_human_player()

        if human_player is None:
            raise ValueError(
                "Human player not found"
            )

        known_cards = (
            human_player.hand
            + self.community_cards
        )

        return probability_report(known_cards)

    def get_human_equity(self, simulations=2000):
        """Monte Carlo win/tie/loss estimate for the human player.

        Returns ``(equity, number_of_opponents)``.
        """
        human_player = self.get_human_player()

        if human_player is None:
            raise ValueError("Human player not found")

        if human_player.folded or len(human_player.hand) != 2:
            raise ValueError("The human player is not in the hand")

        opponents = [
            player
            for player in self.get_players_remaining_in_hand()
            if player is not human_player
        ]

        if not opponents:
            raise ValueError("There are no opponents left")

        equity = monte_carlo_equity(
            human_player.hand,
            self.community_cards,
            len(opponents),
            simulations
        )

        return equity, len(opponents)

    def _print_equity(self):
        try:
            equity, opponents = self.get_human_equity()
        except ValueError:
            return

        print(
            f"\nChance to win against {opponents} random "
            f"opponent{'s' if opponents != 1 else ''} "
            f"(Monte Carlo estimate):"
        )
        print(f"  Win:  {equity['win'] * 100:6.2f}%")
        print(f"  Tie:  {equity['tie'] * 100:6.2f}%")
        print(f"  Lose: {equity['loss'] * 100:6.2f}%")

    def display_probability_report(self):
        human_player = self.get_human_player()

        if human_player is None:
            print("\nHuman player not found.")
            return

        if human_player.folded:
            print("\nYou have folded - no probability to show.")
            return

        if self.state == GameState.PRE_FLOP:
            print("\n=== YOUR PRE-FLOP HAND ===")
            for card in human_player.hand:
                print(f"  {card}")
            print("\nHand-type probabilities are available")
            print("once the flop is dealt.")
            self._print_equity()
            return

        report = self.get_human_probability_report()

        hand_names = {
            HandRank.ONE_PAIR: "One Pair",
            HandRank.TWO_PAIR: "Two Pair",
            HandRank.THREE_OF_A_KIND: "Three of a Kind",
            HandRank.STRAIGHT: "Straight",
            HandRank.FLUSH: "Flush",
            HandRank.FULL_HOUSE: "Full House",
            HandRank.FOUR_OF_A_KIND: "Four of a Kind",
            HandRank.STRAIGHT_FLUSH: "Straight Flush",
            HandRank.ROYAL_FLUSH: "Royal Flush",
        }

        print("\n=== YOUR PROBABILITIES ===")

        # River: no cards remain
        if self.state == GameState.RIVER:
            current_hand = evaluate(
                human_player.hand + self.community_cards
            )

            print(f"Current hand: {describe_hand(current_hand)}")

            self._print_equity()
            return

        print("Chance your best hand ends up as exactly:")

        # Turn: one card remains
        if self.state == GameState.TURN:
            print(
                f"{'Hand':<20}"
                f"{'By River':>12}"
            )
            print("-" * 32)

            for hand_rank, name in hand_names.items():
                probability = (
                    report["by_river"][hand_rank] * 100
                )

                print(
                    f"{name:<20}"
                    f"{probability:>11.2f}%"
                )

            self._print_equity()
            return

        # Flop: two cards remain
        print(
            f"{'Hand':<20}"
            f"{'Turn':>10}"
            f"{'By River':>12}"
        )
        print("-" * 42)

        for hand_rank, name in hand_names.items():
            turn_probability = (
                report["turn"][hand_rank] * 100
            )

            river_probability = (
                report["by_river"][hand_rank] * 100
            )

            print(
                f"{name:<20}"
                f"{turn_probability:>9.2f}%"
                f"{river_probability:>11.2f}%"
            )

        self._print_equity()
