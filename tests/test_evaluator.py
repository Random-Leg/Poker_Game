from card import Card, Rank, Suit
from evaluator import HandRank, evaluate, evaluate_five

def test_high_card():
    cards = [
        Card(0, Suit.HEARTS, Rank.TWO),
        Card(14, Suit.DIAMONDS, Rank.THREE),
        Card(27, Suit.CLUBS, Rank.FOUR),
        Card(40, Suit.SPADES, Rank.FIVE),
        Card(5, Suit.HEARTS, Rank.NINE)
    ]
    result = evaluate_five(cards)
    assert result.rank == HandRank.HIGH_CARD

def test_one_pair():
    cards = [
        Card(0, Suit.HEARTS, Rank.TWO),
        Card(13, Suit.DIAMONDS, Rank.TWO),
        Card(27, Suit.CLUBS, Rank.FOUR),
        Card(40, Suit.SPADES, Rank.FIVE),
        Card(5, Suit.HEARTS, Rank.NINE)
    ]
    result = evaluate_five(cards)
    assert result.rank == HandRank.ONE_PAIR

def test_two_pair():
    cards = [
        Card(0, Suit.HEARTS, Rank.TWO),
        Card(13, Suit.DIAMONDS, Rank.TWO),
        Card(27, Suit.CLUBS, Rank.FOUR),
        Card(40, Suit.SPADES, Rank.FOUR),
        Card(5, Suit.HEARTS, Rank.NINE)
    ]
    result = evaluate_five(cards)
    assert result.rank == HandRank.TWO_PAIR

def test_three_of_a_kind():
    cards = [
        Card(0, Suit.HEARTS, Rank.TWO),
        Card(13, Suit.DIAMONDS, Rank.TWO),
        Card(26, Suit.CLUBS, Rank.TWO),
        Card(40, Suit.SPADES, Rank.FOUR),
        Card(5, Suit.HEARTS, Rank.NINE)
    ]
    result = evaluate_five(cards)
    assert result.rank == HandRank.THREE_OF_A_KIND

def test_straight():
    cards = [
        Card(0, Suit.HEARTS, Rank.TWO),
        Card(14, Suit.DIAMONDS, Rank.THREE),
        Card(28, Suit.CLUBS, Rank.FOUR),
        Card(42, Suit.SPADES, Rank.FIVE),
        Card(6, Suit.HEARTS, Rank.SIX)
    ]
    result = evaluate_five(cards)
    assert result.rank == HandRank.STRAIGHT

def test_flush():
    cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.TEN),
        Card(2, Suit.HEARTS, Rank.EIGHT),
        Card(3, Suit.HEARTS, Rank.FIVE),
        Card(4, Suit.HEARTS, Rank.TWO),
    ]
    result = evaluate_five(cards)
    assert result.rank == HandRank.FLUSH
    assert result.tiebreaker == [14, 10, 8, 5, 2]

def test_full_house():
    cards = [
        Card(0, Suit.HEARTS, Rank.KING),
        Card(1, Suit.DIAMONDS, Rank.KING),
        Card(2, Suit.CLUBS, Rank.KING),
        Card(3, Suit.SPADES, Rank.TEN),
        Card(4, Suit.HEARTS, Rank.TEN),
    ]
    result = evaluate_five(cards)
    assert result.rank == HandRank.FULL_HOUSE
    assert result.tiebreaker == [13, 10]

def test_four_of_a_kind():
    cards = [
        Card(0, Suit.HEARTS, Rank.QUEEN),
        Card(1, Suit.DIAMONDS, Rank.QUEEN),
        Card(2, Suit.CLUBS, Rank.QUEEN),
        Card(3, Suit.SPADES, Rank.QUEEN),
        Card(4, Suit.HEARTS, Rank.TWO),
    ]
    result = evaluate_five(cards)
    assert result.rank == HandRank.FOUR_OF_A_KIND
    assert result.tiebreaker == [12, 2]

def test_straight_flush():
    cards = [
        Card(0, Suit.HEARTS, Rank.NINE),
        Card(1, Suit.HEARTS, Rank.EIGHT),
        Card(2, Suit.HEARTS, Rank.SEVEN),
        Card(3, Suit.HEARTS, Rank.SIX),
        Card(4, Suit.HEARTS, Rank.FIVE),
    ]
    result = evaluate_five(cards)
    assert result.rank == HandRank.STRAIGHT_FLUSH
    assert result.tiebreaker == [9]

def test_royal_flush():
    cards = [
        Card(0, Suit.SPADES, Rank.ACE),
        Card(1, Suit.SPADES, Rank.KING),
        Card(2, Suit.SPADES, Rank.QUEEN),
        Card(3, Suit.SPADES, Rank.JACK),
        Card(4, Suit.SPADES, Rank.TEN),
    ]
    result = evaluate_five(cards)
    assert result.rank == HandRank.ROYAL_FLUSH
    assert result.tiebreaker == [14]

def test_ace_low_straight():
    cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.TWO),
        Card(2, Suit.CLUBS, Rank.THREE),
        Card(3, Suit.SPADES, Rank.FOUR),
        Card(4, Suit.HEARTS, Rank.FIVE),
    ]
    result = evaluate_five(cards)
    assert result.rank == HandRank.STRAIGHT
    assert result.tiebreaker == [5]

def test_ace_low_straight_flush():
    cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.TWO),
        Card(2, Suit.HEARTS, Rank.THREE),
        Card(3, Suit.HEARTS, Rank.FOUR),
        Card(4, Suit.HEARTS, Rank.FIVE),
    ]
    result = evaluate_five(cards)
    assert result.rank == HandRank.STRAIGHT_FLUSH
    assert result.tiebreaker == [5]

def test_evaluate_five_rejects_less_than_five_cards():
    cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.KING),
        Card(2, Suit.CLUBS, Rank.QUEEN),
        Card(3, Suit.SPADES, Rank.JACK),
    ]
    try:
        evaluate_five(cards)
        assert False
    except ValueError:
        pass

def test_evaluate_five_rejects_more_than_five_cards():
    cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.KING),
        Card(2, Suit.CLUBS, Rank.QUEEN),
        Card(3, Suit.SPADES, Rank.JACK),
        Card(4, Suit.HEARTS, Rank.TEN),
        Card(5, Suit.DIAMONDS, Rank.NINE),
    ]
    try:
        evaluate_five(cards)
        assert False
    except ValueError:
        pass

def test_higher_pair_beats_lower_pair():
    hand_one = [
        Card(0, Suit.HEARTS, Rank.KING),
        Card(1, Suit.DIAMONDS, Rank.KING),
        Card(2, Suit.CLUBS, Rank.NINE),
        Card(3, Suit.SPADES, Rank.SEVEN),
        Card(4, Suit.HEARTS, Rank.TWO),
    ]
    hand_two = [
        Card(5, Suit.HEARTS, Rank.QUEEN),
        Card(6, Suit.DIAMONDS, Rank.QUEEN),
        Card(7, Suit.CLUBS, Rank.ACE),
        Card(8, Suit.SPADES, Rank.SEVEN),
        Card(9, Suit.HEARTS, Rank.TWO),
    ]
    result_one = evaluate_five(hand_one)
    result_two = evaluate_five(hand_two)
    assert result_one > result_two

def test_higher_kicker_wins_with_same_pair():
    hand_one = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.ACE),
        Card(2, Suit.CLUBS, Rank.KING),
        Card(3, Suit.SPADES, Rank.NINE),
        Card(4, Suit.HEARTS, Rank.TWO),
    ]
    hand_two = [
        Card(5, Suit.HEARTS, Rank.ACE),
        Card(6, Suit.DIAMONDS, Rank.ACE),
        Card(7, Suit.CLUBS, Rank.QUEEN),
        Card(8, Suit.SPADES, Rank.NINE),
        Card(9, Suit.HEARTS, Rank.TWO),
    ]
    result_one = evaluate_five(hand_one)
    result_two = evaluate_five(hand_two)
    assert result_one > result_two

def test_higher_straight_wins():
    lower_straight = [
        Card(0, Suit.HEARTS, Rank.FIVE),
        Card(1, Suit.DIAMONDS, Rank.FOUR),
        Card(2, Suit.CLUBS, Rank.THREE),
        Card(3, Suit.SPADES, Rank.TWO),
        Card(4, Suit.HEARTS, Rank.SIX),
    ]
    higher_straight = [
        Card(5, Suit.HEARTS, Rank.SIX),
        Card(6, Suit.DIAMONDS, Rank.FIVE),
        Card(7, Suit.CLUBS, Rank.FOUR),
        Card(8, Suit.SPADES, Rank.THREE),
        Card(9, Suit.HEARTS, Rank.SEVEN),
    ]
    result_one = evaluate_five(lower_straight)
    result_two = evaluate_five(higher_straight)
    assert result_two > result_one

def test_evaluate_seven_cards_finds_best_hand():
    cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.ACE),
        Card(2, Suit.CLUBS, Rank.KING),
        Card(3, Suit.SPADES, Rank.QUEEN),
        Card(4, Suit.HEARTS, Rank.JACK),
        Card(5, Suit.DIAMONDS, Rank.NINE),
        Card(6, Suit.CLUBS, Rank.TWO),
    ]
    result = evaluate(cards)
    assert result.rank == HandRank.ONE_PAIR
    assert result.tiebreaker == [14, 13, 12, 11]

def test_evaluate_seven_cards_finds_straight():
    cards = [
        Card(0, Suit.HEARTS, Rank.TWO),
        Card(1, Suit.DIAMONDS, Rank.THREE),
        Card(2, Suit.CLUBS, Rank.FOUR),
        Card(3, Suit.SPADES, Rank.FIVE),
        Card(4, Suit.HEARTS, Rank.SIX),
        Card(5, Suit.DIAMONDS, Rank.KING),
        Card(6, Suit.CLUBS, Rank.ACE),
    ]
    result = evaluate(cards)
    assert result.rank == HandRank.STRAIGHT
    assert result.tiebreaker == [6]

def test_evaluate_seven_cards_finds_flush():
    cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.JACK),
        Card(2, Suit.HEARTS, Rank.NINE),
        Card(3, Suit.HEARTS, Rank.SEVEN),
        Card(4, Suit.HEARTS, Rank.FOUR),
        Card(5, Suit.CLUBS, Rank.KING),
        Card(6, Suit.SPADES, Rank.TWO),
    ]
    result = evaluate(cards)
    assert result.rank == HandRank.FLUSH
    assert result.tiebreaker == [14, 11, 9, 7, 4]

def test_evaluate_seven_cards_finds_full_house():
    cards = [
        Card(0, Suit.HEARTS, Rank.KING),
        Card(1, Suit.DIAMONDS, Rank.KING),
        Card(2, Suit.CLUBS, Rank.KING),
        Card(3, Suit.SPADES, Rank.TEN),
        Card(4, Suit.HEARTS, Rank.TEN),
        Card(5, Suit.DIAMONDS, Rank.ACE),
        Card(6, Suit.CLUBS, Rank.TWO),
    ]
    result = evaluate(cards)
    assert result.rank == HandRank.FULL_HOUSE
    assert result.tiebreaker == [13, 10]

def test_evaluate_rejects_less_than_five_cards():
    cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.KING),
        Card(2, Suit.CLUBS, Rank.QUEEN),
        Card(3, Suit.SPADES, Rank.JACK),
    ]
    try:
        evaluate(cards)
        assert False
    except ValueError:
        pass

# --- fast evaluator must agree with the brute-force reference ------------

import random as _random

from deck import Deck as _Deck
from evaluator import evaluate_bruteforce, describe_hand


def _cards(spec):
    suits = {"h": Suit.HEARTS, "d": Suit.DIAMONDS, "c": Suit.CLUBS, "s": Suit.SPADES}
    ranks = {str(n): Rank(n) for n in range(2, 10)}
    ranks.update({"T": Rank.TEN, "J": Rank.JACK, "Q": Rank.QUEEN, "K": Rank.KING, "A": Rank.ACE})
    return [Card(0, suits[item[1]], ranks[item[0]]) for item in spec.split()]


def test_fast_evaluator_matches_bruteforce_on_random_hands():
    rng = _random.Random(2024)
    all_cards = _Deck().cards

    for _ in range(4000):
        cards = rng.sample(all_cards, rng.choice([5, 6, 7]))
        fast = evaluate(cards)
        slow = evaluate_bruteforce(cards)
        assert fast.rank == slow.rank
        assert fast.tiebreaker == slow.tiebreaker


def test_fast_evaluator_matches_bruteforce_on_structured_hands():
    rng = _random.Random(99)
    all_cards = _Deck().cards
    pools = [
        [c for c in all_cards if c.suit in (Suit.HEARTS, Suit.SPADES)],
        [c for c in all_cards if c.rank.value in (14, 2, 3, 4, 5, 6, 7)],
        [c for c in all_cards if c.rank.value in (3, 4, 5) or c.suit == Suit.CLUBS],
    ]

    for index in range(3000):
        pool = pools[index % len(pools)]
        cards = rng.sample(pool, rng.choice([6, 7]))
        fast = evaluate(cards)
        slow = evaluate_bruteforce(cards)
        assert (fast.rank, fast.tiebreaker) == (slow.rank, slow.tiebreaker)


def test_seven_card_wheel_straight_flush():
    hand = evaluate(_cards("Ah 2h 3h 4h 5h Kd Kc"))
    assert hand.rank == HandRank.STRAIGHT_FLUSH
    assert hand.tiebreaker == [5]


def test_seven_cards_with_two_trips_make_a_full_house():
    hand = evaluate(_cards("Kh Kd Kc Qh Qd Qc 2s"))
    assert hand.rank == HandRank.FULL_HOUSE
    assert hand.tiebreaker == [13, 12]


def test_three_pairs_use_best_two_and_best_kicker():
    hand = evaluate(_cards("Ah Ad Kc Kd 5h 5d 2s"))
    assert hand.rank == HandRank.TWO_PAIR
    assert hand.tiebreaker == [14, 13, 5]


def test_flush_beats_a_straight_in_seven_cards():
    hand = evaluate(_cards("2h 5h 9h Jh Kh 6c 7d"))
    assert hand.rank == HandRank.FLUSH


def test_describe_hand_names():
    assert describe_hand(evaluate(_cards("Ah Kh Qh Jh Th"))) == "Royal Flush"
    assert describe_hand(evaluate(_cards("Ah Ad Kc Kd 5h"))) == "Two Pair, Aces and Kings"
    assert describe_hand(evaluate(_cards("Ah Ad Ac Kd Kh"))) == "Full House, Aces full of Kings"
    assert describe_hand(evaluate(_cards("2h 7d 9c Jd Kh"))) == "High Card, King"
    assert describe_hand(evaluate(_cards("Qh Qd 9c Jd Kh"))) == "Pair of Queens"
