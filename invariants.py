"""Run-time checks for the poker game (instrumentation, no game logic).

An invariant is a statement that must be true of *every* reachable game
state, whatever the cards or the bots did. Checking them after each action
turns a silent corruption (a chip appearing from nowhere, a card dealt
twice) into an immediate, located failure instead of a strange result many
hands later.

This module only reads the game; it never changes it.
"""
from game import GameState, BETTING_STATES

# Number of community cards each state must show. HAND_COMPLETE is not listed
# because a hand won by folds can end on any street.
COMMUNITY_CARDS_BY_STATE = {
    GameState.NEW_HAND: 0,
    GameState.PRE_FLOP: 0,
    GameState.FLOP: 3,
    GameState.TURN: 4,
    GameState.RIVER: 5,
    GameState.SHOWDOWN: 5,
}


class InvariantViolation(AssertionError):
    """Raised when a game state breaks one of the invariants."""


def find_violations(game, total_chips):
    """Return a list of plain-English problems found in the game state.

    ``total_chips`` is the number of chips that existed at the start of the
    game; chips in stacks plus the pot must always add up to it.
    """
    problems = []

    # Chips are conserved.
    stacks = sum(player.chips for player in game.players)
    if stacks + game.pot.amount != total_chips:
        problems.append(
            f"chip total is {stacks + game.pot.amount} "
            f"(stacks {stacks} + pot {game.pot.amount}), "
            f"expected {total_chips}"
        )

    # No negative amounts.
    for player in game.players:
        if player.chips < 0:
            problems.append(f"{player.name} has negative chips ({player.chips})")
    if game.pot.amount < 0:
        problems.append(f"the pot is negative ({game.pot.amount})")

    # The pot's per-player record agrees with the pot total.
    recorded = sum(game.pot.contributions.values())
    if recorded != game.pot.amount:
        problems.append(
            f"pot contributions add up to {recorded} but the pot holds "
            f"{game.pot.amount}"
        )

    # Cards: right counts, none dealt twice.
    for player in game.players:
        if len(player.hand) not in (0, 2):
            problems.append(
                f"{player.name} has {len(player.hand)} hole cards "
                f"(must be 0 or 2)"
            )

    expected_board = COMMUNITY_CARDS_BY_STATE.get(game.state)
    board = len(game.community_cards)
    if expected_board is not None and board != expected_board:
        problems.append(
            f"{board} community cards in state {game.state.name} "
            f"(expected {expected_board})"
        )
    if board > 5:
        problems.append(f"{board} community cards (maximum is 5)")

    seen = [card.card_id for player in game.players for card in player.hand]
    seen += [card.card_id for card in game.community_cards]
    seen += [card.card_id for card in game.deck.cards]
    duplicates = sorted({card for card in seen if seen.count(card) > 1})
    if duplicates:
        problems.append(f"duplicate card ids across hands, board and deck: {duplicates}")
    if len(seen) > 52:
        problems.append(f"{len(seen)} cards in play (maximum is 52)")

    # While betting, the player to act must really be able to act.
    if game.state in BETTING_STATES:
        player = game.current_player
        if player is None:
            problems.append("no player to act during a betting round")
        elif player.folded or player.all_in or player.chips <= 0:
            problems.append(
                f"player to act ({player.name}) has folded, is all-in "
                f"or has no chips"
            )
        for player in game.players:
            if player.hand and not player.folded and player.chips == 0 \
                    and not player.all_in:
                problems.append(
                    f"{player.name} has no chips but is not marked all-in"
                )

    return problems


def check_invariants(game, total_chips, context=""):
    """Raise InvariantViolation if the game state is inconsistent."""
    problems = find_violations(game, total_chips)
    if problems:
        message = "; ".join(problems)
        if context:
            message += f"\n{context}"
        raise InvariantViolation(message)
