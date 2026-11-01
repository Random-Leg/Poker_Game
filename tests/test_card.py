import pytest

from card import Card, Rank, Suit


def test_card_has_correct_id():
    card = Card(12, Suit.HEARTS, Rank.ACE)

    assert card.card_id == 12


def test_card_has_correct_rank():
    card = Card(12, Suit.HEARTS, Rank.ACE)

    assert card.rank == Rank.ACE


def test_card_has_correct_suit():
    card = Card(12, Suit.HEARTS, Rank.ACE)

    assert card.suit == Suit.HEARTS


def test_card_string():
    card = Card(12, Suit.HEARTS, Rank.ACE)

    assert str(card) == "ACE of Hearts"


def test_card_id_cannot_be_below_zero():
    with pytest.raises(ValueError):
        Card(-1, Suit.HEARTS, Rank.ACE)


def test_card_id_cannot_be_above_51():
    with pytest.raises(ValueError):
        Card(52, Suit.HEARTS, Rank.ACE)

def test_card_short_form():
    assert Card(12, Suit.HEARTS, Rank.ACE).short() == "A\u2665"
    assert Card(1, Suit.SPADES, Rank.TEN).short() == "10\u2660"
    assert Card(2, Suit.CLUBS, Rank.TWO).short() == "2\u2663"
    assert Card(3, Suit.DIAMONDS, Rank.QUEEN).short() == "Q\u2666"
