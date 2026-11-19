"""Requirement group 1: cards and deck."""
import pytest

from card import Card, Rank, Suit
from deck import Deck


def snapshot(deck):
    return sorted((c.card_id, c.suit, c.rank) for c in deck.cards)


def test_new_deck_has_52_unique_cards():
    # 1.1 every suit/rank combination once, IDs 0 to 51
    deck = Deck()
    assert len(deck) == 52
    assert {c.card_id for c in deck.cards} == set(range(52))
    assert {(c.suit, c.rank) for c in deck.cards} == {(s, r) for s in Suit for r in Rank}


@pytest.mark.parametrize("card_id", [-1, 52, 100])
def test_card_id_outside_0_to_51_is_rejected(card_id):
    # 1.2 boundary values: 0 and 51 are the last valid IDs
    Card(0, Suit.HEARTS, Rank.TWO)
    Card(51, Suit.SPADES, Rank.ACE)
    with pytest.raises(ValueError):
        Card(card_id, Suit.HEARTS, Rank.TWO)


def test_shuffle_only_reorders_and_keeps_every_card_unchanged():
    # 1.2 and 1.3 same 52 cards, same ID/suit/rank, none added or lost
    deck = Deck()
    before = snapshot(deck)
    order_before = [c.card_id for c in deck.cards]
    deck.shuffle()
    assert snapshot(deck) == before
    assert [c.card_id for c in deck.cards] != order_before


def test_draw_removes_one_card_and_never_repeats():
    # 1.4 each draw returns a card and shrinks the deck by one
    deck = Deck()
    deck.shuffle()
    drawn = []
    for expected_size in range(51, -1, -1):
        drawn.append(deck.draw())
        assert len(deck) == expected_size
    assert len({c.card_id for c in drawn}) == 52


def test_draw_from_empty_deck_raises():
    # 1.5
    deck = Deck()
    for _ in range(52):
        deck.draw()
    with pytest.raises(ValueError):
        deck.draw()
