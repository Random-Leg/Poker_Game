import pytest
from player import Player
from pot import Pot


def test_new_pot_is_empty():
    pot = Pot()

    assert pot.amount == 0
    assert pot.contributions == {}

def test_player_can_contribute_to_pot():
    player = Player("Alice", 1000)
    pot = Pot()

    pot.add_bet(player, 100)

    assert player.chips == 900
    assert pot.amount == 100
    assert pot.get_contribution(player) == 100

def test_multiple_players_can_contribute():
    player_one = Player("Alice", 1000)
    player_two = Player("Bob", 1000)

    pot = Pot()

    pot.add_bet(player_one, 100)
    pot.add_bet(player_two, 200)

    assert player_one.chips == 900
    assert player_two.chips == 800

    assert pot.amount == 300

    assert pot.get_contribution(player_one) == 100
    assert pot.get_contribution(player_two) == 200

def test_player_can_contribute_multiple_times():
    player = Player("Alice", 1000)
    pot = Pot()

    pot.add_bet(player, 50)
    pot.add_bet(player, 100)

    assert player.chips == 850
    assert pot.amount == 150
    assert pot.get_contribution(player) == 150

def test_zero_contribution_is_rejected():
    player = Player("Alice", 1000)
    pot = Pot()

    try:
        pot.add_bet(player, 0)
        assert False
    except ValueError:
        pass

def test_negative_contribution_is_rejected():
    player = Player("Alice", 1000)
    pot = Pot()

    try:
        pot.add_bet(player, -50)
        assert False
    except ValueError:
        pass

def test_player_cannot_contribute_more_chips_than_they_have():
    player = Player("Alice", 100)
    pot = Pot()

    try:
        pot.add_bet(player, 101)
        assert False
    except ValueError:
        pass

def test_player_can_contribute_all_chips():
    player = Player("Alice", 100)
    pot = Pot()

    pot.add_bet(player, 100)

    assert player.chips == 0
    assert player.all_in is True
    assert pot.amount == 100
    assert pot.get_contribution(player) == 100

def test_pot_can_be_awarded_to_player():
    player_one = Player("Alice", 1000)
    player_two = Player("Bob", 1000)

    pot = Pot()

    pot.add_bet(player_one, 100)
    pot.add_bet(player_two, 100)

    assert pot.amount == 200

    pot.award(player_one)

    assert player_one.chips == 1100
    assert player_two.chips == 900
    assert pot.amount == 0

def test_awarding_pot_clears_contributions():
    player_one = Player("Alice", 1000)
    player_two = Player("Bob", 1000)

    pot = Pot()

    pot.add_bet(player_one, 100)
    pot.add_bet(player_two, 200)

    pot.award(player_one)

    assert pot.amount == 0
    assert pot.contributions == {}
    assert pot.get_contribution(player_one) == 0
    assert pot.get_contribution(player_two) == 0

def test_zero_contribution_is_rejected():
    player = Player("Alice", 1000)
    pot = Pot()

    with pytest.raises(ValueError):
        pot.add_bet(player, 0)

def test_folded_player_cannot_contribute():
    player = Player("Alice", 1000)
    pot = Pot()

    player.fold()

    with pytest.raises(ValueError):
        pot.add_bet(player, 100)

    assert player.chips == 1000
    assert pot.amount == 0
    assert pot.get_contribution(player) == 0