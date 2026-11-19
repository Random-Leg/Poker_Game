"""Tests for the instrumentation: invariants.py and simulate.py.

The instrumentation only helps if it (a) stays quiet on correct games and
(b) fires on broken ones, so both directions are tested. Faults are injected
by corrupting a game state by hand or by patching a game method.
"""
import pytest

import pot as pot_module
from betting import BettingAction
from bot import Bot
from game import GameState
from main import create_game
from invariants import InvariantViolation, check_invariants, find_violations
from simulate import play_tournament

TOTAL = 9000


def started_game(seed=1):
    import random
    random.seed(seed)
    game = create_game()
    game.start_hand()
    return game


# --- invariants stay quiet on correct states --------------------------------

def test_fresh_game_has_no_violations():
    assert find_violations(create_game(), TOTAL) == []


def test_started_hand_has_no_violations():
    assert find_violations(started_game(), TOTAL) == []


def test_check_invariants_is_silent_when_nothing_is_wrong():
    check_invariants(started_game(), TOTAL)


# --- invariants fire on corrupted states ------------------------------------

def add_chip(game):
    game.players[3].chips += 1


def remove_chip_from_pot(game):
    game.pot.amount -= 1


def negative_chips(game):
    game.players[2].chips = -5
    game.players[3].chips += 5


def third_hole_card(game):
    game.players[4].hand.append(game.deck.draw())


def six_community_cards(game):
    game.community_cards.extend(game.deck.draw() for _ in range(6))


def duplicate_between_players(game):
    game.players[1].hand[0] = game.players[0].hand[0]


def card_still_in_deck(game):
    game.deck.cards.append(game.players[0].hand[0])


def folded_player_to_act(game):
    game.current_player.folded = True


def board_does_not_match_state(game):
    game.community_cards.extend(game.deck.draw() for _ in range(3))


@pytest.mark.parametrize(
    "corrupt, expected_word",
    [
        (add_chip, "chip total"),
        (remove_chip_from_pot, "chip total"),
        (negative_chips, "negative"),
        (third_hole_card, "hole cards"),
        (six_community_cards, "community"),
        (duplicate_between_players, "duplicate"),
        (card_still_in_deck, "duplicate"),
        (folded_player_to_act, "to act"),
        (board_does_not_match_state, "community"),
    ],
)
def test_each_corruption_is_detected(corrupt, expected_word):
    game = started_game()
    corrupt(game)
    problems = find_violations(game, TOTAL)
    assert any(expected_word in problem for problem in problems), problems


def test_check_invariants_raises_with_the_problem_in_the_message():
    game = started_game()
    add_chip(game)
    with pytest.raises(InvariantViolation, match="chip total"):
        check_invariants(game, TOTAL)


# --- the simulator ----------------------------------------------------------

@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_bot_only_tournament_finishes_with_one_winner(seed):
    result = play_tournament(seed)
    assert result["finished"]
    assert result["hands"] > 0
    assert result["winner_chips"] == TOTAL


def test_same_seed_gives_identical_history():
    assert play_tournament(7)["history"] == play_tournament(7)["history"]


def test_different_seeds_give_different_histories():
    assert play_tournament(7)["history"] != play_tournament(8)["history"]


def test_history_records_every_action():
    result = play_tournament(3)
    assert len(result["history"]) == result["actions"]
    assert result["actions"] > result["hands"]


def test_illegal_bot_actions_are_counted_not_hidden(monkeypatch):
    # An illegal raise (1 chip, below the minimum) every time a bot is asked.
    monkeypatch.setattr(
        Bot, "decide",
        lambda self, legal, situation, equity=None: (BettingAction.RAISE, 1),
    )
    result = play_tournament(2, max_hands=3)
    assert result["illegal_bot_actions"] > 0


def test_injected_chip_leak_is_caught_with_context(monkeypatch):
    original = pot_module.Pot.add_bet

    def leaky_add_bet(self, player, amount):
        original(self, player, amount)
        self.amount += 1          # a bug: a chip appears from nowhere

    monkeypatch.setattr(pot_module.Pot, "add_bet", leaky_add_bet)
    with pytest.raises(InvariantViolation) as caught:
        play_tournament(4)
    message = str(caught.value)
    assert "chip total" in message
    assert "hand 1" in message          # says where it happened
    assert "recent actions" in message  # and what led up to it
