import pytest

from player import Player
from card import Card, Rank, Suit


def test_player_has_correct_name():
    player = Player("TestName", 1000)

    assert player.name == "TestName"


def test_player_has_correct_starting_chips():
    player = Player("TestName", 1000)

    assert player.chips == 1000


def test_player_starts_with_empty_hand():
    player = Player("TestName", 1000)

    assert player.hand == []


def test_player_starts_not_folded():
    player = Player("TestName", 1000)

    assert player.folded is False


def test_player_starts_not_all_in():
    player = Player("TestName", 1000)

    assert player.all_in is False


def test_player_can_receive_card():
    player = Player("TestName", 1000)
    card = Card(12, Rank.ACE, Suit.HEARTS)

    player.add_card(card)

    assert player.hand == [card]


def test_player_can_have_two_cards():
    player = Player("TestName", 1000)

    card1 = Card(12, Rank.ACE, Suit.HEARTS)
    card2 = Card(11, Rank.KING, Suit.SPADES)

    player.add_card(card1)
    player.add_card(card2)

    assert player.hand == [card1, card2]


def test_player_cannot_have_more_than_two_cards():
    player = Player("TestName", 1000)

    player.add_card(Card(0, Rank.TWO, Suit.HEARTS))
    player.add_card(Card(1, Rank.THREE, Suit.HEARTS))

    with pytest.raises(ValueError):
        player.add_card(Card(2, Rank.FOUR, Suit.HEARTS))


def test_player_can_fold():
    player = Player("TestName", 1000)

    player.fold()

    assert player.folded is True


def test_player_can_bet():
    player = Player("TestName", 1000)

    player.bet(200)

    assert player.chips == 800


def test_player_cannot_bet_zero():
    player = Player("TestName", 1000)

    with pytest.raises(ValueError):
        player.bet(0)


def test_player_cannot_bet_negative_amount():
    player = Player("TestName", 1000)

    with pytest.raises(ValueError):
        player.bet(-100)


def test_player_cannot_bet_more_chips_than_they_have():
    player = Player("TestName", 1000)

    with pytest.raises(ValueError):
        player.bet(1001)


def test_player_becomes_all_in_when_all_chips_are_bet():
    player = Player("TestName", 1000)

    player.bet(1000)

    assert player.chips == 0
    assert player.all_in is True


def test_player_cannot_start_with_negative_chips():
    with pytest.raises(ValueError):
        Player("TestName", -100)