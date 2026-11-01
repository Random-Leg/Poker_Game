import pytest
from card import Card, Suit, Rank
from game import PokerGame, GameState
from player import Player
from betting import BettingAction
from pot import Pot

def create_players():
    return [
        Player(f"Player {i}", 1000)
        for i in range(9)
    ]

def test_game_requires_exactly_nine_players():
    players = create_players()[:8]

    with pytest.raises(ValueError):
        PokerGame(players)

def test_game_requires_unique_player_names():
    players = create_players()
    players[1].name = players[0].name

    with pytest.raises(ValueError):
        PokerGame(players)

def test_game_starts_in_new_hand_state():
    game = PokerGame(create_players())

    assert game.state == GameState.NEW_HAND

def test_game_has_nine_players():
    game = PokerGame(create_players())

    assert len(game.players) == 9

def test_game_starts_with_empty_community_cards():
    game = PokerGame(create_players())

    assert game.community_cards == []

def test_game_starts_with_dealer_at_position_zero():
    game = PokerGame(create_players())

    assert game.dealer_position == 0

def test_first_player_is_initial_dealer():
    players = create_players()
    game = PokerGame(players)

    assert game.get_dealer() == players[0]

def test_start_hand_moves_to_pre_flop():
    game = PokerGame(create_players())

    game.start_hand()

    assert game.state == GameState.PRE_FLOP

def test_start_hand_gives_each_player_two_cards():
    game = PokerGame(create_players())

    game.start_hand()

    for player in game.players:
        assert len(player.hand) == 2

def test_start_hand_deals_18_cards():
    game = PokerGame(create_players())

    game.start_hand()

    total_cards = sum(len(player.hand) for player in game.players)

    assert total_cards == 18

def test_deck_has_34_cards_after_dealing_hole_cards():
    game = PokerGame(create_players())

    game.start_hand()

    assert len(game.deck) == 34

def test_all_dealt_cards_are_unique():
    game = PokerGame(create_players())

    game.start_hand()

    cards = []

    for player in game.players:
        cards.extend(player.hand)

    card_ids = [card.card_id for card in cards]

    assert len(card_ids) == len(set(card_ids))

def test_start_hand_clears_existing_player_hands():
    game = PokerGame(create_players())

    game.start_hand()

    for player in game.players:
        assert len(player.hand) == 2

    game.state = GameState.HAND_COMPLETE
    game.reset_hand()

    game.start_hand()

    for player in game.players:
        assert len(player.hand) == 2

def test_start_hand_resets_folded_status():
    game = PokerGame(create_players())

    game.players[0].fold()

    game.start_hand()

    assert game.players[0].folded is False

def test_start_hand_resets_all_in_status():
    game = PokerGame(create_players())

    game.players[0].all_in = True

    game.start_hand()

    assert game.players[0].all_in is False

def test_cannot_start_hand_twice():
    game = PokerGame(create_players())

    game.start_hand()

    with pytest.raises(ValueError):
        game.start_hand()

def test_deal_hole_cards_gives_two_cards_to_each_player():
    game = PokerGame(create_players())

    game.deal_hole_cards()

    for player in game.players:
        assert len(player.hand) == 2

def test_deal_hole_cards_uses_unique_cards():
    game = PokerGame(create_players())

    game.deal_hole_cards()

    cards = []

    for player in game.players:
        cards.extend(player.hand)

    card_ids = [card.card_id for card in cards]

    assert len(card_ids) == len(set(card_ids))

def test_move_dealer_moves_to_next_player():
    players = create_players()
    game = PokerGame(players)

    game.move_dealer()

    assert game.dealer_position == 1

def test_move_dealer_changes_dealer():
    players = create_players()
    game = PokerGame(players)

    first_dealer = game.get_dealer()

    game.move_dealer()

    second_dealer = game.get_dealer()

    assert first_dealer != second_dealer

def test_dealer_wraps_around_table():
    game = PokerGame(create_players())

    game.dealer_position = 8

    game.move_dealer()

    assert game.dealer_position == 0

def test_move_to_flop():
    game = PokerGame(create_players())

    game.start_hand()
    game.move_to_flop()

    assert game.state == GameState.FLOP

def test_move_to_turn():
    game = PokerGame(create_players())

    game.start_hand()
    game.move_to_flop()
    game.move_to_turn()

    assert game.state == GameState.TURN

def test_move_to_river():
    game = PokerGame(create_players())

    game.start_hand()
    game.move_to_flop()
    game.move_to_turn()
    game.move_to_river()

    assert game.state == GameState.RIVER

def test_move_to_showdown():
    game = PokerGame(create_players())

    game.start_hand()
    game.move_to_flop()
    game.move_to_turn()
    game.move_to_river()
    game.move_to_showdown()

    assert game.state == GameState.SHOWDOWN

def test_complete_hand():
    game = PokerGame(create_players())

    game.start_hand()
    game.move_to_flop()
    game.move_to_turn()
    game.move_to_river()
    game.move_to_showdown()
    game.complete_hand()

    assert game.state == GameState.HAND_COMPLETE

def test_cannot_move_to_flop_before_starting_hand():
    game = PokerGame(create_players())

    with pytest.raises(ValueError):
        game.move_to_flop()

def test_cannot_move_to_turn_before_flop():
    game = PokerGame(create_players())

    game.start_hand()

    with pytest.raises(ValueError):
        game.move_to_turn()

def test_cannot_move_to_river_before_turn():
    game = PokerGame(create_players())

    game.start_hand()
    game.move_to_flop()

    with pytest.raises(ValueError):
        game.move_to_river()

def test_cannot_showdown_before_river():
    game = PokerGame(create_players())

    game.start_hand()

    with pytest.raises(ValueError):
        game.move_to_showdown()

def test_cannot_complete_hand_before_showdown():
    game = PokerGame(create_players())

    game.start_hand()

    with pytest.raises(ValueError):
        game.complete_hand()

def test_advance_state_moves_through_entire_hand():
    game = PokerGame(create_players())

    game.advance_state()
    assert game.state == GameState.PRE_FLOP

    game.advance_state()
    assert game.state == GameState.FLOP

    game.advance_state()
    assert game.state == GameState.TURN

    game.advance_state()
    assert game.state == GameState.RIVER

    game.advance_state()
    assert game.state == GameState.SHOWDOWN

    game.advance_state()
    assert game.state == GameState.HAND_COMPLETE

def test_cannot_advance_after_hand_is_complete():
    game = PokerGame(create_players())

    for _ in range(6):
        game.advance_state()

    with pytest.raises(ValueError):
        game.advance_state()

def test_reset_hand_returns_to_new_hand():
    game = PokerGame(create_players())

    for _ in range(6):
        game.advance_state()

    game.reset_hand()

    assert game.state == GameState.NEW_HAND

def test_reset_hand_clears_player_hands():
    game = PokerGame(create_players())

    game.start_hand()

    for player in game.players:
        assert len(player.hand) == 2

    game.state = GameState.HAND_COMPLETE
    game.reset_hand()

    for player in game.players:
        assert len(player.hand) == 0

def test_reset_hand_clears_community_cards():
    game = PokerGame(create_players())

    game.community_cards.append("test")

    game.state = GameState.HAND_COMPLETE
    game.reset_hand()

    assert game.community_cards == []

def test_reset_hand_moves_dealer():
    game = PokerGame(create_players())

    game.state = GameState.HAND_COMPLETE

    game.reset_hand()

    assert game.dealer_position == 1

def test_reset_hand_dealer_wraps_around():
    game = PokerGame(create_players())

    game.dealer_position = 8
    game.state = GameState.HAND_COMPLETE

    game.reset_hand()

    assert game.dealer_position == 0

def test_cannot_reset_hand_before_completion():
    game = PokerGame(create_players())

    with pytest.raises(ValueError):
        game.reset_hand()

def test_player_with_zero_chips_is_not_active():
    players = create_players()
    game = PokerGame(players)

    players[3].chips = 0

    active = game.get_active_players()

    assert players[3] not in active
    assert len(active) == 8

def test_player_with_chips_remains_active():
    players = create_players()
    game = PokerGame(players)

    active = game.get_active_players()

    assert len(active) == 9

def test_flop_deals_three_community_cards():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()
    game.move_to_flop()

    assert len(game.community_cards) == 3


def test_turn_adds_one_community_card():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()
    game.move_to_flop()
    game.move_to_turn()

    assert len(game.community_cards) == 4


def test_river_adds_one_community_card():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()
    game.move_to_flop()
    game.move_to_turn()
    game.move_to_river()

    assert len(game.community_cards) == 5


def test_all_community_cards_are_unique():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()
    game.move_to_flop()
    game.move_to_turn()
    game.move_to_river()

    card_ids = [
        card.card_id
        for card in game.community_cards
    ]

    assert len(card_ids) == len(set(card_ids))


def test_community_cards_do_not_overlap_player_hands():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()
    game.move_to_flop()
    game.move_to_turn()
    game.move_to_river()

    player_card_ids = {
        card.card_id
        for player in players
        for card in player.hand
    }

    community_card_ids = {
        card.card_id
        for card in game.community_cards
    }

    assert player_card_ids.isdisjoint(community_card_ids)

def test_correct_number_of_cards_remain_after_river():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()
    game.move_to_flop()
    game.move_to_turn()
    game.move_to_river()

    assert len(game.deck) == 26

def test_small_blind_is_player_left_of_dealer():
    players = create_players()
    game = PokerGame(players)

    game.dealer_position = 0

    assert game.get_small_blind() == players[1]


def test_big_blind_is_two_positions_left_of_dealer():
    players = create_players()
    game = PokerGame(players)

    game.dealer_position = 0

    assert game.get_big_blind() == players[2]

def test_blinds_wrap_around_table():
    players = create_players()
    game = PokerGame(players)

    game.dealer_position = 8

    assert game.get_small_blind() == players[0]
    assert game.get_big_blind() == players[1]

def test_small_blind_skips_eliminated_player():
    players = create_players()
    game = PokerGame(players)

    players[1].chips = 0
    game.dealer_position = 0

    assert game.get_small_blind() == players[2]


def test_big_blind_skips_eliminated_players():
    players = create_players()
    game = PokerGame(players)

    players[1].chips = 0
    players[2].chips = 0
    game.dealer_position = 0

    assert game.get_big_blind() == players[4]

def test_initial_blind_amounts():
    players = create_players()
    game = PokerGame(players)

    assert game.get_blind_amounts() == (10, 20)

def test_post_blinds_adds_small_and_big_blind_to_pot():
    players = create_players()
    game = PokerGame(players)

    game.dealer_position = 0
    game.post_blinds()

    assert game.pot.amount == 30


def test_post_blinds_deducts_chips_from_players():
    players = create_players()
    game = PokerGame(players)

    game.dealer_position = 0
    game.post_blinds()

    assert players[1].chips == 990
    assert players[2].chips == 980


def test_post_blinds_records_contributions():
    players = create_players()
    game = PokerGame(players)

    game.dealer_position = 0
    game.post_blinds()

    assert game.pot.get_contribution(players[1]) == 10
    assert game.pot.get_contribution(players[2]) == 20


def test_post_blinds_skips_eliminated_players():
    players = create_players()
    game = PokerGame(players)

    players[1].chips = 0
    game.dealer_position = 0

    game.post_blinds()

    assert game.pot.get_contribution(players[2]) == 10
    assert game.pot.get_contribution(players[3]) == 20

def test_pre_flop_first_player_is_left_of_big_blind():
    players = create_players()
    game = PokerGame(players)

    game.dealer_position = 0

    assert game.get_first_to_act_pre_flop() == players[3]

def test_pre_flop_first_player_skips_eliminated_players():
    players = create_players()
    game = PokerGame(players)

    players[1].chips = 0
    game.dealer_position = 0

    assert game.get_first_to_act_pre_flop() == players[4]

def test_set_first_player_pre_flop():
    players = create_players()
    game = PokerGame(players)

    game.dealer_position = 0
    game.set_first_player_pre_flop()

    assert game.current_player == players[3]

def test_start_hand_sets_up_pre_flop():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    assert game.state == GameState.PRE_FLOP
    assert game.pot.amount == 30
    assert game.current_player == players[3]

def test_start_hand_sets_pre_flop_first_player_with_eliminated_player():
    players = create_players()
    game = PokerGame(players)

    players[1].chips = 0

    game.start_hand()

    assert game.current_player == players[4]

def test_get_next_player_skips_eliminated_players():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    players[4].chips = 0
    game.current_player = players[3]

    assert game.get_next_player() == players[5]


def test_get_next_player_skips_folded_players():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    players[4].fold()
    game.current_player = players[3]

    assert game.get_next_player() == players[5]


def test_get_next_player_wraps_around_table():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    game.current_player = players[8]

    assert game.get_next_player() == players[0]

def test_perform_action_fold():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    current_player = game.current_player

    game.perform_action(BettingAction.FOLD)

    assert current_player.folded is True
    assert game.current_player != current_player

def test_perform_action_call():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    game.perform_action(BettingAction.CALL)

    assert game.pot.get_contribution(game.players[3]) == 20
    assert game.current_player == game.players[4]

def test_post_blinds_sets_current_bet():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    assert game.betting_round.current_bet == 20

def test_pre_flop_player_can_call_big_blind():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    game.perform_action(BettingAction.CALL)

    assert game.pot.get_contribution(players[3]) == 20

def test_perform_action_raise():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    game.perform_action(BettingAction.RAISE, 20)

    assert game.betting_round.current_bet == 40
    assert game.pot.get_contribution(players[3]) == 40
    assert players[3].chips == 960
    assert game.current_player == players[4]

def test_raise_below_minimum_is_rejected():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    with pytest.raises(ValueError):
        game.perform_action(BettingAction.RAISE, 10)

def test_perform_action_all_in():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    game.perform_action(BettingAction.ALL_IN)

    assert players[3].chips == 0
    assert players[3].all_in is True
    assert game.pot.get_contribution(players[3]) == 1000

def test_all_in_moves_to_next_player():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    game.perform_action(BettingAction.ALL_IN)

    assert game.current_player == players[4]

def test_bet_requires_amount():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    with pytest.raises(ValueError):
        game.perform_action(BettingAction.BET)

def test_raise_requires_amount():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    with pytest.raises(ValueError):
        game.perform_action(BettingAction.RAISE)

def test_players_who_are_not_folded_or_all_in_can_act():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    assert len(game.get_players_who_can_act()) == 9

def test_folded_player_cannot_act():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    players[3].fold()

    assert players[3] not in game.get_players_who_can_act()

def test_all_in_player_cannot_act():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    players[3].all_in = True

    assert players[3] not in game.get_players_who_can_act()

def test_betting_round_is_not_complete_at_start():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    assert game.is_betting_round_complete() is False

def test_betting_round_completes_when_every_player_calls():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    for _ in range(8):
        game.perform_action(BettingAction.CALL)

    game.perform_action(BettingAction.CHECK)

    assert game.state == GameState.FLOP

def test_betting_round_completes_when_all_players_match_bet():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    for _ in range(8):
        game.perform_action(BettingAction.CALL)

    game.perform_action(BettingAction.CHECK)

    assert game.state == GameState.FLOP

def test_raise_reopens_betting_for_previous_players():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    first_player = game.current_player

    game.perform_action(BettingAction.CALL)

    second_player = game.current_player

    game.perform_action(BettingAction.CALL)

    third_player = game.current_player

    game.perform_action(BettingAction.RAISE, 20)

    assert first_player not in game.acted_players
    assert second_player not in game.acted_players
    assert third_player in game.acted_players

def test_betting_round_ends_when_only_one_player_can_act():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    for _ in range(8):
        game.perform_action(BettingAction.FOLD)

    assert game.is_betting_round_complete() is True

def test_betting_round_ends_when_players_are_all_in():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    all_in_player = game.current_player
    game.perform_action(BettingAction.ALL_IN)

    for _ in range(7):
        game.perform_action(BettingAction.FOLD)

    # The big blind still has to answer the all-in, so the round is not
    # over yet.
    assert game.is_betting_round_complete() is False
    assert game.current_player is game.get_big_blind()

    game.perform_action(BettingAction.FOLD)

    assert game.state == GameState.HAND_COMPLETE
    assert all_in_player.chips == 1000 + 30

def test_first_to_act_post_flop_is_left_of_dealer():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    assert game.get_first_to_act_post_flop() == players[1]

def test_first_to_act_post_flop_skips_eliminated_player():
    players = create_players()
    game = PokerGame(players)

    players[1].chips = 0

    game.start_hand()

    assert game.get_first_to_act_post_flop() == players[2]

def test_completed_pre_flop_moves_to_flop():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    for _ in range(8):
        game.perform_action(BettingAction.CALL)

    game.perform_action(BettingAction.CHECK)

    assert game.state == GameState.FLOP
    assert len(game.community_cards) == 3

def test_flop_starts_new_betting_round():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    for _ in range(8):
        game.perform_action(BettingAction.CALL)

    game.perform_action(BettingAction.CHECK)

    assert game.betting_round.current_bet == 0
    assert game.acted_players == set()
    assert game.current_player == players[1]

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

    if self.state != GameState.SHOWDOWN:
        self.start_new_betting_round()

def test_first_to_act_post_flop_skips_folded_player():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    players[1].fold()

    assert game.get_first_to_act_post_flop() == players[2]

def test_start_new_betting_round_resets_betting_state():
        players = create_players()
        game = PokerGame(players)

        game.start_hand()

        game.betting_round.current_bet = 40
        game.betting_round.minimum_raise = 20
        game.acted_players.add(players[3])

        game.start_new_betting_round()

        assert game.betting_round.current_bet == 0
        assert game.betting_round.minimum_raise == 0
        assert game.acted_players == set()
        assert game.current_player == players[1]

def test_get_players_remaining_in_hand():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    players[1].fold()
    players[2].fold()

    remaining = game.get_players_remaining_in_hand()

    assert len(remaining) == 7
    assert players[1] not in remaining
    assert players[2] not in remaining

def test_get_remaining_player():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    for player in players[1:]:
        player.fold()

    assert game.get_remaining_player() == players[0]

def test_get_remaining_player_requires_one_player():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    players[1].fold()

    with pytest.raises(ValueError):
        game.get_remaining_player()

def test_end_hand_by_fold_awards_pot():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    winner = players[0]

    for player in players[1:]:
        player.fold()

    pot_amount = game.pot.amount
    starting_chips = winner.chips

    result = game.end_hand_by_fold()

    assert result == winner
    assert winner.chips == starting_chips + pot_amount
    assert game.pot.amount == 0
    assert game.state == GameState.HAND_COMPLETE

def test_last_player_remaining_ends_hand():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    for _ in range(8):
        game.perform_action(BettingAction.FOLD)

    assert game.state == GameState.HAND_COMPLETE

def test_get_players_remaining_in_hand():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    players[1].fold()
    players[2].fold()

    remaining = game.get_players_remaining_in_hand()

    assert len(remaining) == 7
    assert players[1] not in remaining
    assert players[2] not in remaining


def test_get_remaining_player():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    for player in players[1:]:
        player.fold()

    assert game.get_remaining_player() == players[0]


def test_get_remaining_player_requires_one_player():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    players[1].fold()

    with pytest.raises(ValueError):
        game.get_remaining_player()


def test_end_hand_by_fold_awards_pot():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    winner = players[0]

    for player in players[1:]:
        player.fold()

    pot_amount = game.pot.amount
    starting_chips = winner.chips

    result = game.end_hand_by_fold()

    assert result == winner
    assert winner.chips == starting_chips + pot_amount
    assert game.pot.amount == 0
    assert game.state == GameState.HAND_COMPLETE


def test_last_player_remaining_ends_hand():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    for _ in range(8):
        game.perform_action(BettingAction.FOLD)

    assert game.state == GameState.HAND_COMPLETE

def test_all_in_players_are_not_players_who_can_act():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    for player in players:
        player.chips = 0
        player.all_in = True

    assert game.get_players_who_can_act() == []

def test_betting_round_complete_when_all_players_are_all_in():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    for player in players:
        player.chips = 0
        player.all_in = True

    assert game.is_betting_round_complete() is True

def test_add_all_in_bets_entire_stack():
    player = Player("Alice", 6)
    pot = Pot()

    amount = pot.add_all_in(player)

    assert amount == 6
    assert player.chips == 0
    assert player.all_in is True
    assert pot.amount == 6
    assert pot.get_contribution(player) == 6

def test_full_hand_reaches_showdown():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    # Pre-flop
    for _ in range(8):
        game.perform_action(BettingAction.CALL)

    game.perform_action(BettingAction.CHECK)

    assert game.state == GameState.FLOP
    assert len(game.community_cards) == 3

    # Flop
    players_to_act = len(game.get_players_who_can_act())

    for _ in range(players_to_act):
        game.perform_action(BettingAction.CHECK)

    assert game.state == GameState.TURN
    assert len(game.community_cards) == 4

    # Turn
    players_to_act = len(game.get_players_who_can_act())

    for _ in range(players_to_act):
        game.perform_action(BettingAction.CHECK)

    assert game.state == GameState.RIVER
    assert len(game.community_cards) == 5

    # River
    players_to_act = len(game.get_players_who_can_act())

    for _ in range(players_to_act):
        game.perform_action(BettingAction.CHECK)

    assert game.state == GameState.SHOWDOWN
    assert len(game.community_cards) == 5

def test_hand_ends_when_all_other_players_fold():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    for _ in range(8):
        game.perform_action(BettingAction.FOLD)

    assert game.state == GameState.HAND_COMPLETE
    assert game.pot.amount == 0

def test_display_game_state(capsys):
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    game.display_game_state()

    output = capsys.readouterr().out

    assert "State: pre_flop" in output
    assert "Pot: 30" in output
    assert "Current bet: 20" in output
    assert "Community cards:" in output
    assert "Players:" in output


def test_display_player_hand(capsys):
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    player = players[0]

    game.display_player_hand(player)

    output = capsys.readouterr().out

    assert f"{player.name}'s hand:" in output
    assert str(player.hand[0]) in output
    assert str(player.hand[1]) in output

def test_legal_actions_at_start_of_pre_flop():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    actions = game.betting_round.get_legal_actions(
        game.current_player,
        game.pot
    )

    assert BettingAction.FOLD in actions
    assert BettingAction.CALL in actions
    assert BettingAction.ALL_IN in actions
    assert BettingAction.CHECK not in actions

def test_parse_fold_action():
    game = PokerGame(create_players())
    assert game.parse_action("fold") == BettingAction.FOLD

def test_parse_short_fold_action():
    game = PokerGame(create_players())
    assert game.parse_action("f") == BettingAction.FOLD

def test_parse_check_action():
    game = PokerGame(create_players())
    assert game.parse_action("check") == BettingAction.CHECK

def test_parse_call_action():
    game = PokerGame(create_players())
    assert game.parse_action("call") == BettingAction.CALL

def test_parse_bet_action():
    game = PokerGame(create_players())
    assert game.parse_action("bet") == BettingAction.BET

def test_parse_raise_action():
    game = PokerGame(create_players())
    assert game.parse_action("raise") == BettingAction.RAISE

def test_parse_all_in_action():
    game = PokerGame(create_players())
    assert game.parse_action("all-in") == BettingAction.ALL_IN

def test_parse_action_is_case_insensitive():
    game = PokerGame(create_players())
    assert game.parse_action("CALL") == BettingAction.CALL

def test_parse_invalid_action():
    game = PokerGame(create_players())
    with pytest.raises(ValueError):
        game.parse_action("banana")

def test_human_turn_call(monkeypatch):
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "call"
    )

    current_player = game.current_player

    game.human_turn()

    assert game.pot.get_contribution(current_player) == 20
    assert game.current_player != current_player

def test_human_turn_raise(monkeypatch):
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    inputs = iter(["raise", "40"])

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(inputs)
    )

    game.human_turn()

    assert game.betting_round.current_bet == 60

def test_complete_hand_moves_from_showdown_to_hand_complete():
    players = [
        Player("Player 1", 1000),
        Player("Player 2", 1000),
        Player("Player 3", 1000),
        Player("Player 4", 1000),
        Player("Player 5", 1000),
        Player("Player 6", 1000),
        Player("Player 7", 1000),
        Player("Player 8", 1000),
        Player("Player 9", 1000),
    ]

    game = PokerGame(players)

    game.community_cards = [
        Card(0, Suit.HEARTS, Rank.TWO),
        Card(1, Suit.DIAMONDS, Rank.THREE),
        Card(2, Suit.CLUBS, Rank.EIGHT),
        Card(3, Suit.SPADES, Rank.NINE),
        Card(4, Suit.HEARTS, Rank.JACK),
    ]

    players[0].hand = [
        Card(5, Suit.CLUBS, Rank.ACE),
        Card(6, Suit.DIAMONDS, Rank.ACE),
    ]

    players[1].hand = [
        Card(7, Suit.CLUBS, Rank.KING),
        Card(8, Suit.DIAMONDS, Rank.KING),
    ]

    for player in players[2:]:
        player.folded = True

    game.pot.amount = 200
    game.state = GameState.SHOWDOWN

    winners = game.complete_hand()

    assert winners == [players[0]]
    assert game.state == GameState.HAND_COMPLETE

def test_complete_hand_only_allowed_from_showdown():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    with pytest.raises(ValueError):
        game.complete_hand()

def test_reset_hand_sets_state_to_new_hand():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()
    game.state = GameState.HAND_COMPLETE

    game.reset_hand()

    assert game.state == GameState.NEW_HAND

def test_start_hand_creates_new_pot():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    first_pot = game.pot

    game.state = GameState.HAND_COMPLETE
    game.reset_hand()
    game.start_hand()

    assert game.pot is not first_pot
    assert game.pot.amount == 30

def test_start_hand_shuffles_new_deck():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    assert len(game.deck) == 34

def test_all_in_players_automatically_advance_to_showdown():
    players = create_players()
    game = PokerGame(players)

    game.start_hand()

    for player in game.get_active_players():
        if player != game.current_player:
            player.all_in = True

    game.perform_action(BettingAction.ALL_IN)

    assert game.state == GameState.SHOWDOWN

def test_determine_winner():
    players = [
        Player("Player 1", 1000),
        Player("Player 2", 1000),
        Player("Player 3", 1000),
        Player("Player 4", 1000),
        Player("Player 5", 1000),
        Player("Player 6", 1000),
        Player("Player 7", 1000),
        Player("Player 8", 1000),
        Player("Player 9", 1000),
    ]

    game = PokerGame(players)

    game.community_cards = [
        Card(0, Suit.HEARTS, Rank.NINE),
        Card(1, Suit.DIAMONDS, Rank.THREE),
        Card(2, Suit.CLUBS, Rank.FOUR),
        Card(3, Suit.SPADES, Rank.FIVE),
        Card(4, Suit.HEARTS, Rank.SIX),
    ]

    players[0].hand = [
        Card(5, Suit.CLUBS, Rank.ACE),
        Card(6, Suit.DIAMONDS, Rank.ACE),
    ]

    players[1].hand = [
        Card(7, Suit.CLUBS, Rank.KING),
        Card(8, Suit.DIAMONDS, Rank.KING),
    ]

    for player in players[2:]:
        player.folded = True

    winners = game.determine_winners()

    assert winners == [players[0]]

def test_determine_winner_tie():
    players = [
        Player("Player 1", 1000),
        Player("Player 2", 1000),
        Player("Player 3", 1000),
        Player("Player 4", 1000),
        Player("Player 5", 1000),
        Player("Player 6", 1000),
        Player("Player 7", 1000),
        Player("Player 8", 1000),
        Player("Player 9", 1000),
    ]

    game = PokerGame(players)

    game.community_cards = [
        Card(0, Suit.HEARTS, Rank.TEN),
        Card(1, Suit.DIAMONDS, Rank.JACK),
        Card(2, Suit.CLUBS, Rank.QUEEN),
        Card(3, Suit.SPADES, Rank.KING),
        Card(4, Suit.HEARTS, Rank.ACE),
    ]

    players[0].hand = [
        Card(5, Suit.CLUBS, Rank.TWO),
        Card(6, Suit.DIAMONDS, Rank.THREE),
    ]

    players[1].hand = [
        Card(7, Suit.CLUBS, Rank.FOUR),
        Card(8, Suit.DIAMONDS, Rank.FIVE),
    ]

    for player in players[2:]:
        player.folded = True

    winners = game.determine_winners()

    assert winners == [players[0], players[1]]

def test_complete_hand_awards_pot_to_single_winner():
    players = [
        Player("Player 1", 1000),
        Player("Player 2", 1000),
        Player("Player 3", 1000),
        Player("Player 4", 1000),
        Player("Player 5", 1000),
        Player("Player 6", 1000),
        Player("Player 7", 1000),
        Player("Player 8", 1000),
        Player("Player 9", 1000),
    ]

    game = PokerGame(players)

    game.community_cards = [
        Card(0, Suit.HEARTS, Rank.TWO),
        Card(1, Suit.DIAMONDS, Rank.THREE),
        Card(2, Suit.CLUBS, Rank.EIGHT),
        Card(3, Suit.SPADES, Rank.NINE),
        Card(4, Suit.HEARTS, Rank.JACK),
    ]

    players[0].hand = [
        Card(5, Suit.CLUBS, Rank.ACE),
        Card(6, Suit.DIAMONDS, Rank.ACE),
    ]

    players[1].hand = [
        Card(7, Suit.CLUBS, Rank.KING),
        Card(8, Suit.DIAMONDS, Rank.KING),
    ]

    for player in players[2:]:
        player.folded = True

    game.pot.amount = 200
    game.state = GameState.SHOWDOWN

    winners = game.complete_hand()

    assert winners == [players[0]]
    assert players[0].chips == 1200
    assert players[1].chips == 1000
    assert game.pot.amount == 0
    assert game.state == GameState.HAND_COMPLETE

def test_complete_hand_splits_pot_between_tied_winners():
    players = [
        Player("Player 1", 1000),
        Player("Player 2", 1000),
        Player("Player 3", 1000),
        Player("Player 4", 1000),
        Player("Player 5", 1000),
        Player("Player 6", 1000),
        Player("Player 7", 1000),
        Player("Player 8", 1000),
        Player("Player 9", 1000),
    ]

    game = PokerGame(players)

    game.community_cards = [
        Card(0, Suit.HEARTS, Rank.TEN),
        Card(1, Suit.DIAMONDS, Rank.JACK),
        Card(2, Suit.CLUBS, Rank.QUEEN),
        Card(3, Suit.SPADES, Rank.KING),
        Card(4, Suit.HEARTS, Rank.ACE),
    ]

    players[0].hand = [
        Card(5, Suit.CLUBS, Rank.TWO),
        Card(6, Suit.DIAMONDS, Rank.THREE),
    ]

    players[1].hand = [
        Card(7, Suit.CLUBS, Rank.FOUR),
        Card(8, Suit.DIAMONDS, Rank.FIVE),
    ]

    for player in players[2:]:
        player.folded = True

    game.pot.amount = 201
    game.state = GameState.SHOWDOWN

    winners = game.complete_hand()

    assert winners == [players[0], players[1]]
    # The odd chip goes to the winner closest to the left of the dealer
    # (the dealer is players[0]).
    assert players[0].chips == 1100
    assert players[1].chips == 1101
    assert game.pot.amount == 0
    assert game.state == GameState.HAND_COMPLETE

def test_get_probability_report_from_flop():
    players = [
        Player(f"Player {i}", 1000)
        for i in range(1, 10)
    ]

    game = PokerGame(players)
    game.start_hand()

    game.move_to_flop()

    game.start_new_betting_round()

    report = game.get_probability_report()

    assert "turn" in report
    assert "by_river" in report

    assert len(report["turn"]) == 9
    assert len(report["by_river"]) == 9


def test_get_probability_report_requires_flop_or_later():
    players = [
        Player(f"Player {i}", 1000)
        for i in range(1, 10)
    ]

    game = PokerGame(players)
    game.start_hand()

    with pytest.raises(ValueError):
        game.get_probability_report()


def test_get_probability_report_requires_current_player():
    players = [
        Player(f"Player {i}", 1000)
        for i in range(1, 10)
    ]

    game = PokerGame(players)
    game.start_hand()

    game.move_to_flop()

    game.current_player = None

    with pytest.raises(ValueError):
        game.get_probability_report()

def test_get_human_probability_report():
    players = [
        Player("You", 1000)
    ] + [
        Player(f"Player {i}", 1000)
        for i in range(2, 10)
    ]

    game = PokerGame(players)
    game.start_hand()

    game.move_to_flop()

    report = game.get_human_probability_report()

    assert "turn" in report
    assert "by_river" in report

    assert len(report["turn"]) == 9
    assert len(report["by_river"]) == 9

def test_get_human_probability_report_does_not_require_human_turn():
    players = [
        Player("You", 1000)
    ] + [
        Player(f"Player {i}", 1000)
        for i in range(2, 10)
    ]

    game = PokerGame(players)
    game.start_hand()

    game.move_to_flop()

    game.current_player = players[1]

    report = game.get_human_probability_report()

    assert "turn" in report
    assert "by_river" in report

def test_display_probability_report(capsys):
    players = [
        Player("You", 1000)
    ] + [
        Player(f"Player {i}", 1000)
        for i in range(2, 10)
    ]

    game = PokerGame(players)
    game.start_hand()

    game.move_to_flop()

    game.display_probability_report()

    captured = capsys.readouterr()

    assert "YOUR PROBABILITIES" in captured.out
    assert "One Pair" in captured.out
    assert "Two Pair" in captured.out
    assert "Three of a Kind" in captured.out
    assert "Straight" in captured.out
    assert "Flush" in captured.out
    assert "Full House" in captured.out
    assert "Four of a Kind" in captured.out
    assert "Straight Flush" in captured.out
    assert "Royal Flush" in captured.out

def test_parse_probability_command():
    players = [
        Player("You", 1000)
    ] + [
        Player(f"Player {i}", 1000)
        for i in range(2, 10)
    ]

    game = PokerGame(players)

    assert game.parse_command("p") == "probability"
    assert game.parse_command("P") == "probability"
    assert game.parse_command(" probability ") == "probability"


def test_parse_invalid_command():
    players = [
        Player("You", 1000)
    ] + [
        Player(f"Player {i}", 1000)
        for i in range(2, 10)
    ]

    game = PokerGame(players)

    with pytest.raises(ValueError):
        game.parse_command("xyz")