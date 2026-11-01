from card import Card, Rank, Suit
from probability import (probability_of_rank, probability_of_card, probability_of_hitting_out, calculate_hand_probabilities, 
                         calculate_hand_probabilities_one_pair_or_better, probability_of_specific_hand, 
                         probability_of_improving_hand, find_outs, probability_of_target_hand_by_river, 
                         probability_of_target_hand_next_card, probability_of_target_hand_on_turn, 
                         probability_of_target_hand_by_river_exact, probability_report, get_remaining_cards)
import pytest
from evaluator import HandRank

def test_probability_of_rank_with_two_known_cards():
    known_cards = [
        Card(0, Suit.SPADES, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.KING),
    ]
    probability = probability_of_rank(
        Rank.ACE,
        known_cards
    )
    assert probability == pytest.approx(3 / 50)

def test_probability_of_rank_with_no_known_cards():
    probability = probability_of_rank(
        Rank.ACE,
        []
    )
    assert probability == pytest.approx(4 / 52)

def test_probability_of_rank_with_one_known_card():
    known_cards = [
        Card(0, Suit.SPADES, Rank.ACE),
    ]
    probability = probability_of_rank(
        Rank.ACE,
        known_cards
    )
    assert probability == pytest.approx(3 / 51)

def test_probability_of_card_with_no_known_cards():
    target = Card(0, Suit.SPADES, Rank.ACE)
    probability = probability_of_card(
        target,
        []
    )
    assert probability == pytest.approx(1 / 52)

def test_probability_of_card_with_known_cards():
    target = Card(0, Suit.SPADES, Rank.ACE)
    known_cards = [
        Card(1, Suit.HEARTS, Rank.KING),
        Card(2, Suit.CLUBS, Rank.TWO),
    ]
    probability = probability_of_card(
        target,
        known_cards
    )
    assert probability == pytest.approx(1 / 50)

def test_probability_of_known_card_is_zero():
    target = Card(0, Suit.SPADES, Rank.ACE)
    known_cards = [
        target,
        Card(1, Suit.HEARTS, Rank.KING),
    ]
    probability = probability_of_card(
        target,
        known_cards
    )
    assert probability == pytest.approx(0.0)

def test_probability_of_hitting_out_on_next_card():
    probability = probability_of_hitting_out(
        outs=9,
        unknown_cards=47,
        draws=1
    )
    assert probability == pytest.approx(9 / 47)

def test_probability_of_missing_out_on_next_card():
    probability = probability_of_hitting_out(
        outs=0,
        unknown_cards=47,
        draws=1
    )
    assert probability == pytest.approx(0.0)

def test_probability_of_hitting_out_over_two_draws():
    probability = probability_of_hitting_out(
        outs=9,
        unknown_cards=47,
        draws=2
    )
    expected = 1 - ((38 / 47) * (37 / 46))
    assert probability == pytest.approx(expected)

def test_probability_of_hitting_out_with_all_cards_as_outs():
    probability = probability_of_hitting_out(
        outs=47,
        unknown_cards=47,
        draws=1
    )
    assert probability == pytest.approx(1.0)

def test_calculate_hand_probabilities_after_flop():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.KING),
        Card(2, Suit.HEARTS, Rank.QUEEN),
        Card(3, Suit.CLUBS, Rank.TWO),
        Card(4, Suit.DIAMONDS, Rank.SEVEN),
    ]
    probabilities = calculate_hand_probabilities(
        known_cards,
        draws=2
    )
    assert sum(probabilities.values()) == pytest.approx(1.0)

def test_calculate_hand_probabilities_contains_all_hand_types():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.KING),
        Card(2, Suit.CLUBS, Rank.QUEEN),
        Card(3, Suit.SPADES, Rank.JACK),
        Card(4, Suit.HEARTS, Rank.NINE),
    ]
    probabilities = calculate_hand_probabilities(
        known_cards,
        draws=2
    )
    for hand_rank in HandRank:
        assert hand_rank in probabilities

def test_calculate_hand_probabilities_has_no_negative_values():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.KING),
        Card(2, Suit.CLUBS, Rank.QUEEN),
        Card(3, Suit.SPADES, Rank.JACK),
        Card(4, Suit.HEARTS, Rank.NINE),
    ]
    probabilities = calculate_hand_probabilities(
        known_cards,
        draws=2
    )
    for probability in probabilities.values():
        assert probability >= 0

def test_calculate_hand_probabilities_requires_five_known_cards():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.KING),
    ]
    with pytest.raises(ValueError):
        calculate_hand_probabilities(
            known_cards,
            draws=2
        )

def test_calculate_hand_probabilities_one_pair_or_better_excludes_high_card():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.KING),
        Card(2, Suit.CLUBS, Rank.QUEEN),
        Card(3, Suit.SPADES, Rank.JACK),
        Card(4, Suit.HEARTS, Rank.NINE),
    ]

    probabilities = calculate_hand_probabilities_one_pair_or_better(
        known_cards,
        draws=2
    )

    assert HandRank.HIGH_CARD not in probabilities


def test_calculate_hand_probabilities_one_pair_or_better_contains_nine_categories():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.KING),
        Card(2, Suit.CLUBS, Rank.QUEEN),
        Card(3, Suit.SPADES, Rank.JACK),
        Card(4, Suit.HEARTS, Rank.NINE),
    ]

    probabilities = calculate_hand_probabilities_one_pair_or_better(
        known_cards,
        draws=2
    )

    expected_categories = [
        HandRank.ONE_PAIR,
        HandRank.TWO_PAIR,
        HandRank.THREE_OF_A_KIND,
        HandRank.STRAIGHT,
        HandRank.FLUSH,
        HandRank.FULL_HOUSE,
        HandRank.FOUR_OF_A_KIND,
        HandRank.STRAIGHT_FLUSH,
        HandRank.ROYAL_FLUSH,
    ]

    assert set(probabilities.keys()) == set(expected_categories)


def test_calculate_hand_probabilities_one_pair_or_better_values_are_valid():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.KING),
        Card(2, Suit.CLUBS, Rank.QUEEN),
        Card(3, Suit.SPADES, Rank.JACK),
        Card(4, Suit.HEARTS, Rank.NINE),
    ]

    probabilities = calculate_hand_probabilities_one_pair_or_better(
        known_cards,
        draws=2
    )

    for probability in probabilities.values():
        assert 0 <= probability <= 1

def test_calculate_hand_probabilities_one_pair_or_better_on_turn():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.KING),
        Card(2, Suit.CLUBS, Rank.QUEEN),
        Card(3, Suit.SPADES, Rank.JACK),
        Card(4, Suit.HEARTS, Rank.NINE),
    ]

    probabilities = calculate_hand_probabilities_one_pair_or_better(
        known_cards,
        draws=1
    )

    assert set(probabilities.keys()) == {
        HandRank.ONE_PAIR,
        HandRank.TWO_PAIR,
        HandRank.THREE_OF_A_KIND,
        HandRank.STRAIGHT,
        HandRank.FLUSH,
        HandRank.FULL_HOUSE,
        HandRank.FOUR_OF_A_KIND,
        HandRank.STRAIGHT_FLUSH,
        HandRank.ROYAL_FLUSH,
    }

    for probability in probabilities.values():
        assert 0 <= probability <= 1


def test_calculate_hand_probabilities_one_pair_or_better_by_river():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.KING),
        Card(2, Suit.CLUBS, Rank.QUEEN),
        Card(3, Suit.SPADES, Rank.JACK),
        Card(4, Suit.HEARTS, Rank.NINE),
    ]

    probabilities = calculate_hand_probabilities_one_pair_or_better(
        known_cards,
        draws=2
    )

    assert sum(probabilities.values()) <= 1.0

def test_probability_of_specific_hand():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.KING),
        Card(2, Suit.HEARTS, Rank.QUEEN),
        Card(3, Suit.CLUBS, Rank.TWO),
        Card(4, Suit.DIAMONDS, Rank.SEVEN),
    ]

    probability = probability_of_specific_hand(
        known_cards,
        HandRank.FLUSH,
        draws=2
    )

    assert 0 <= probability <= 1


def test_probability_of_specific_hand_matches_full_calculation():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.KING),
        Card(2, Suit.CLUBS, Rank.QUEEN),
        Card(3, Suit.SPADES, Rank.JACK),
        Card(4, Suit.HEARTS, Rank.NINE),
    ]

    probabilities = calculate_hand_probabilities(
        known_cards,
        draws=2
    )

    probability = probability_of_specific_hand(
        known_cards,
        HandRank.STRAIGHT,
        draws=2
    )

    assert probability == pytest.approx(
        probabilities[HandRank.STRAIGHT]
    )


def test_probability_of_specific_hand_requires_valid_hand_rank():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.KING),
        Card(2, Suit.CLUBS, Rank.QUEEN),
        Card(3, Suit.SPADES, Rank.JACK),
        Card(4, Suit.HEARTS, Rank.NINE),
    ]

    with pytest.raises(ValueError):
        probability_of_specific_hand(
            known_cards,
            "flush",
            draws=2
        )

def test_probability_of_improving_hand():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.ACE),
        Card(2, Suit.CLUBS, Rank.KING),
        Card(3, Suit.SPADES, Rank.QUEEN),
        Card(4, Suit.HEARTS, Rank.NINE),
    ]

    probability = probability_of_improving_hand(
        known_cards,
        draws=2
    )

    assert 0 <= probability <= 1


def test_probability_of_improving_hand_is_zero_when_already_royal_flush():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.KING),
        Card(2, Suit.HEARTS, Rank.QUEEN),
        Card(3, Suit.HEARTS, Rank.JACK),
        Card(4, Suit.HEARTS, Rank.TEN),
    ]

    probability = probability_of_improving_hand(
        known_cards,
        draws=1
    )

    assert probability == 0.0


def test_probability_of_improving_hand_requires_at_least_five_cards():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.KING),
    ]

    with pytest.raises(ValueError):
        probability_of_improving_hand(
            known_cards,
            draws=2
        )

def test_find_outs_for_flush():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.KING),
        Card(2, Suit.HEARTS, Rank.QUEEN),
        Card(3, Suit.HEARTS, Rank.NINE),
        Card(4, Suit.CLUBS, Rank.TWO),
    ]

    outs = find_outs(
        known_cards,
        HandRank.FLUSH
    )

    assert len(outs) == 9


def test_find_outs_does_not_include_known_cards():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.KING),
        Card(2, Suit.HEARTS, Rank.QUEEN),
        Card(3, Suit.HEARTS, Rank.NINE),
        Card(4, Suit.CLUBS, Rank.TWO),
    ]

    outs = find_outs(
        known_cards,
        HandRank.FLUSH
    )

    for card in outs:
        assert card not in known_cards


def test_find_outs_requires_five_known_cards():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.KING),
    ]

    with pytest.raises(ValueError):
        find_outs(
            known_cards,
            HandRank.FLUSH
        )

def test_probability_of_hitting_outs_on_next_card():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.KING),
        Card(2, Suit.HEARTS, Rank.QUEEN),
        Card(3, Suit.HEARTS, Rank.NINE),
        Card(4, Suit.CLUBS, Rank.TWO),
    ]

    probability = probability_of_target_hand_next_card(
        known_cards,
        HandRank.FLUSH
    )

    assert probability == pytest.approx(9 / 47)


def test_probability_of_hitting_outs_by_river():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.KING),
        Card(2, Suit.HEARTS, Rank.QUEEN),
        Card(3, Suit.HEARTS, Rank.NINE),
        Card(4, Suit.CLUBS, Rank.TWO),
    ]

    probability = probability_of_target_hand_by_river(
        known_cards,
        HandRank.FLUSH
    )

    expected = 1 - ((38 / 47) * (37 / 46))

    assert probability == pytest.approx(expected)


def test_probability_of_target_hand_next_card_requires_five_cards():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.KING),
    ]

    with pytest.raises(ValueError):
        probability_of_target_hand_next_card(
            known_cards,
            HandRank.FLUSH
        )

def test_probability_of_target_hand_on_turn():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.KING),
        Card(2, Suit.HEARTS, Rank.QUEEN),
        Card(3, Suit.HEARTS, Rank.NINE),
        Card(4, Suit.CLUBS, Rank.TWO),
    ]

    probability = probability_of_target_hand_on_turn(
        known_cards,
        HandRank.FLUSH
    )

    assert probability == pytest.approx(9 / 47)


def test_probability_of_target_hand_by_river_is_exact():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.KING),
        Card(2, Suit.HEARTS, Rank.QUEEN),
        Card(3, Suit.HEARTS, Rank.NINE),
        Card(4, Suit.CLUBS, Rank.TWO),
    ]

    probability = probability_of_target_hand_by_river_exact(
        known_cards,
        HandRank.FLUSH
    )

    assert 0 <= probability <= 1

def test_probability_report_contains_turn_and_river_probabilities():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.KING),
        Card(2, Suit.HEARTS, Rank.QUEEN),
        Card(3, Suit.CLUBS, Rank.TWO),
        Card(4, Suit.DIAMONDS, Rank.SEVEN),
    ]

    report = probability_report(known_cards)

    assert "turn" in report
    assert "by_river" in report


def test_probability_report_contains_nine_hand_categories():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.KING),
        Card(2, Suit.CLUBS, Rank.QUEEN),
        Card(3, Suit.SPADES, Rank.JACK),
        Card(4, Suit.HEARTS, Rank.NINE),
    ]

    report = probability_report(known_cards)

    expected_categories = {
        HandRank.ONE_PAIR,
        HandRank.TWO_PAIR,
        HandRank.THREE_OF_A_KIND,
        HandRank.STRAIGHT,
        HandRank.FLUSH,
        HandRank.FULL_HOUSE,
        HandRank.FOUR_OF_A_KIND,
        HandRank.STRAIGHT_FLUSH,
        HandRank.ROYAL_FLUSH,
    }

    assert set(report["by_river"].keys()) == expected_categories


def test_probability_report_probabilities_are_valid():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.DIAMONDS, Rank.KING),
        Card(2, Suit.CLUBS, Rank.QUEEN),
        Card(3, Suit.SPADES, Rank.JACK),
        Card(4, Suit.HEARTS, Rank.NINE),
    ]

    report = probability_report(known_cards)

    for category in report["turn"].values():
        assert 0 <= category <= 1

    for category in report["by_river"].values():
        assert 0 <= category <= 1

def test_probability_rejects_duplicate_known_cards():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.ACE),
        Card(2, Suit.CLUBS, Rank.KING),
        Card(3, Suit.SPADES, Rank.QUEEN),
        Card(4, Suit.DIAMONDS, Rank.NINE),
    ]

    with pytest.raises(ValueError):
        calculate_hand_probabilities(
            known_cards,
            draws=2
        )


def test_probability_rejects_duplicate_cards_in_probability_report():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.ACE),
        Card(2, Suit.CLUBS, Rank.KING),
        Card(3, Suit.SPADES, Rank.QUEEN),
        Card(4, Suit.DIAMONDS, Rank.NINE),
    ]

    with pytest.raises(ValueError):
        probability_report(known_cards)

def test_get_remaining_cards_rejects_duplicate_known_cards():
    known_cards = [
        Card(0, Suit.HEARTS, Rank.ACE),
        Card(1, Suit.HEARTS, Rank.ACE),
    ]

    with pytest.raises(ValueError):
        get_remaining_cards(known_cards)

# --- Monte Carlo equity ------------------------------------------------

import random as _random

from probability import monte_carlo_equity


def _hole(rank_a, rank_b, suit_a=Suit.HEARTS, suit_b=Suit.SPADES):
    return [Card(0, suit_a, rank_a), Card(1, suit_b, rank_b)]


def test_monte_carlo_probabilities_sum_to_one():
    result = monte_carlo_equity(
        _hole(Rank.ACE, Rank.KING), [], 3, 500, _random.Random(1)
    )

    assert result["win"] + result["tie"] + result["loss"] == pytest.approx(1.0)


def test_pocket_aces_are_a_big_favourite_heads_up():
    result = monte_carlo_equity(
        _hole(Rank.ACE, Rank.ACE), [], 1, 3000, _random.Random(2)
    )

    assert 0.80 < result["win"] < 0.90


def test_seven_deuce_is_a_big_underdog_against_a_full_table():
    result = monte_carlo_equity(
        _hole(Rank.SEVEN, Rank.TWO), [], 8, 2000, _random.Random(3)
    )

    assert result["win"] < 0.15


def test_monte_carlo_is_reproducible_with_a_seeded_generator():
    first = monte_carlo_equity(
        _hole(Rank.QUEEN, Rank.JACK), [], 2, 400, _random.Random(7)
    )
    second = monte_carlo_equity(
        _hole(Rank.QUEEN, Rank.JACK), [], 2, 400, _random.Random(7)
    )

    assert first == second


def test_unbeatable_hand_always_wins():
    board = [
        Card(2, Suit.HEARTS, Rank.QUEEN),
        Card(3, Suit.HEARTS, Rank.JACK),
        Card(4, Suit.HEARTS, Rank.TEN),
        Card(5, Suit.CLUBS, Rank.TWO),
        Card(6, Suit.DIAMONDS, Rank.THREE),
    ]
    hole = [Card(0, Suit.HEARTS, Rank.ACE), Card(1, Suit.HEARTS, Rank.KING)]

    result = monte_carlo_equity(hole, board, 4, 300, _random.Random(4))

    assert result["win"] == 1.0


def test_monte_carlo_never_reuses_known_cards():
    hole = _hole(Rank.ACE, Rank.KING)
    duplicate_board = [Card(9, Suit.HEARTS, Rank.ACE)]

    with pytest.raises(ValueError):
        monte_carlo_equity(hole, duplicate_board, 2, 10)


@pytest.mark.parametrize(
    "hole, opponents, simulations",
    [
        ([Card(0, Suit.HEARTS, Rank.ACE)], 1, 10),
        (None, 0, 10),
        (None, 1, 0),
    ],
)
def test_monte_carlo_validates_arguments(hole, opponents, simulations):
    hole = hole if hole is not None else _hole(Rank.ACE, Rank.KING)

    with pytest.raises(ValueError):
        monte_carlo_equity(hole, [], opponents, simulations)
