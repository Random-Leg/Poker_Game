from enum import IntEnum
from itertools import combinations
from collections import Counter

class HandRank(IntEnum):
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

class EvaluatedHand:
    def __init__(self, rank: HandRank, tiebreaker: list[int]):
        self.rank = rank
        self.tiebreaker = tiebreaker

    def __eq__(self, other):
        if not isinstance(other, EvaluatedHand):
            return NotImplemented

        return (
            self.rank == other.rank
            and self.tiebreaker == other.tiebreaker
        )

    def __lt__(self, other):
        if not isinstance(other, EvaluatedHand):
            return NotImplemented

        if self.rank != other.rank:
            return self.rank < other.rank

        return self.tiebreaker < other.tiebreaker


def evaluate_five(cards):
    if len(cards) != 5:
        raise ValueError("Exactly 5 cards are required")

    ranks = sorted(
        [card.rank.value for card in cards],
        reverse=True
    )

    suits = [card.suit for card in cards]

    counts = Counter(ranks)

    is_flush = len(set(suits)) == 1

    unique_ranks = sorted(set(ranks), reverse=True)

    is_straight = False
    straight_high = None

    if len(unique_ranks) == 5:
        if unique_ranks[0] - unique_ranks[4] == 4:
            is_straight = True
            straight_high = unique_ranks[0]

        # Ace-low straight: A, 2, 3, 4, 5
        elif unique_ranks == [14, 5, 4, 3, 2]:
            is_straight = True
            straight_high = 5

    if is_straight and is_flush:
        if straight_high == 14:
            return EvaluatedHand(
                HandRank.ROYAL_FLUSH,
                [14]
            )

        return EvaluatedHand(
            HandRank.STRAIGHT_FLUSH,
            [straight_high]
        )

    four_of_a_kind = [
        rank for rank, count in counts.items()
        if count == 4
    ]

    if four_of_a_kind:
        four_rank = four_of_a_kind[0]

        kicker = max(
            rank for rank in ranks
            if rank != four_rank
        )

        return EvaluatedHand(
            HandRank.FOUR_OF_A_KIND,
            [four_rank, kicker]
        )

    three_of_a_kind = [
        rank for rank, count in counts.items()
        if count == 3
    ]

    pairs = [
        rank for rank, count in counts.items()
        if count == 2
    ]

    if three_of_a_kind and pairs:
        return EvaluatedHand(
            HandRank.FULL_HOUSE,
            [three_of_a_kind[0], pairs[0]]
        )

    if is_flush:
        return EvaluatedHand(
            HandRank.FLUSH,
            ranks
        )

    if is_straight:
        return EvaluatedHand(
            HandRank.STRAIGHT,
            [straight_high]
        )

    if three_of_a_kind:
        three_rank = three_of_a_kind[0]

        kickers = sorted(
            [rank for rank in ranks if rank != three_rank],
            reverse=True
        )

        return EvaluatedHand(
            HandRank.THREE_OF_A_KIND,
            [three_rank] + kickers
        )

    if len(pairs) == 2:
        pairs_sorted = sorted(pairs, reverse=True)

        kicker = max(
            rank for rank in ranks
            if rank not in pairs
        )

        return EvaluatedHand(
            HandRank.TWO_PAIR,
            pairs_sorted + [kicker]
        )

    if len(pairs) == 1:
        pair_rank = pairs[0]

        kickers = sorted(
            [rank for rank in ranks if rank != pair_rank],
            reverse=True
        )

        return EvaluatedHand(
            HandRank.ONE_PAIR,
            [pair_rank] + kickers
        )

    return EvaluatedHand(
        HandRank.HIGH_CARD,
        ranks
    )

def evaluate_bruteforce(cards):
    """Reference implementation: best of every 5-card combination.

    Kept for cross-checking the fast evaluator in the test-suite.
    """
    if len(cards) < 5:
        raise ValueError("At least 5 cards are required")

    best_hand = None
    
    for combination in combinations(cards, 5):
        evaluated = evaluate_five(combination)
        if best_hand is None or best_hand < evaluated:
            best_hand = evaluated
    return best_hand


def _straight_high(rank_set):
    """Return the high card of the best straight in rank_set, else None."""
    ranks = set(rank_set)
    if 14 in ranks:
        ranks.add(1)  # ace plays low in A-2-3-4-5
    for high in range(14, 4, -1):
        if all((high - offset) in ranks for offset in range(5)):
            return high
    return None


def evaluate(cards):
    """Return the best five-card hand that can be made from 5-7 cards.

    Evaluates all cards at once (rather than trying all 21 five-card
    combinations) which is roughly an order of magnitude faster and
    gives identical results to ``evaluate_bruteforce``.
    """
    if len(cards) < 5:
        raise ValueError("At least 5 cards are required")

    if len(cards) == 5:
        return evaluate_five(cards)

    ranks = [card.rank.value for card in cards]
    counts = Counter(ranks)

    suit_ranks = {}
    for card in cards:
        suit_ranks.setdefault(card.suit, []).append(card.rank.value)

    flush_ranks = None
    for suited in suit_ranks.values():
        if len(suited) >= 5:
            flush_ranks = sorted(suited, reverse=True)

    if flush_ranks is not None:
        straight_flush_high = _straight_high(flush_ranks)
        if straight_flush_high == 14:
            return EvaluatedHand(HandRank.ROYAL_FLUSH, [14])
        if straight_flush_high is not None:
            return EvaluatedHand(
                HandRank.STRAIGHT_FLUSH, [straight_flush_high]
            )

    quads = sorted(
        (rank for rank, count in counts.items() if count == 4),
        reverse=True
    )
    trips = sorted(
        (rank for rank, count in counts.items() if count == 3),
        reverse=True
    )
    pairs = sorted(
        (rank for rank, count in counts.items() if count == 2),
        reverse=True
    )

    if quads:
        kicker = max(rank for rank in counts if rank != quads[0])
        return EvaluatedHand(HandRank.FOUR_OF_A_KIND, [quads[0], kicker])

    if trips and (len(trips) > 1 or pairs):
        pair_candidates = pairs + trips[1:]
        return EvaluatedHand(
            HandRank.FULL_HOUSE,
            [trips[0], max(pair_candidates)]
        )

    if flush_ranks is not None:
        return EvaluatedHand(HandRank.FLUSH, flush_ranks[:5])

    straight_high = _straight_high(counts.keys())
    if straight_high is not None:
        return EvaluatedHand(HandRank.STRAIGHT, [straight_high])

    distinct_desc = sorted(counts.keys(), reverse=True)

    if trips:
        kickers = [rank for rank in distinct_desc if rank != trips[0]][:2]
        return EvaluatedHand(
            HandRank.THREE_OF_A_KIND, [trips[0]] + kickers
        )

    if len(pairs) >= 2:
        top_pairs = pairs[:2]
        kicker = max(rank for rank in distinct_desc if rank not in top_pairs)
        return EvaluatedHand(HandRank.TWO_PAIR, top_pairs + [kicker])

    if len(pairs) == 1:
        kickers = [rank for rank in distinct_desc if rank != pairs[0]][:3]
        return EvaluatedHand(HandRank.ONE_PAIR, [pairs[0]] + kickers)

    return EvaluatedHand(HandRank.HIGH_CARD, distinct_desc[:5])


_RANK_NAMES = {
    2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven",
    8: "Eight", 9: "Nine", 10: "Ten", 11: "Jack", 12: "Queen",
    13: "King", 14: "Ace",
}

_RANK_PLURALS = {
    2: "Twos", 3: "Threes", 4: "Fours", 5: "Fives", 6: "Sixes",
    7: "Sevens", 8: "Eights", 9: "Nines", 10: "Tens", 11: "Jacks",
    12: "Queens", 13: "Kings", 14: "Aces",
}


def describe_hand(hand):
    """Human readable description of an EvaluatedHand."""
    t = hand.tiebreaker

    if hand.rank == HandRank.ROYAL_FLUSH:
        return "Royal Flush"
    if hand.rank == HandRank.STRAIGHT_FLUSH:
        return f"Straight Flush, {_RANK_NAMES[t[0]]} high"
    if hand.rank == HandRank.FOUR_OF_A_KIND:
        return f"Four of a Kind, {_RANK_PLURALS[t[0]]}"
    if hand.rank == HandRank.FULL_HOUSE:
        return (
            f"Full House, {_RANK_PLURALS[t[0]]} full of "
            f"{_RANK_PLURALS[t[1]]}"
        )
    if hand.rank == HandRank.FLUSH:
        return f"Flush, {_RANK_NAMES[t[0]]} high"
    if hand.rank == HandRank.STRAIGHT:
        return f"Straight, {_RANK_NAMES[t[0]]} high"
    if hand.rank == HandRank.THREE_OF_A_KIND:
        return f"Three of a Kind, {_RANK_PLURALS[t[0]]}"
    if hand.rank == HandRank.TWO_PAIR:
        return (
            f"Two Pair, {_RANK_PLURALS[t[0]]} and {_RANK_PLURALS[t[1]]}"
        )
    if hand.rank == HandRank.ONE_PAIR:
        return f"Pair of {_RANK_PLURALS[t[0]]}"
    return f"High Card, {_RANK_NAMES[t[0]]}"
