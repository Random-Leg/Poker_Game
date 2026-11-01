"""Regression tests for the game-flow, side-pot and input-handling fixes."""
import pytest

from betting import BettingAction, BettingRound
from card import Card, Rank, Suit
from game import PokerGame, GameState, QuitGame, BETTING_STATES
from player import Player
from pot import Pot


def make_game(stacks=None, **kwargs):
    stacks = stacks or [1000] * 9
    players = [Player(f"P{i}", chips) for i, chips in enumerate(stacks)]
    return PokerGame(players, human_name="P0", **kwargs), players


def card(rank, suit, card_id=0):
    return Card(card_id, suit, rank)


def fold_everyone_out(game):
    while game.state in BETTING_STATES:
        game.perform_action(BettingAction.FOLD)


# ---------------------------------------------------------------- eliminated


def test_eliminated_players_are_not_dealt_in_or_counted():
    game, players = make_game([1000, 1000, 1000, 0, 0, 0, 1000, 1000, 1000])

    game.start_hand()

    for eliminated in players[3:6]:
        assert eliminated.hand == []
        assert eliminated not in game.get_players_remaining_in_hand()

    assert len(game.get_players_remaining_in_hand()) == 6


def test_eliminated_player_cannot_win_a_pot_with_the_board():
    game, players = make_game([1000, 1000, 0, 0, 0, 0, 0, 0, 0])

    game.start_hand()
    fold_everyone_out(game)

    assert game.state == GameState.HAND_COMPLETE
    assert sum(player.chips for player in players) == 2000
    assert all(player.chips == 0 for player in players[2:])


# ------------------------------------------------------------------- headsup


def test_heads_up_dealer_posts_small_blind_and_acts_first_pre_flop():
    game, players = make_game([1000, 0, 0, 0, 1000, 0, 0, 0, 0])

    game.start_hand()

    assert game.get_small_blind() is players[0]
    assert game.get_big_blind() is players[4]
    assert game.current_player is players[0]
    assert game.pot.get_contribution(players[0]) == 10
    assert game.pot.get_contribution(players[4]) == 20


def test_heads_up_big_blind_acts_first_after_the_flop():
    game, players = make_game([1000, 0, 0, 0, 1000, 0, 0, 0, 0])

    game.start_hand()
    game.perform_action(BettingAction.CALL)
    game.perform_action(BettingAction.CHECK)

    assert game.state == GameState.FLOP
    assert game.current_player is players[4]


def test_short_stacks_all_in_on_the_blinds_run_the_board_out():
    game, players = make_game([5, 10, 0, 0, 0, 0, 0, 0, 0])

    game.start_hand()

    assert game.state == GameState.SHOWDOWN
    assert len(game.community_cards) == 5

    game.complete_hand()

    assert sum(player.chips for player in players) == 15
    assert game.state == GameState.HAND_COMPLETE


# ------------------------------------------------------------- betting state


def test_start_hand_clears_acted_players_from_previous_hand():
    game, players = make_game()
    game.start_hand()
    fold_everyone_out(game)
    game.reset_hand()

    game.acted_players = set(players)
    game.start_hand()

    assert game.acted_players == set()
    assert game.is_betting_round_complete() is False


def test_last_player_with_chips_must_still_answer_an_all_in():
    game, players = make_game([1000, 50, 1000, 0, 0, 0, 0, 0, 0])

    game.start_hand()
    # Dealer P0 acts first heads-up-plus-one: P0 dealer, P1 SB, P2 BB.
    assert game.current_player is players[0]
    game.perform_action(BettingAction.ALL_IN)
    game.perform_action(BettingAction.ALL_IN)  # P1 (50 chips) shoves too

    assert game.state == GameState.PRE_FLOP
    assert game.current_player is players[2]
    assert game.is_betting_round_complete() is False


def test_board_is_run_out_when_only_one_player_can_still_bet():
    game, players = make_game([50, 1000, 1000, 0, 0, 0, 0, 0, 0])

    game.start_hand()
    game.perform_action(BettingAction.ALL_IN)   # P0 (dealer) all-in for 50
    game.perform_action(BettingAction.CALL)     # P1 calls
    game.perform_action(BettingAction.FOLD)     # P2 folds the big blind

    assert game.state == GameState.SHOWDOWN
    assert len(game.community_cards) == 5


def test_perform_action_requires_a_betting_state():
    game, _ = make_game()

    with pytest.raises(ValueError):
        game.perform_action(BettingAction.FOLD)


def test_invalid_actions_do_not_change_game_state():
    game, players = make_game()
    game.start_hand()

    before = (
        game.pot.amount,
        dict(game.pot.contributions),
        [(p.chips, p.folded, p.all_in) for p in players],
        game.current_player,
    )

    for action, amount in (
        (BettingAction.CHECK, None),
        (BettingAction.RAISE, -5),
        (BettingAction.RAISE, 10 ** 9),
        (BettingAction.RAISE, 1),
        (BettingAction.BET, 5),
    ):
        with pytest.raises(ValueError):
            game.perform_action(action, amount)

    after = (
        game.pot.amount,
        dict(game.pot.contributions),
        [(p.chips, p.folded, p.all_in) for p in players],
        game.current_player,
    )

    assert before == after


# -------------------------------------------------------------- betting rules


def test_bet_below_minimum_is_rejected_unless_all_in():
    betting_round = BettingRound()
    betting_round.minimum_bet = 20
    pot = Pot()
    player = Player("A", 500)

    with pytest.raises(ValueError):
        betting_round.bet(player, pot, 5)

    short = Player("B", 5)
    betting_round.bet(short, pot, 5)

    assert short.all_in is True


def test_bet_sets_the_minimum_raise_to_the_bet_size():
    betting_round = BettingRound()
    betting_round.minimum_bet = 20
    pot = Pot()

    betting_round.bet(Player("A", 500), pot, 60)

    assert betting_round.current_bet == 60
    assert betting_round.min_raise_amount == 60


def test_short_all_in_does_not_create_a_zero_chip_raise():
    betting_round = BettingRound()
    betting_round.minimum_bet = 20
    pot = Pot()
    short = Player("short", 5)
    other = Player("other", 500)

    betting_round.all_in(short, pot)

    assert betting_round.current_bet == 5
    assert betting_round.min_raise_amount == 20

    actions = betting_round.get_legal_actions(other, pot)

    assert BettingAction.RAISE in actions
    assert betting_round.can_raise(other, pot, 0) is False


def test_full_all_in_raise_updates_minimum_raise():
    betting_round = BettingRound()
    betting_round.minimum_bet = 20
    pot = Pot()

    betting_round.bet(Player("A", 500), pot, 20)
    betting_round.all_in(Player("B", 100), pot)

    assert betting_round.current_bet == 100
    assert betting_round.min_raise_amount == 80


# ----------------------------------------------------------------- side pots


def test_side_pots_layer_by_all_in_amounts():
    pot = Pot()
    short, middle, deep, folder = (
        Player("short", 100),
        Player("middle", 300),
        Player("deep", 1000),
        Player("folder", 1000),
    )

    pot.add_bet(short, 100)
    pot.add_bet(middle, 300)
    pot.add_bet(deep, 500)
    pot.add_bet(folder, 50)
    folder.fold()

    pots, refunds = pot.build_side_pots([short, middle, deep])

    assert pots == [
        (350, [short, middle, deep]),
        (400, [middle, deep]),
        (200, [deep]),
    ]
    assert refunds == {}
    assert sum(amount for amount, _ in pots) == pot.amount


def test_side_pots_without_all_ins_is_a_single_pot():
    pot = Pot()
    players = [Player(f"p{i}", 500) for i in range(3)]

    for player in players:
        pot.add_bet(player, 100)

    pots, refunds = pot.build_side_pots(players)

    assert pots == [(300, players)]
    assert refunds == {}


def test_chips_nobody_can_win_are_refunded():
    pot = Pot()
    eligible = Player("eligible", 500)
    other = Player("other", 500)

    pot.add_bet(eligible, 100)
    pot.add_bet(other, 300)

    pots, refunds = pot.build_side_pots([eligible])

    assert pots == [(200, [eligible])]
    assert refunds == {other: 200}


def test_unattributed_pot_chips_go_to_the_main_pot():
    pot = Pot()
    players = [Player("a", 10), Player("b", 10)]
    pot.amount = 50

    pots, refunds = pot.build_side_pots(players)

    assert pots == [(50, players)]


def test_showdown_pays_main_and_side_pots_to_the_right_players():
    game, players = make_game([100, 300, 1000, 1000] + [1000] * 5)
    short, middle, deep, folder = players[:4]

    game.community_cards = [
        card(Rank.TWO, Suit.CLUBS),
        card(Rank.SEVEN, Suit.DIAMONDS),
        card(Rank.NINE, Suit.SPADES),
        card(Rank.FOUR, Suit.HEARTS),
        card(Rank.THREE, Suit.DIAMONDS),
    ]
    short.hand = [card(Rank.ACE, Suit.CLUBS), card(Rank.ACE, Suit.DIAMONDS)]
    middle.hand = [card(Rank.KING, Suit.CLUBS), card(Rank.KING, Suit.DIAMONDS)]
    deep.hand = [card(Rank.QUEEN, Suit.CLUBS), card(Rank.QUEEN, Suit.DIAMONDS)]

    game.pot.add_bet(short, 100)
    game.pot.add_bet(middle, 300)
    game.pot.add_bet(deep, 500)
    game.pot.add_bet(folder, 50)
    folder.fold()
    for other in players[4:]:
        other.fold()

    game.state = GameState.SHOWDOWN
    winners = game.complete_hand()

    assert winners == [short, middle, deep]
    assert short.chips == 350        # wins the main pot
    assert middle.chips == 400       # wins the side pot with the second best hand
    assert deep.chips == 500 + 200   # keeps the uncontested part of their bet
    assert folder.chips == 950
    assert game.pot.amount == 0
    assert [p["label"] for p in game.last_result["pots"]] == [
        "Main pot", "Side pot 1", "Side pot 2",
    ]


def test_tie_for_side_pot_splits_it():
    game, players = make_game()

    game.community_cards = [
        card(Rank.TEN, Suit.HEARTS),
        card(Rank.JACK, Suit.DIAMONDS),
        card(Rank.QUEEN, Suit.CLUBS),
        card(Rank.KING, Suit.SPADES),
        card(Rank.ACE, Suit.HEARTS),
    ]
    for player, (a, b) in zip(players[:3], [
        (Rank.TWO, Rank.THREE), (Rank.FOUR, Rank.FIVE), (Rank.SIX, Rank.SEVEN)
    ]):
        player.hand = [card(a, Suit.CLUBS), card(b, Suit.DIAMONDS)]
        game.pot.add_bet(player, 100)
    for other in players[3:]:
        other.fold()

    game.state = GameState.SHOWDOWN
    game.complete_hand()

    # Everyone plays the board straight, so the pot is split three ways.
    assert [p.chips for p in players[:3]] == [1000, 1000, 1000]


# -------------------------------------------------------------------- blinds


def test_blinds_increase_after_configured_number_of_hands():
    game, _ = make_game(hands_per_level=2)

    game.start_hand()
    fold_everyone_out(game)
    game.reset_hand()
    assert game.get_blind_amounts() == (10, 20)

    game.start_hand()
    fold_everyone_out(game)
    game.reset_hand()
    assert game.get_blind_amounts() == (15, 30)
    assert game.get_blind_level() == 2


def test_blinds_stop_at_the_last_level():
    game, _ = make_game(blind_levels=[(5, 10), (10, 20)], hands_per_level=1)

    for _ in range(4):
        game.start_hand()
        fold_everyone_out(game)
        game.reset_hand()

    assert game.get_blind_amounts() == (10, 20)


@pytest.mark.parametrize("levels", [[], [(20, 10)], [(0, 10)], [(-5, 10)]])
def test_invalid_blind_levels_are_rejected(levels):
    players = [Player(f"P{i}", 1000) for i in range(9)]

    with pytest.raises(ValueError):
        PokerGame(players, blind_levels=levels)


def test_hands_per_level_must_be_positive():
    players = [Player(f"P{i}", 1000) for i in range(9)]

    with pytest.raises(ValueError):
        PokerGame(players, hands_per_level=0)


# --------------------------------------------------------------- human input


def feed_inputs(monkeypatch, *answers):
    inputs = iter(answers)
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))


def test_human_turn_recovers_from_invalid_commands(monkeypatch, capsys):
    game, _ = make_game()
    game.start_hand()
    player = game.current_player
    feed_inputs(monkeypatch, "banana", "", "check", "call")

    game.human_turn()

    assert game.pot.get_contribution(player) == 20
    output = capsys.readouterr().out
    assert "Invalid action" in output
    assert "check is not currently a legal action" in output


def test_human_turn_rejects_bad_raise_amounts_then_accepts_valid_one(
    monkeypatch, capsys
):
    game, _ = make_game()
    game.start_hand()
    feed_inputs(
        monkeypatch,
        "raise", "abc",
        "raise", "5",
        "raise", "-10",
        "raise", "99999",
        "raise", "40",
    )

    game.human_turn()

    assert game.betting_round.current_bet == 60
    output = capsys.readouterr().out
    assert "whole number" in output
    assert "Amount must be between" in output


def test_human_turn_accepts_raise_with_amount_on_one_line(monkeypatch):
    game, _ = make_game()
    game.start_hand()
    feed_inputs(monkeypatch, "raise 40")

    game.human_turn()

    assert game.betting_round.current_bet == 60


def test_c_means_call_when_checking_is_not_allowed(monkeypatch):
    game, _ = make_game()
    game.start_hand()
    player = game.current_player
    feed_inputs(monkeypatch, "c")

    game.human_turn()

    assert game.pot.get_contribution(player) == 20


def test_probability_request_does_not_use_up_the_turn(monkeypatch, capsys):
    game, _ = make_game()
    game.start_hand()
    player = game.current_player
    feed_inputs(monkeypatch, "p", "fold")

    game.human_turn()

    assert player.folded is True
    assert "Win:" in capsys.readouterr().out


def test_human_can_quit(monkeypatch):
    game, _ = make_game()
    game.start_hand()
    feed_inputs(monkeypatch, "q")

    with pytest.raises(QuitGame):
        game.human_turn()


def test_probability_report_handles_a_high_card_hand_on_the_river(capsys):
    game, players = make_game()
    game.start_hand()
    game.move_to_flop()
    game.move_to_turn()
    game.move_to_river()
    players[0].hand = [card(Rank.TWO, Suit.CLUBS), card(Rank.FOUR, Suit.HEARTS)]
    game.community_cards = [
        card(Rank.SEVEN, Suit.CLUBS),
        card(Rank.NINE, Suit.DIAMONDS),
        card(Rank.JACK, Suit.SPADES),
        card(Rank.KING, Suit.HEARTS),
        card(Rank.THREE, Suit.DIAMONDS),
    ]

    game.display_probability_report()

    output = capsys.readouterr().out
    assert "High Card" in output
    assert "Win:" in output


def test_hand_result_is_reported_after_showdown(capsys):
    game, players = make_game()
    game.start_hand()
    game.move_to_flop()
    game.move_to_turn()
    game.move_to_river()
    game.move_to_showdown()
    for player in players[2:]:
        player.fold()

    game.complete_hand()
    game.display_hand_result()

    output = capsys.readouterr().out
    assert "SHOWDOWN" in output
    assert "wins" in output or "split" in output


def test_bot_situation_never_exposes_other_players_cards():
    game, players = make_game()
    game.start_hand()
    bot_player = game.current_player

    situation = game.get_bot_situation(bot_player)

    assert situation["hole_cards"] == bot_player.hand
    others = {
        id(c) for p in players if p is not bot_player for c in p.hand
    }
    seen = {id(c) for c in situation["hole_cards"] + situation["community_cards"]}
    assert not (others & seen)
