from betting import BettingRound, BettingAction
from player import Player
from pot import Pot
import pytest


def test_new_betting_round_has_no_bet():
    betting = BettingRound()

    assert betting.current_bet == 0
    assert betting.minimum_raise == 0

def test_player_can_check_when_there_is_no_bet():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    assert betting.can_check(player, pot) is True

def test_player_cannot_check_when_behind_current_bet():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    pot.add_bet(player, 50)
    betting.current_bet = 100

    assert betting.can_check(player, pot) is False

def test_player_can_check_when_their_contribution_matches_current_bet():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    pot.add_bet(player, 100)
    betting.current_bet = 100

    assert betting.can_check(player, pot) is True

def test_folded_player_cannot_check():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    player.fold()

    assert betting.can_check(player, pot) is False

def test_all_in_player_cannot_check():
    player = Player("Alice", 100)
    betting = BettingRound()
    pot = Pot()

    pot.add_bet(player, 100)

    assert player.all_in is True
    assert betting.can_check(player, pot) is False

def test_player_can_call_when_behind_current_bet():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    pot.add_bet(player, 50)
    betting.current_bet = 100

    assert betting.can_call(player, pot) is True

def test_player_cannot_call_when_there_is_no_bet():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    assert betting.can_call(player, pot) is False

def test_player_cannot_call_when_contribution_matches_current_bet():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    pot.add_bet(player, 100)
    betting.current_bet = 100

    assert betting.can_call(player, pot) is False

def test_folded_player_cannot_call():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    player.fold()
    betting.current_bet = 100

    assert betting.can_call(player, pot) is False

def test_all_in_player_cannot_call():
    player = Player("Alice", 100)
    betting = BettingRound()
    pot = Pot()

    pot.add_bet(player, 100)
    betting.current_bet = 200

    assert betting.can_call(player, pot) is False

def test_player_can_bet_when_there_is_no_current_bet():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    assert betting.can_bet(player, pot) is True

def test_player_cannot_bet_when_there_is_already_a_bet():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    betting.current_bet = 100

    assert betting.can_bet(player, pot) is False

def test_folded_player_cannot_bet():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    player.fold()

    assert betting.can_bet(player, pot) is False

def test_all_in_player_cannot_bet():
    player = Player("Alice", 100)
    betting = BettingRound()
    pot = Pot()

    player.bet(100)

    assert betting.can_bet(player, pot) is False

def test_player_with_no_chips_cannot_bet():
    player = Player("Alice", 0)
    betting = BettingRound()
    pot = Pot()

    assert betting.can_bet(player, pot) is False

def test_player_can_go_all_in():
    player = Player("Alice", 1000)

    betting = BettingRound()

    assert betting.can_all_in(player) is True

def test_folded_player_cannot_go_all_in():
    player = Player("Alice", 1000)

    betting = BettingRound()
    player.fold()

    assert betting.can_all_in(player) is False

def test_already_all_in_player_cannot_go_all_in():
    player = Player("Alice", 1000)

    betting = BettingRound()
    player.bet(1000)

    assert betting.can_all_in(player) is False

def test_player_with_no_chips_cannot_go_all_in():
    player = Player("Alice", 0)

    betting = BettingRound()

    assert betting.can_all_in(player) is False

def test_player_can_raise():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    betting.current_bet = 50
    betting.minimum_raise = 50

    assert betting.can_raise(player, pot, 50) is True

def test_player_cannot_raise_when_there_is_no_bet():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    betting.current_bet = 0
    betting.minimum_raise = 50

    assert betting.can_raise(player, pot, 50) is False

def test_player_cannot_raise_by_less_than_minimum():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    betting.current_bet = 50
    betting.minimum_raise = 50

    assert betting.can_raise(player, pot, 25) is False

def test_player_cannot_raise_more_than_their_chips():
    player = Player("Alice", 30)
    betting = BettingRound()
    pot = Pot()

    betting.current_bet = 50
    betting.minimum_raise = 50

    assert betting.can_raise(player, pot, 50) is False

def test_folded_player_cannot_raise():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    player.fold()

    betting.current_bet = 50
    betting.minimum_raise = 50

    assert betting.can_raise(player, pot, 50) is False

def test_all_in_player_cannot_raise():
    player = Player("Alice", 100)
    betting = BettingRound()
    pot = Pot()

    player.bet(100)

    betting.current_bet = 50
    betting.minimum_raise = 50

    assert betting.can_raise(player, pot, 50) is False

def test_bet_reduces_player_chips():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    betting.bet(player, pot, 100)

    assert player.chips == 900

def test_bet_adds_money_to_pot():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    betting.bet(player, pot, 100)

    assert pot.amount == 100

def test_bet_sets_current_bet():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    betting.bet(player, pot, 100)

    assert betting.current_bet == 100

def test_bet_records_player_contribution():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    betting.bet(player, pot, 100)

    assert pot.get_contribution(player) == 100

def test_cannot_bet_when_there_is_already_a_bet():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    betting.current_bet = 50

    with pytest.raises(ValueError):
        betting.bet(player, pot, 100)

def test_call_matches_current_bet():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    pot.add_bet(player, 40)
    betting.current_bet = 100

    betting.call(player, pot)

    assert pot.get_contribution(player) == 100

def test_call_reduces_player_chips():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    pot.add_bet(player, 40)
    betting.current_bet = 100

    betting.call(player, pot)

    assert player.chips == 900

def test_call_adds_required_amount_to_pot():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    pot.add_bet(player, 40)
    betting.current_bet = 100

    betting.call(player, pot)

    assert pot.amount == 100

def test_cannot_call_when_there_is_no_bet():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    with pytest.raises(ValueError):
        betting.call(player, pot)

def test_raise_increases_current_bet():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    betting.current_bet = 50
    betting.minimum_raise = 50

    betting.raise_bet(player, pot, 50)

    assert betting.current_bet == 100

def test_raise_adds_correct_amount_to_player_contribution():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    pot.add_bet(player, 50)

    betting.current_bet = 50
    betting.minimum_raise = 50

    betting.raise_bet(player, pot, 50)

    assert pot.get_contribution(player) == 100

def test_raise_reduces_player_chips_correctly():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    pot.add_bet(player, 50)

    betting.current_bet = 50
    betting.minimum_raise = 50

    betting.raise_bet(player, pot, 50)

    assert player.chips == 900

def test_check_is_allowed_when_no_bet_exists():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    betting.check(player, pot)

def test_check_does_not_change_player_chips():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    betting.check(player, pot)

    assert player.chips == 1000

def test_check_does_not_change_pot():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    betting.check(player, pot)

    assert pot.amount == 0

def test_cannot_check_when_there_is_a_bet():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    betting.current_bet = 100

    with pytest.raises(ValueError):
        betting.check(player, pot)

def test_fold_marks_player_as_folded():
    player = Player("Alice", 1000)
    betting = BettingRound()

    betting.fold(player)

    assert player.folded is True

def test_cannot_fold_twice():
    player = Player("Alice", 1000)
    betting = BettingRound()

    betting.fold(player)

    with pytest.raises(ValueError):
        betting.fold(player)

def test_bet_records_player_contribution():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    betting.bet(player, pot, 100)

    assert pot.get_contribution(player) == 100

def test_player_must_have_enough_chips_for_full_raise():
    player = Player("Alice", 120)
    betting = BettingRound()
    pot = Pot()

    pot.add_bet(player, 20)

    betting.current_bet = 100
    betting.minimum_raise = 50

    assert betting.can_raise(player, pot, 50) is False

def test_raise_increases_current_bet():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    betting.current_bet = 50
    betting.minimum_raise = 50

    betting.raise_bet(player, pot, 50)

    assert betting.current_bet == 100

def test_raise_records_correct_contribution():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    pot.add_bet(player, 50)

    betting.current_bet = 50
    betting.minimum_raise = 50

    betting.raise_bet(player, pot, 50)

    assert pot.get_contribution(player) == 100

def test_raise_reduces_player_chips():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    pot.add_bet(player, 50)

    betting.current_bet = 50
    betting.minimum_raise = 50

    betting.raise_bet(player, pot, 50)

    assert player.chips == 900

def test_raise_updates_minimum_raise():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    betting.current_bet = 50
    betting.minimum_raise = 50

    betting.raise_bet(player, pot, 75)

    assert betting.minimum_raise == 75

def test_cannot_raise_below_minimum():
    player = Player("Alice", 1000)
    betting = BettingRound()
    pot = Pot()

    betting.current_bet = 50
    betting.minimum_raise = 50

    with pytest.raises(ValueError):
        betting.raise_bet(player, pot, 25)

def all_in(self, player, pot):
    if not self.can_all_in(player):
        raise ValueError("Player cannot go all-in")

    amount = player.chips

    pot.add_bet(player, amount)

    if amount > self.current_bet:
        self.current_bet = amount

def test_all_in_uses_all_player_chips():
    player = Player("Alice", 300)
    betting = BettingRound()
    pot = Pot()

    betting.all_in(player, pot)

    assert player.chips == 0

def test_all_in_marks_player_as_all_in():
    player = Player("Alice", 300)
    betting = BettingRound()
    pot = Pot()

    betting.all_in(player, pot)

    assert player.all_in is True

def test_all_in_adds_chips_to_pot():
    player = Player("Alice", 300)
    betting = BettingRound()
    pot = Pot()

    betting.all_in(player, pot)

    assert pot.amount == 300

def test_all_in_updates_current_bet_if_higher():
    player = Player("Alice", 300)
    betting = BettingRound()
    pot = Pot()

    betting.current_bet = 100

    betting.all_in(player, pot)

    assert betting.current_bet == 300

def test_short_all_in_does_not_lower_current_bet():
    player = Player("Alice", 60)
    betting = BettingRound()
    pot = Pot()

    betting.current_bet = 100

    betting.all_in(player, pot)

    assert betting.current_bet == 100

