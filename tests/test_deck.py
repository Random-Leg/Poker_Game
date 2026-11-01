import pytest

from deck import Deck


def test_new_deck_has_52_cards():
    deck = Deck()

    assert len(deck) == 52


def test_deck_contains_52_unique_ids():
    deck = Deck()

    ids = [card.card_id for card in deck.cards]

    assert len(ids) == 52
    assert len(set(ids)) == 52


def test_deck_contains_ids_zero_to_51():
    deck = Deck()

    ids = [card.card_id for card in deck.cards]

    assert set(ids) == set(range(52))


def test_deck_has_13_cards_of_each_suit():
    deck = Deck()

    suits = [card.suit for card in deck.cards]

    for suit in set(suits):
        assert suits.count(suit) == 13


def test_deck_has_4_cards_of_each_rank():
    deck = Deck()

    ranks = [card.rank for card in deck.cards]

    for rank in set(ranks):
        assert ranks.count(rank) == 4


def test_drawing_card_reduces_deck_size():
    deck = Deck()

    deck.draw()

    assert len(deck) == 51


def test_drawn_card_is_removed():
    deck = Deck()

    card = deck.draw()

    assert card not in deck.cards


def test_drawing_all_cards_leaves_empty_deck():
    deck = Deck()

    for _ in range(52):
        deck.draw()

    assert len(deck) == 0


def test_drawing_from_empty_deck_raises_error():
    deck = Deck()

    for _ in range(52):
        deck.draw()

    with pytest.raises(ValueError):
        deck.draw()