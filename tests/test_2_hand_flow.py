"""Requirement group 2: hand flow and tournament progression."""
import pytest

from betting import BettingAction as A
from game import BETTING_STATES, GameState as S
from helpers import act, check_down, finish, fold_until_done, full_table, play_to, snapshot, stack_deck, table
from player import Player
from game import PokerGame
from simulate import play_tournament


def test_a_hand_moves_through_every_state_in_order():
    # 2.3 and 2.4 the seven states and their 11 legal transitions, part 1:
    # the main line NEW_HAND -> PRE_FLOP -> FLOP -> TURN -> RIVER -> SHOWDOWN -> HAND_COMPLETE -> NEW_HAND
    game = full_table()
    states, board_sizes = [game.state], []
    game.start_hand()
    while game.state != S.SHOWDOWN:
        if not states or states[-1] != game.state:
            states.append(game.state)
            board_sizes.append(len(game.community_cards))
        act(game, A.CHECK if A.CHECK in game.betting_round.get_legal_actions(
            game.current_player, game.pot) else A.CALL)
    states.append(game.state)
    game.complete_hand()
    states.append(game.state)
    game.reset_hand()
    states.append(game.state)
    assert states == [S.NEW_HAND, S.PRE_FLOP, S.FLOP, S.TURN, S.RIVER, S.SHOWDOWN,
                      S.HAND_COMPLETE, S.NEW_HAND]
    assert board_sizes == [0, 3, 4, 5]


@pytest.mark.parametrize("state", list(BETTING_STATES), ids=lambda s: s.name)
def test_a_hand_can_end_by_folds_from_each_betting_state(state):
    # 2.3 and 2.4 transitions part 2: each betting state straight to HAND_COMPLETE.
    # 2.4 the last player left wins without a showdown.
    game = full_table()
    game.start_hand()
    play_to(game, state)
    fold_until_done(game)
    assert game.state == S.HAND_COMPLETE
    assert game.last_result["showdown"] is False
    assert game.pot.amount == 0
    assert sum(p.chips for p in game.players) == 9000


STATE_MOVES = [
    (S.NEW_HAND, ["move_to_flop", "move_to_turn", "move_to_river", "move_to_showdown", "complete_hand", "reset_hand"]),
    (S.PRE_FLOP, ["move_to_turn", "move_to_river", "move_to_showdown", "complete_hand", "reset_hand", "start_hand"]),
    (S.FLOP, ["move_to_flop", "move_to_river", "move_to_showdown", "complete_hand", "reset_hand"]),
    (S.RIVER, ["move_to_flop", "move_to_turn", "complete_hand", "start_hand"]),
    (S.HAND_COMPLETE, ["start_hand", "move_to_flop", "complete_hand", "advance_state"]),
]


@pytest.mark.parametrize("state, moves", STATE_MOVES, ids=lambda v: v.name if hasattr(v, "name") else "moves")
def test_operations_in_the_wrong_state_raise_and_change_nothing(state, moves):
    # 2.3 and 8.4 illegal transitions (for example flop to river) are rejected
    game = full_table()
    if state != S.NEW_HAND:
        game.start_hand()
        if state == S.HAND_COMPLETE:
            fold_until_done(game)
        else:
            play_to(game, state)
    assert game.state == state
    before = snapshot(game)
    for move in moves:
        with pytest.raises(ValueError):
            getattr(game, move)()
        assert snapshot(game) == before, move
    if state == S.NEW_HAND:
        with pytest.raises(ValueError):
            game.perform_action(A.CHECK)             # no betting outside a betting round


def test_when_everyone_folds_the_last_player_takes_the_pot_without_a_showdown():
    # 2.4 the big blind wins the blinds when the other eight fold
    game = full_table()
    game.start_hand()
    big_blind = game.get_big_blind()
    act(game, *[A.FOLD] * 8)
    assert game.state == S.HAND_COMPLETE
    assert game.community_cards == []
    assert big_blind.chips == 1000 + 10              # wins the small blind's 10
    assert game.last_result["pots"][0]["winners"] == [big_blind]


def test_when_everyone_is_all_in_the_board_is_dealt_out_without_more_betting(monkeypatch):
    # 2.5 three all-in players: straight to showdown with five community cards
    stack_deck(monkeypatch, ["AS", "KS", "QS", "AH", "KH", "QH",
                             "??", "2C", "7D", "9H", "??", "4C", "??", "3D"])
    game = table([100, 300, 500])
    game.start_hand()
    act(game, A.ALL_IN, A.ALL_IN, A.ALL_IN)
    assert game.state == S.SHOWDOWN
    assert len(game.community_cards) == 5
    # one player still has chips but nobody to bet against: the board is dealt out as well
    game = table([100, 100, 1000])
    game.start_hand()
    act(game, A.ALL_IN, A.ALL_IN, A.CALL)
    assert game.state == S.SHOWDOWN
    assert len(game.community_cards) == 5


def test_dealer_and_blinds_move_one_seat_and_skip_eliminated_players():
    # 2.6 and 2.8 seat 1 has no chips, so the dealer button jumps from seat 0 to seat 2
    game = table([1000, 0, 1000, 1000, 1000, 1000, 1000, 1000, 1000])
    game.start_hand()
    assert game.players.index(game.get_dealer()) == 0
    assert game.players.index(game.get_small_blind()) == 2     # seat 1 is skipped
    assert game.players.index(game.get_big_blind()) == 3
    assert game.players[1].hand == []                          # eliminated players are not dealt in
    fold_until_done(game)
    game.reset_hand()
    assert game.players.index(game.get_dealer()) == 2          # one seat clockwise, skipping seat 1
    game.start_hand()
    assert game.players.index(game.get_small_blind()) == 3
    assert game.players.index(game.get_big_blind()) == 4


def test_heads_up_dealer_is_small_blind_and_acts_first_before_the_flop_only():
    # 2.7
    game = table([1000, 1000])
    game.start_hand()
    dealer = game.get_dealer()
    other = game.players[1] if dealer is game.players[0] else game.players[0]
    assert game.get_small_blind() is dealer and game.get_big_blind() is other
    assert game.current_player is dealer                       # first to act pre-flop
    act(game, A.CALL, A.CHECK)
    assert game.state == S.FLOP
    assert game.current_player is other                        # the big blind acts first after the flop


def test_game_needs_exactly_nine_players_with_unique_names():
    # 2.1
    for count in (8, 10):
        with pytest.raises(ValueError):
            PokerGame([Player(f"P{i}", 100) for i in range(count)])
    with pytest.raises(ValueError):
        PokerGame([Player(f"P{i}", 100) for i in range(8)] + [Player("P0", 100)])


def test_game_ends_when_one_player_holds_all_the_chips(monkeypatch):
    # 2.9 heads-up all-in; the aces win
    stack_deck(monkeypatch, ["AS", "2C", "AH", "7D", "??", "3C", "9D", "JH", "??", "5S", "??", "8C"])
    game = table([100, 100])
    assert not game.is_game_over()
    game.start_hand()
    act(game, A.ALL_IN, A.ALL_IN)
    finish(game)
    assert game.is_game_over()
    assert [p.chips for p in game.players[:2]] == [200, 0]
    with pytest.raises(ValueError):
        game.reset_hand()                            # nothing more to play
    game.state = S.NEW_HAND
    with pytest.raises(ValueError):
        game.start_hand()                            # a single player cannot start a hand


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_bot_only_tournament_from_a_seed_finishes_with_one_winner(seed):
    # 2.10 (the simulator also checks every invariant after each action)
    result = play_tournament(seed)
    assert result["finished"] and result["winner_chips"] == 9000
