"""Play whole bot-only tournaments with the invariants checked at every step.

This is instrumentation, not game logic. It does three things the normal
game does not:

  * observe  - records every action taken (the history) and counts illegal
               bot actions instead of silently hiding them;
  * check    - runs invariants.check_invariants after every action and
               reports where and after what a problem appeared;
  * control  - a seed makes a whole tournament repeatable.

Run it from the command line:  python simulate.py --seed 1 --tournaments 20
"""
import argparse
import random
import time
from collections import deque

from betting import BettingAction
from game import GameState, BETTING_STATES
from invariants import InvariantViolation, check_invariants
from main import create_bots, create_game, HUMAN_NAME, STARTING_CHIPS

DEFAULT_MAX_HANDS = 1000
MAX_ACTIONS_PER_HAND = 300   # a hand that needs more than this is stuck
RECENT_ACTIONS_SHOWN = 8


def _describe(entry):
    hand, name, action, amount = entry
    text = f"hand {hand}: {name} {action}"
    return text if amount is None else f"{text} {amount}"


def play_tournament(
    seed,
    max_hands=DEFAULT_MAX_HANDS,
    starting_chips=STARTING_CHIPS,
    real_equity=False,
):
    """Play one tournament in which every seat, including "You", is a bot.

    Returns a dictionary with: finished, hands, actions, history (a list of
    (hand, player, action, amount) tuples), illegal_bot_actions, winner and
    winner_chips. Raises InvariantViolation, with the hand number and the
    recent actions in the message, if any state is inconsistent.

    ``real_equity=False`` gives each post-flop decision a random win
    probability instead of the 250-game Monte Carlo estimate. That keeps a
    tournament fast and still exercises every bot action; set it to True to
    run the bots exactly as they play in the real game.
    """
    random.seed(seed)

    game = create_game()
    for player in game.players:
        player.chips = starting_chips
    total_chips = starting_chips * len(game.players)

    bots = create_bots()
    bots[HUMAN_NAME] = type(next(iter(bots.values())))("balanced")

    history = []
    recent = deque(maxlen=RECENT_ACTIONS_SHOWN)
    illegal = []

    def check(where):
        context = (
            f"found in hand {game.hand_number}, {where} "
            f"(state {game.state.name}, seed {seed})\n"
            f"recent actions: " + (" | ".join(recent) or "none")
        )
        check_invariants(game, total_chips, context)

    hands = 0
    while not game.is_game_over() and hands < max_hands:
        game.start_hand()
        hands += 1
        check("after dealing")

        actions_this_hand = 0
        while game.state in BETTING_STATES:
            actions_this_hand += 1
            if actions_this_hand > MAX_ACTIONS_PER_HAND:
                raise InvariantViolation(
                    f"hand {game.hand_number} did not finish within "
                    f"{MAX_ACTIONS_PER_HAND} actions (seed {seed})\n"
                    f"recent actions: " + " | ".join(recent)
                )

            player = game.current_player
            legal = game.betting_round.get_legal_actions(player, game.pot)
            situation = game.get_bot_situation(player)
            equity = None
            if not real_equity and situation["community_cards"]:
                equity = random.random()
            action, amount = bots[player.name].decide(
                legal, situation, equity=equity
            )

            try:
                game.perform_action(action, amount)
            except ValueError as error:
                illegal.append((game.hand_number, player.name, action, amount, str(error)))
                action, amount = BettingAction.FOLD, None
                for safe in (BettingAction.CHECK, BettingAction.CALL):
                    if safe in legal:
                        action = safe
                        break
                game.perform_action(action, None)

            entry = (game.hand_number, player.name, action.name, amount)
            history.append(entry)
            recent.append(_describe(entry))
            check(f"after {_describe(entry)}")

        if game.state == GameState.SHOWDOWN:
            game.complete_hand()
            check("after showdown")

        if game.is_game_over():
            break   # the real game also stops here, without resetting

        game.reset_hand()
        check("after reset")

    winner = max(game.players, key=lambda player: player.chips)
    return {
        "finished": game.is_game_over(),
        "hands": hands,
        "actions": len(history),
        "history": history,
        "illegal_bot_actions": len(illegal),
        "illegal_details": illegal,
        "winner": winner.name,
        "winner_chips": winner.chips,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Bot-only tournaments with invariant checks")
    parser.add_argument("--seed", type=int, default=1, help="first seed")
    parser.add_argument("--tournaments", type=int, default=10)
    parser.add_argument("--max-hands", type=int, default=DEFAULT_MAX_HANDS)
    parser.add_argument("--real-equity", action="store_true",
                        help="use the real Monte Carlo estimate (slow)")
    arguments = parser.parse_args(argv)

    for seed in range(arguments.seed, arguments.seed + arguments.tournaments):
        started = time.perf_counter()
        result = play_tournament(
            seed, arguments.max_hands, real_equity=arguments.real_equity
        )
        seconds = time.perf_counter() - started
        status = "finished" if result["finished"] else "stopped at the hand limit"
        print(
            f"seed {seed}: {status} after {result['hands']} hands, "
            f"{result['actions']} actions, "
            f"{result['illegal_bot_actions']} illegal bot actions, "
            f"winner {result['winner']} ({seconds:.1f}s)"
        )


if __name__ == "__main__":
    main()
