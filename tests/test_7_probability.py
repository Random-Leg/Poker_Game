"""Requirement group 7: probability estimate."""
import random
import time
from itertools import combinations

import pytest

from evaluator import evaluate
from helpers import card, cards
from probability import get_remaining_cards, monte_carlo_equity

SITUATIONS = [
    ("pre-flop", "AH KH", ""),
    ("flop", "9S 9D", "2C 9H KD"),
    ("turn", "AS KS", "9S 5D 2S JH"),
    ("river", "QH QD", "2C 7D 9H 4C 3D"),
]


@pytest.mark.parametrize("name, hole, board", SITUATIONS, ids=[s[0] for s in SITUATIONS])
def test_win_tie_loss_are_probabilities_that_sum_to_one(name, hole, board):
    # 7.1
    result = monte_carlo_equity(cards(hole), cards(board), 3, 500, rng=random.Random(1))
    assert set(result) == {"win", "tie", "loss"}
    assert all(0 <= value <= 1 for value in result.values())
    assert sum(result.values()) == pytest.approx(1, abs=1e-6)


def test_a_hand_that_plays_the_board_is_a_tie_not_a_win():
    # 7.1 royal flush on the board: every opponent ties
    result = monte_carlo_equity(cards("2C 3D"), cards("AH KH QH JH TH"), 2, 200, rng=random.Random(3))
    assert result == {"win": 0.0, "tie": 1.0, "loss": 0.0}


@pytest.mark.parametrize(
    "hole, board, opponents, simulations",
    [
        ("AH", "", 1, 100),                          # one hole card
        ("AH KH QH", "", 1, 100),                    # three hole cards
        ("AH KH", "2C 3C 4C 5C 6C 7C", 1, 100),      # six community cards
        ("AH AH", "", 1, 100),                       # duplicate hole cards
        ("AH KH", "AH 3C 4C", 1, 100),               # board repeats a hole card
        ("AH KH", "", 0, 100),                       # no opponent
        ("AH KH", "", 1, 0),                         # zero simulations
        ("AH KH", "", 1, -5),                        # negative simulations
        ("AH KH", "", 24, 100),                      # 5 + 48 cards needed, only 50 left
    ],
)
def test_invalid_input_is_rejected(hole, board, opponents, simulations):
    # 7.4
    with pytest.raises(ValueError):
        monte_carlo_equity(cards(hole), cards(board), opponents, simulations)


class RecordingRandom(random.Random):
    def __init__(self, seed):
        super().__init__(seed)
        self.draws = []

    def sample(self, population, k, **kwargs):
        chosen = super().sample(population, k, **kwargs)
        self.draws.append(chosen)
        return chosen


def test_simulated_cards_never_repeat_known_or_other_simulated_cards():
    # 7.2
    hole, board = cards("AH KH"), cards("9S 5D 2S")
    known = {(c.suit, c.rank) for c in hole + board}
    rng = RecordingRandom(5)
    monte_carlo_equity(hole, board, 8, 300, rng=rng)
    assert len(rng.draws) == 300
    for drawn in rng.draws:
        identities = [(c.suit, c.rank) for c in drawn]
        assert len(set(identities)) == len(identities)
        assert not set(identities) & known


def exact_win_probability(hole, board):
    """Enumerate every river card and every opponent hand (heads-up, on the turn)."""
    remaining = get_remaining_cards(hole + board)
    wins = total = 0
    for river in remaining:
        rest = [c for c in remaining if c is not river]
        full_board = board + [river]
        mine = evaluate(hole + full_board)
        for opponent in combinations(rest, 2):
            theirs = evaluate(list(opponent) + full_board)
            wins += theirs < mine
            total += 1
    return wins / total


@pytest.mark.parametrize("hole, board", [("AS KS", "9S 5D 2S JH"), ("7H 7D", "2C 9H KD 3S")])
def test_estimate_is_within_two_points_of_the_exactly_enumerated_win_probability(hole, board):
    # 7.5 and 7.3 heads-up on the turn: the estimate and the enumeration share the evaluator
    hole, board = cards(hole), cards(board)
    exact = exact_win_probability(hole, board)
    estimate = monte_carlo_equity(hole, board, 1, 10_000, rng=random.Random(2026))["win"]
    assert abs(estimate - exact) <= 0.02, (estimate, exact)


def test_estimate_is_fast_enough_for_the_in_game_setting():
    # 7.6 limits are 1 s for 2,000 simulations vs 8 opponents and 5 s for 10,000
    hole, board = cards("AH KH"), cards("9S 5D 2S")
    started = time.perf_counter()
    monte_carlo_equity(hole, board, 8, 2000, rng=random.Random(1))
    first = time.perf_counter() - started
    started = time.perf_counter()
    monte_carlo_equity(hole, board, 8, 10_000, rng=random.Random(1))
    second = time.perf_counter() - started
    print(f"2,000 simulations: {first:.2f}s, 10,000 simulations: {second:.2f}s")
    assert first < 1.0 and second < 5.0
