"""Requirement group 5: hand evaluation."""
import random
from itertools import combinations

import pytest

from evaluator import HandRank, evaluate, evaluate_bruteforce
from helpers import card, cards

ALL_CARDS = [card(r + s) for r in "23456789TJQKA" for s in "HDCS"]

CATEGORY_HANDS = [
    ("AH KH QH JH TH", HandRank.ROYAL_FLUSH),
    ("9S 8S 7S 6S 5S", HandRank.STRAIGHT_FLUSH),
    ("7H 7D 7C 7S KD", HandRank.FOUR_OF_A_KIND),
    ("KH KD KC 4S 4D", HandRank.FULL_HOUSE),
    ("AH 9H 7H 4H 2H", HandRank.FLUSH),
    ("9H 8D 7C 6S 5D", HandRank.STRAIGHT),
    ("QH QD QC 8S 3D", HandRank.THREE_OF_A_KIND),
    ("JH JD 4C 4S AD", HandRank.TWO_PAIR),
    ("TH TD AC 8S 3D", HandRank.ONE_PAIR),
    ("AH JD 9C 5S 3D", HandRank.HIGH_CARD),
]


@pytest.mark.parametrize("hand, expected", CATEGORY_HANDS)
def test_each_of_the_ten_categories_is_recognised(hand, expected):
    # 5.1
    assert evaluate(cards(hand)).rank == expected


def test_categories_rank_in_the_correct_order():
    # 5.1 each example beats the next category down
    ranks = [evaluate(cards(hand)) for hand, _ in CATEGORY_HANDS]
    for stronger, weaker in zip(ranks, ranks[1:]):
        assert weaker < stronger


@pytest.mark.parametrize(
    "description, hole_and_board, expected",
    [
        ("five cards", "AH KH QH JH TH", HandRank.ROYAL_FLUSH),
        ("six cards, 2 hole cards used", "AH KH QH JH 2C TH", HandRank.ROYAL_FLUSH),
        ("board plays, 0 hole cards used", "2C 3D AH KH QH JH TH", HandRank.ROYAL_FLUSH),
        ("1 hole card used", "AH 3D 7S 7H 7D 2C KC", HandRank.THREE_OF_A_KIND),
        ("2 hole cards used", "7C 7S 7H 2D 9C KD 4S", HandRank.THREE_OF_A_KIND),
        ("seven cards hide a flush among pairs", "AH 2H 2D 2C 9H 4H KH", HandRank.FLUSH),
    ],
)
def test_best_five_of_five_six_or_seven_cards(description, hole_and_board, expected):
    # 5.2
    assert evaluate(cards(hole_and_board)).rank == expected


@pytest.mark.parametrize(
    "better, worse",
    [
        ("KH KD 5C 4S 2D", "QH QD AC JS TD"),          # pair: pair rank first
        ("AH AD 2C 2S 3D", "KH KD QC QS JD"),          # two pair: high pair first
        ("3H 3D 3C 2S 2D", "2H 2D 2C AS AD"),          # full house: trips first
        ("AH 9H 7H 4H 2H", "KH QH JH 9H 3H"),          # flush: highest card first
        ("9H 8D 7C 6S 5D", "8H 7D 6C 5S 4D"),          # straight: higher beats lower
        ("9H 9D 9C 9S 2D", "8H 8D 8C 8S AD"),          # four of a kind: rank first
        ("AH AD KC 5S 2D", "AC AS QC 5H 2H"),          # pair of aces: kicker K beats Q
    ],
)
def test_same_category_is_ordered_by_ranks_then_kickers(better, worse):
    # 5.3
    a, b = evaluate(cards(better)), evaluate(cards(worse))
    assert b < a and not a < b


def test_same_ranks_in_different_suits_tie():
    # 5.3
    assert evaluate(cards("KH KD QC QS 2D")) == evaluate(cards("KC KS QD QH 2S"))


def test_equal_hands_tie_including_when_the_sixth_and_seventh_card_differ():
    # 5.3 only the best five count: different 6th/7th cards must not break a tie
    first = evaluate(cards("AH AD KC QS JD 9C 2H"))
    second = evaluate(cards("AC AS KD QH JC 8D 3S"))
    assert first == second


def test_ace_is_low_only_in_the_wheel_and_the_wheel_is_the_lowest_straight():
    # 5.4
    wheel = evaluate(cards("AH 2D 3C 4S 5D"))
    six_high = evaluate(cards("2H 3D 4C 5S 6D"))
    broadway = evaluate(cards("AH KD QC JS TD"))
    nine_high = evaluate(cards("9H TD JC QS KD"))
    assert wheel.rank == HandRank.STRAIGHT and wheel.tiebreaker == [5]
    assert wheel < six_high < nine_high < broadway
    # no wrap-around: Q-K-A-2-3 is not a straight
    assert evaluate(cards("QH KD AC 2S 3D")).rank == HandRank.HIGH_CARD
    # a suited wheel is a straight flush, not a royal flush
    assert evaluate(cards("AH 2H 3H 4H 5H")).rank == HandRank.STRAIGHT_FLUSH


def test_fast_evaluator_matches_the_reference_on_random_hands():
    # 5.5 the brute-force evaluator is the oracle (diversity)
    rng = random.Random(2026)
    checked = 0
    for _ in range(300):                       # ordinary random hands
        hand = rng.sample(ALL_CARDS, rng.choice([5, 6, 7]))
        assert evaluate(hand) == evaluate_bruteforce(hand), hand
        checked += 1
    narrow = [c for c in ALL_CARDS if c.suit.name in ("HEARTS", "SPADES")
              and c.rank.value in (2, 3, 4, 5, 6, 7, 14)]
    for _ in range(300):                       # few suits and ranks: many flushes/straights
        hand = rng.sample(narrow, rng.choice([5, 6, 7]))
        assert evaluate(hand) == evaluate_bruteforce(hand), hand
        checked += 1
    assert checked == 600
