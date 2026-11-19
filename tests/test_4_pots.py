"""Requirement group 4: pots and payout."""
import random

import pytest

from betting import BettingAction as A
from bot import Bot
from game import BETTING_STATES, GameState
from helpers import act, check_down, finish, full_table, stack_deck, table
from player import Player
from pot import Pot


def players(*chips):
    return [Player(f"P{i}", c) for i, c in enumerate(chips, 1)]


def test_pot_equals_contributions_and_a_folded_players_chips_stay():
    # 4.1
    pot = Pot()
    a, b, c = players(500, 500, 500)
    pot.add_bet(a, 50)
    pot.add_bet(b, 50)
    pot.add_bet(c, 20)
    c.fold()
    pot.add_bet(a, 100)
    assert pot.amount == 220 == sum(pot.contributions.values())
    assert pot.get_contribution(c) == 20             # still counted after folding
    with pytest.raises(ValueError):
        pot.add_bet(c, 10)                           # a folded player cannot add more


def test_players_all_in_for_different_amounts_make_main_and_side_pots():
    # 4.2 three levels (100, 200, 300), plus 50 from a player who folded
    pot = Pot()
    a, b, c, folded = players(100, 200, 300, 500)
    for player, amount in ((a, 100), (b, 200), (c, 300), (folded, 50)):
        pot.add_bet(player, amount)
    folded.fold()
    pots, refunds = pot.build_side_pots([a, b, c])
    assert pots == [(350, [a, b, c]), (200, [b, c]), (100, [c])]
    assert refunds == {}
    assert sum(amount for amount, _ in pots) == pot.amount


def test_chips_nobody_can_match_go_back_to_their_owner():
    # 4.3 a player who put in 300 and folded; the two contenders matched only 100
    pot = Pot()
    big, b, c = players(500, 100, 100)
    for player, amount in ((big, 300), (b, 100), (c, 100)):
        pot.add_bet(player, amount)
    big.fold()
    pots, refunds = pot.build_side_pots([b, c])
    assert pots == [(300, [b, c])]
    assert refunds == {big: 200}


def play_three_way_all_in(monkeypatch, hands):
    """Seats 0, 1, 2 hold 100, 300, 500 chips and all go all-in pre-flop.

    ``hands`` gives each seat's two hole cards. The board is 2C 7D 9H 4C 3D.
    """
    first, second, third = (h.split() for h in hands)
    stack_deck(monkeypatch, [first[0], second[0], third[0], first[1], second[1], third[1],
                             "??", "2C", "7D", "9H", "??", "4C", "??", "3D"])
    game = table([100, 300, 500])
    game.start_hand()
    act(game, A.ALL_IN, A.ALL_IN, A.ALL_IN)          # seat 0 (dealer) acts first with 3 players
    assert game.state == GameState.SHOWDOWN
    game.complete_hand()
    return game


def test_each_pot_goes_to_the_best_hand_among_the_players_eligible_for_it(monkeypatch):
    # 4.4 seat 0 (100 chips) has the best hand but can only win the pot it matched
    game = play_three_way_all_in(monkeypatch, ["AS AH", "KS KH", "QS QH"])
    seat0, seat1, seat2 = game.players[:3]
    assert (seat0.chips, seat1.chips, seat2.chips) == (300, 400, 200)
    assert sum(p.chips for p in game.players) == 900


def test_shortest_stack_with_the_worst_hand_is_eliminated(monkeypatch):
    # 4.4 and 2.8 the best hand sits in the big stack
    game = play_three_way_all_in(monkeypatch, ["QS QH", "KS KH", "AS AH"])
    seat0, seat1, seat2 = game.players[:3]
    assert (seat0.chips, seat1.chips, seat2.chips) == (0, 0, 900)


def test_uncalled_chips_are_returned_when_the_other_player_is_short(monkeypatch):
    # 4.3 heads-up: 500 chips all-in against a 100-chip stack that holds the better hand
    stack_deck(monkeypatch, ["7C", "AS", "2D", "AH", "??", "3C", "9D", "JH", "??", "5S", "??", "8C"])
    game = table([500, 100])
    game.start_hand()
    act(game, A.ALL_IN, A.ALL_IN)
    game.complete_hand()
    rich, short = game.players[:2]
    assert short.chips == 200 and rich.chips == 400  # short stack wins only what it matched


def test_odd_chip_goes_to_the_winner_nearest_the_dealers_left(monkeypatch):
    # 4.5 pot of 25 split between seats 0 and 2: seat 2 is nearer the dealer's left
    stack_deck(monkeypatch, ["2C", "4D", "2S", "3D", "5D", "3C",
                             "??", "AH", "KH", "QH", "??", "JH", "??", "TH"])
    game = table([100, 100, 100], blind_levels=[(5, 10)])
    game.start_hand()
    act(game, A.CALL, A.FOLD, A.CHECK)               # seat 0 calls 10, small blind folds, big blind checks
    check_down(game)                                 # the board (royal flush in hearts) plays for both
    finish(game)
    seat0, seat1, seat2 = game.players[:3]
    assert (seat0.chips, seat1.chips, seat2.chips) == (90 + 12, 95, 90 + 13)


def test_chips_are_conserved_over_many_hands_with_all_in_bots():
    # 4.6 nine bots, a fixed seed, a mix of strategies; 9,000 chips after every hand
    rng = random.Random(11)
    random.seed(11)
    game = full_table(blind_levels=[(50, 100)], hands_per_level=10)
    bots = [Bot(s) for s in ("aggressive", "balanced", "passive")]
    for hand in range(25):
        if game.is_game_over():
            break
        game.start_hand()
        while game.state in BETTING_STATES:
            player = game.current_player
            legal = game.betting_round.get_legal_actions(player, game.pot)
            situation = game.get_bot_situation(player)
            action, amount = rng.choice(bots).decide(legal, situation, equity=rng.random())
            game.perform_action(action, amount)
        finish(game)
        assert sum(p.chips for p in game.players) == 9000
        if not game.is_game_over():
            game.reset_hand()
