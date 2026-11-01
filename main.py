import argparse
import random

from betting import BettingAction
from game import PokerGame, GameState, QuitGame, BETTING_STATES
from player import Player
from bot import Bot


STARTING_CHIPS = 1000
HUMAN_NAME = "You"

BOT_STRATEGIES = {
    "Player 2": "passive",
    "Player 3": "aggressive",
    "Player 4": "balanced",
    "Player 5": "passive",
    "Player 6": "balanced",
    "Player 7": "aggressive",
    "Player 8": "passive",
    "Player 9": "balanced",
}

STREET_NAMES = {3: "FLOP", 4: "TURN", 5: "RIVER"}


def create_game():
    players = [Player(HUMAN_NAME, STARTING_CHIPS)] + [
        Player(name, STARTING_CHIPS) for name in BOT_STRATEGIES
    ]

    return PokerGame(players, human_name=HUMAN_NAME)


def create_bots():
    return {
        name: Bot(strategy)
        for name, strategy in BOT_STRATEGIES.items()
    }


def announce_board(game, shown_cards):
    """Print each street that has been dealt since the last call.

    Returns the number of community cards now on the table.
    """
    total = len(game.community_cards)

    for count in (3, 4, 5):
        if shown_cards < count <= total:
            print(
                f"\n--- {STREET_NAMES[count]} --- "
                f"{game.format_cards(game.community_cards[:count])}   "
                f"(pot {game.pot.amount})"
            )

    return total


def bot_turn(game, bot):
    """Let a bot act and report what it did."""
    player = game.current_player

    legal_actions = game.betting_round.get_legal_actions(
        player,
        game.pot
    )

    situation = game.get_bot_situation(player)
    action, amount = bot.decide(legal_actions, situation)

    try:
        game.perform_action(action, amount)
    except ValueError:
        # A bot must never be able to stall the game: fall back to the
        # safest legal action.
        action, amount = BettingAction.FOLD, None
        for safe in (BettingAction.CHECK, BettingAction.CALL):
            if safe in legal_actions:
                action = safe
                break
        game.perform_action(action, None)

    to_call = situation["to_call"]

    if action == BettingAction.FOLD:
        text = "folds"
    elif action == BettingAction.CHECK:
        text = "checks"
    elif action == BettingAction.CALL:
        text = f"calls {to_call}"
    elif action == BettingAction.BET:
        text = f"bets {amount}"
    elif action == BettingAction.RAISE:
        total = situation["current_bet"] + amount
        text = f"raises by {amount} (bet is now {total})"
    else:
        text = f"goes ALL-IN ({situation['chips']} chips)"

    print(f"  {player.name} ({bot.strategy}) {text}")


def play_hand(game, bots):
    """Play one complete hand and return the players it eliminated."""
    game.start_hand()

    chips_before = {
        player.name: player.chips for player in game.players
    }

    small_blind = game.get_small_blind()
    big_blind = game.get_big_blind()

    print("\n" + "#" * 44)
    print(
        f"HAND #{game.hand_number}   "
        f"blinds {game.small_blind}/{game.big_blind} "
        f"(level {game.get_blind_level()})"
    )
    print(
        f"Dealer: {game.get_dealer().name}   "
        f"SB: {small_blind.name}   BB: {big_blind.name}"
    )
    print("#" * 44)

    human = game.get_human_player()
    if human is not None and human.hand:
        print(f"\nYour cards: {game.format_cards(human.hand)}")

    shown_cards = 0

    while game.state in BETTING_STATES:
        shown_cards = announce_board(game, shown_cards)

        if game.current_player.name == game.human_name:
            game.human_turn()
        else:
            bot_turn(game, bots[game.current_player.name])

    announce_board(game, shown_cards)

    if game.state == GameState.SHOWDOWN:
        game.complete_hand()

    game.display_hand_result()

    return [
        player for player in game.players
        if chips_before[player.name] > 0 and player.chips == 0
    ]


def display_standings(game):
    print("\nChip counts:")
    for player in sorted(
        game.players,
        key=lambda candidate: candidate.chips,
        reverse=True
    ):
        marker = "  <-- you" if player.name == game.human_name else ""
        status = "" if player.chips > 0 else "  (eliminated)"
        print(f"  {player.name:<10} {player.chips:>6}{status}{marker}")


def ask_to_continue():
    answer = input("\nPlay another hand? (Y/n): ").strip().lower()

    return answer not in ("n", "no", "q", "quit", "exit")


def print_final_result(game):
    standing = sorted(
        game.players,
        key=lambda candidate: candidate.chips,
        reverse=True
    )
    leader = standing[0]

    if game.is_game_over():
        if leader.name == game.human_name:
            print(
                f"\n*** You win the tournament with "
                f"{leader.chips} chips! ***"
            )
        else:
            print(f"\n*** {leader.name} wins the tournament. ***")
    else:
        print(
            f"\nFinal chip leader: {leader.name} "
            f"with {leader.chips} chips."
        )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Texas Hold'em vs 8 bots")
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="random seed for reproducible games"
    )
    arguments = parser.parse_args(argv)

    if arguments.seed is not None:
        random.seed(arguments.seed)

    game = create_game()
    bots = create_bots()

    print("=== TEXAS HOLD'EM ===")
    print(f"You and 8 bots start with {STARTING_CHIPS} chips each.")
    print("Opponents:")
    for name, strategy in BOT_STRATEGIES.items():
        print(f"  {name}: {strategy}")
    print("\nType 'p' on your turn for a win-probability estimate,")
    print("or 'q' to quit.")

    try:
        while not game.is_game_over():
            eliminated = play_hand(game, bots)

            for player in eliminated:
                print(f"\n{player.name} has been eliminated.")

            display_standings(game)

            if game.is_game_over():
                break

            if game.get_human_player().chips == 0:
                print("\nYou are out of chips - game over.")
                break

            if not ask_to_continue():
                break

            old_blinds = game.get_blind_amounts()
            game.reset_hand()

            if game.get_blind_amounts() != old_blinds:
                small, big = game.get_blind_amounts()
                print(f"\n*** Blinds increase to {small}/{big} ***")

    except (QuitGame, KeyboardInterrupt, EOFError):
        print("\n\nLeaving the table.")

    print_final_result(game)
    print("\nGame over.")


if __name__ == "__main__":
    main()
