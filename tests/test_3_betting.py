"""Requirement group 3: betting and blinds."""
import pytest

from betting import BettingAction as A, BettingRound
from game import GameState
from helpers import act, fold_until_done, full_table, snapshot, table
from player import Player
from pot import Pot

BIG_BLIND = 20


def setup(*chips):
    """A fresh betting round (minimum bet 20) and players with these stacks."""
    pot, rnd = Pot(), BettingRound()
    rnd.minimum_bet = BIG_BLIND
    rnd.start_new_round(pot)
    return rnd, pot, [Player(f"P{i}", c) for i, c in enumerate(chips, 1)]


def test_legal_actions_depend_on_what_is_owed():
    # 3.1
    rnd, pot, (p1, p2, p3) = setup(1000, 1000, 30)
    # nothing owed: check or bet, never call or raise
    assert set(rnd.get_legal_actions(p1, pot)) == {A.CHECK, A.BET, A.ALL_IN, A.FOLD}
    rnd.bet(p2, pot, 50)
    # a bet is open and affordable: call or raise, never check or bet
    assert set(rnd.get_legal_actions(p1, pot)) == {A.CALL, A.RAISE, A.ALL_IN, A.FOLD}
    # a bet is open but p3 (30 chips) cannot afford the call: all-in or fold only
    assert set(rnd.get_legal_actions(p3, pot)) == {A.ALL_IN, A.FOLD}
    # boundaries: owing exactly one chip forbids a check; a stack one short of the call forbids a call
    owes_one = BettingRound()
    assert owes_one.can_check(p1, Pot())
    owes_one.current_bet = 1
    assert not owes_one.can_check(p1, Pot())
    rnd.current_bet = 50
    assert not rnd.can_call(Player("short", 49), pot)
    assert rnd.can_call(Player("exact", 50), pot)


def test_amount_to_call_is_current_bet_minus_contribution_and_never_negative():
    # 3.4
    rnd, pot, (p1, p2, p3) = setup(1000, 1000, 1000)
    rnd.bet(p1, pot, 50)
    assert rnd.get_amount_to_call(p1, pot) == 0      # already matched
    assert rnd.get_amount_to_call(p2, pot) == 50
    pot.add_bet(p3, 80)                              # contributes more than the bet
    assert rnd.get_amount_to_call(p3, pot) == 0
    rnd.call(p2, pot)
    assert rnd.get_amount_to_call(p2, pot) == 0


@pytest.mark.parametrize("amount, accepted", [(1, False), (19, False), (20, True), (21, True)])
def test_opening_bet_below_the_big_blind_is_rejected(amount, accepted):
    # 3.5 boundary values around the minimum bet (20)
    rnd, pot, (p1, *_ ) = setup(1000, 1000)
    if accepted:
        rnd.bet(p1, pot, amount)
        assert rnd.current_bet == amount
    else:
        with pytest.raises(ValueError):
            rnd.bet(p1, pot, amount)
        assert p1.chips == 1000 and pot.amount == 0


def test_opening_bet_below_minimum_is_allowed_only_when_it_is_all_in():
    # 3.5 exception, and 3.2 never more than the stack
    rnd, pot, (short, rich) = setup(15, 1000)
    with pytest.raises(ValueError):
        rnd.bet(short, pot, 16)                      # more than the stack
    rnd.bet(short, pot, 15)                          # all-in below the minimum
    assert short.all_in and short.chips == 0


def test_raise_below_the_minimum_is_rejected_and_the_boundary_is_accepted():
    # 3.5 minimum raise = size of the last full bet or raise
    rnd, pot, (p1, p2, p3, p4) = setup(1000, 1000, 1000, 1000)
    rnd.bet(p1, pot, 50)                             # minimum raise is now 50
    for too_small in (1, 49):
        with pytest.raises(ValueError):
            rnd.raise_bet(p2, pot, too_small)
    rnd.raise_bet(p2, pot, 50)                       # exactly the minimum
    assert rnd.current_bet == 100
    # a re-raise must be at least the last raise (70 here)
    rnd.raise_bet(p3, pot, 70)
    with pytest.raises(ValueError):
        rnd.raise_bet(p4, pot, 69)
    rnd.raise_bet(p4, pot, 70)
    assert rnd.current_bet == 240


def test_raise_cannot_exceed_the_stack():
    # 3.2 boundary at the maximum raise
    rnd, pot, (p1, p2) = setup(1000, 300)
    rnd.bet(p1, pot, 50)
    top = rnd.get_max_raise(p2, pot)                 # 300 - 50 = 250
    assert top == 250
    with pytest.raises(ValueError):
        rnd.raise_bet(p2, pot, top + 1)
    rnd.raise_bet(p2, pot, top)
    assert p2.chips == 0 and p2.all_in


def test_short_all_in_does_not_lower_the_bet_or_change_the_minimum_raise():
    # 3.6
    rnd, pot, (p1, p2, p3) = setup(1000, 60, 30)
    rnd.bet(p1, pot, 50)
    assert rnd.min_raise_amount == 50
    rnd.all_in(p2, pot)                              # 60 total: only 10 more, not a full raise
    assert rnd.current_bet == 60 and rnd.min_raise_amount == 50
    rnd.all_in(p3, pot)                              # 30 total: below the bet
    assert rnd.current_bet == 60 and rnd.min_raise_amount == 50


def test_folded_and_all_in_players_cannot_act():
    # 3.3
    rnd, pot, (p1, p2, p3) = setup(1000, 1000, 1000)
    rnd.fold(p1)
    rnd.all_in(p2, pot)
    for player in (p1, p2):
        assert rnd.get_legal_actions(player, pot) == []
    with pytest.raises(ValueError):
        rnd.check(p1, pot)
    with pytest.raises(ValueError):
        rnd.call(p1, pot)
    with pytest.raises(ValueError):
        rnd.bet(p2, pot, 20)
    with pytest.raises(ValueError):
        rnd.raise_bet(p2, pot, 20)
    with pytest.raises(ValueError):
        rnd.all_in(p2, pot)


@pytest.mark.parametrize(
    "action, amount",
    [
        (A.CHECK, None),            # the big blind is owed
        (A.BET, 100),               # a bet already exists
        (A.RAISE, None),            # amount missing
        (A.RAISE, 5),               # below the minimum raise
        (A.RAISE, 10**6),           # more than the stack
        ("jump", None),             # not an action
    ],
)
def test_illegal_action_is_rejected_and_changes_nothing(action, amount):
    # 3.8 chips, pot, bets and turn order exactly as before
    game = full_table()
    game.start_hand()
    before = snapshot(game)
    with pytest.raises(ValueError):
        game.perform_action(action, amount)
    assert snapshot(game) == before


def test_betting_round_ends_only_after_everyone_has_had_a_chance_to_act():
    # 3.7 the big blind keeps the option to raise even if everyone just calls
    game = full_table()
    game.start_hand()
    big_blind = game.get_big_blind()
    act(game, *[A.CALL] * 8)                         # all seven others and the small blind
    assert game.state == GameState.PRE_FLOP
    assert game.current_player is big_blind
    game.perform_action(A.CHECK)
    assert game.state == GameState.FLOP


def test_blinds_rise_after_the_configured_number_of_hands_and_then_stay():
    # 3.10 levels (10,20) (20,40) (40,80), 2 hands per level
    game = full_table(blind_levels=[(10, 20), (20, 40), (40, 80)], hands_per_level=2)
    seen = []
    for _ in range(7):
        game.start_hand()
        seen.append(game.get_blind_amounts())
        fold_until_done(game)
        game.reset_hand()
    assert seen == [(10, 20), (10, 20), (20, 40), (20, 40), (40, 80), (40, 80), (40, 80)]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"blind_levels": []},
        {"blind_levels": [(0, 10)]},
        {"blind_levels": [(-5, 10)]},
        {"blind_levels": [(20, 10)]},
        {"hands_per_level": 0},
    ],
)
def test_invalid_blind_configuration_is_rejected(kwargs):
    # 3.11
    with pytest.raises(ValueError):
        full_table(**kwargs)


@pytest.mark.parametrize("seat, stack", [(1, 5), (2, 15)])
def test_player_who_cannot_cover_a_blind_posts_what_they_have_and_is_all_in(seat, stack):
    # 3.9 hand 1: dealer is seat 0, small blind seat 1 (10), big blind seat 2 (20)
    chips = [1000] * 9
    chips[seat] = stack
    game = table(chips)
    game.start_hand()
    short = game.players[seat]
    assert game.pot.get_contribution(short) == stack
    assert short.chips == 0 and short.all_in
