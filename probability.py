from card import Card, Rank, Suit
from evaluator import evaluate, HandRank
from itertools import combinations
import random

def probability_of_rank(rank: Rank, known_cards: list[Card]) -> float:
    if not isinstance(rank, Rank):
        raise ValueError("rank must be a Rank")

    if len(known_cards) > 52:
        raise ValueError("There cannot be more than 52 known cards")

    known_rank_count = sum(
        1
        for card in known_cards
        if card.rank == rank
    )

    remaining_cards = 52 - len(known_cards)
    remaining_cards_of_rank = 4 - known_rank_count

    if remaining_cards == 0:
        return 0.0

    return remaining_cards_of_rank / remaining_cards


def probability_of_card(
    target_card: Card,
    known_cards: list[Card]
) -> float:

    if not isinstance(target_card, Card):
        raise ValueError("target_card must be a Card")

    if len(known_cards) > 52:
        raise ValueError("There cannot be more than 52 known cards")

    for card in known_cards:
        if (
            card.rank == target_card.rank
            and card.suit == target_card.suit
        ):
            return 0.0

    remaining_cards = 52 - len(known_cards)

    if remaining_cards == 0:
        return 0.0

    return 1 / remaining_cards


def probability_of_hitting_out(
    outs: int,
    unknown_cards: int,
    draws: int
) -> float:

    if outs < 0:
        raise ValueError("outs cannot be negative")

    if unknown_cards <= 0:
        raise ValueError("unknown_cards must be greater than zero")

    if draws <= 0:
        raise ValueError("draws must be greater than zero")

    if outs > unknown_cards:
        raise ValueError(
            "outs cannot be greater than unknown_cards"
        )

    if draws > unknown_cards:
        raise ValueError(
            "draws cannot be greater than unknown_cards"
        )

    if outs == 0:
        return 0.0

    if outs == unknown_cards:
        return 1.0

    probability_of_missing = 1.0

    for draw in range(draws):
        probability_of_missing *= (
            (unknown_cards - outs - draw)
            / (unknown_cards - draw)
        )

    return 1 - probability_of_missing


def find_outs(
    known_cards: list[Card],
    target_hand: HandRank
) -> list[Card]:

    if len(known_cards) < 5:
        raise ValueError(
            "At least 5 known cards are required"
        )

    if not isinstance(target_hand, HandRank):
        raise ValueError(
            "target_hand must be a HandRank"
        )

    remaining_cards = get_remaining_cards(known_cards)

    current_hand = evaluate(known_cards)

    outs = []

    for card in remaining_cards:
        final_hand = evaluate(
            known_cards + [card]
        )

        if (
            final_hand.rank == target_hand
            and current_hand.rank != target_hand
        ):
            outs.append(card)

    return outs


def probability_of_hand_on_next_card(
    known_cards: list[Card],
    target_hand: HandRank
) -> float:

    outs = find_outs(
        known_cards,
        target_hand
    )

    unknown_cards = len(
        get_remaining_cards(known_cards)
    )

    return probability_of_hitting_out(
        len(outs),
        unknown_cards,
        1
    )

def calculate_hand_probabilities(
    known_cards: list[Card],
    draws: int
) -> dict[HandRank, float]:

    if len(known_cards) < 5:
        raise ValueError(
            "At least 5 known cards are required"
        )

    if draws <= 0:
        raise ValueError(
            "draws must be greater than zero"
        )

    remaining_cards = get_remaining_cards(known_cards)

    if draws > len(remaining_cards):
        raise ValueError(
            "draws cannot exceed remaining cards"
        )

    counts = {
        hand_rank: 0
        for hand_rank in HandRank
    }

    total_combinations = 0

    for future_cards in combinations(
        remaining_cards,
        draws
    ):
        final_cards = known_cards + list(future_cards)

        evaluated_hand = evaluate(final_cards)

        counts[evaluated_hand.rank] += 1
        total_combinations += 1

    return {
        hand_rank: count / total_combinations
        for hand_rank, count in counts.items()
    }

def calculate_hand_probabilities_one_pair_or_better(
    known_cards: list[Card],
    draws: int
) -> dict[HandRank, float]:

    probabilities = calculate_hand_probabilities(
        known_cards,
        draws
    )

    probabilities.pop(HandRank.HIGH_CARD)

    return probabilities

def probability_of_specific_hand(
    known_cards: list[Card],
    target_hand: HandRank,
    draws: int
) -> float:

    if not isinstance(target_hand, HandRank):
        raise ValueError(
            "target_hand must be a HandRank"
        )

    probabilities = calculate_hand_probabilities(
        known_cards,
        draws
    )

    return probabilities[target_hand]

def probability_of_improving_hand(
    known_cards: list[Card],
    draws: int
) -> float:
    if len(known_cards) < 5:
        raise ValueError(
            "At least 5 known cards are required"
        )
    if draws <= 0:
        raise ValueError(
            "draws must be greater than zero"
        )
    remaining_cards = get_remaining_cards(known_cards)
    if draws > len(remaining_cards):
        raise ValueError(
            "draws cannot exceed remaining cards"
        )
    current_hand = evaluate(known_cards)
    total_combinations = 0
    improving_combinations = 0
    for future_cards in combinations(
        remaining_cards,
        draws
    ):
        final_cards = known_cards + list(future_cards)
        final_hand = evaluate(final_cards)
        total_combinations += 1
        if final_hand.rank > current_hand.rank:
            improving_combinations += 1
    return improving_combinations / total_combinations

def probability_of_target_hand_next_card(
    known_cards: list[Card],
    target_hand: HandRank
) -> float:

    outs = find_outs(
        known_cards,
        target_hand
    )

    remaining_cards = get_remaining_cards(
        known_cards
    )

    return len(outs) / len(remaining_cards)

def probability_of_target_hand_by_river(
    known_cards: list[Card],
    target_hand: HandRank
) -> float:

    outs = find_outs(
        known_cards,
        target_hand
    )

    remaining_cards = len(
        get_remaining_cards(known_cards)
    )

    if remaining_cards < 2:
        raise ValueError(
            "At least two unknown cards are required"
        )

    outs_count = len(outs)

    probability_of_missing = (
        (remaining_cards - outs_count)
        / remaining_cards
    ) * (
        (remaining_cards - outs_count - 1)
        / (remaining_cards - 1)
    )

    return 1 - probability_of_missing

def probability_of_target_hand_on_turn(
    known_cards: list[Card],
    target_hand: HandRank
) -> float:

    outs = find_outs(
        known_cards,
        target_hand
    )

    remaining_cards = get_remaining_cards(
        known_cards
    )

    return len(outs) / len(remaining_cards)

def probability_of_target_hand_by_river_exact(
    known_cards: list[Card],
    target_hand: HandRank
) -> float:

    if len(known_cards) < 5:
        raise ValueError(
            "At least 5 known cards are required"
        )

    remaining_cards = get_remaining_cards(
        known_cards
    )

    if len(remaining_cards) < 2:
        raise ValueError(
            "At least two unknown cards are required"
        )

    total_combinations = 0
    successful_combinations = 0

    for future_cards in combinations(
        remaining_cards,
        2
    ):
        final_hand = evaluate(
            known_cards + list(future_cards)
        )

        total_combinations += 1

        if final_hand.rank == target_hand:
            successful_combinations += 1

    return successful_combinations / total_combinations

def probability_report(
    known_cards: list[Card]
) -> dict:

    if len(known_cards) < 5:
        raise ValueError(
            "At least 5 known cards are required"
        )

    if len(known_cards) > 7:
        raise ValueError(
            "At most 7 known cards are allowed"
        )

    if len(known_cards) == 5:
        return {
            "turn": calculate_hand_probabilities_one_pair_or_better(
                known_cards,
                draws=1
            ),
            "by_river": calculate_hand_probabilities_one_pair_or_better(
                known_cards,
                draws=2
            ),
        }

    if len(known_cards) == 6:
        return {
            "turn": None,
            "by_river": calculate_hand_probabilities_one_pair_or_better(
                known_cards,
                draws=1
            ),
        }

    current_hand = evaluate(known_cards)

    return {
        "turn": None,
        "by_river": None,
        "current_hand": current_hand.rank,
    }

def validate_known_cards(known_cards: list[Card]) -> None:

    if len(known_cards) > 52:
        raise ValueError(
            "There cannot be more than 52 known cards"
        )

    seen_cards = set()

    for card in known_cards:
        card_identity = (card.suit, card.rank)

        if card_identity in seen_cards:
            raise ValueError(
                "Known cards cannot contain duplicates"
            )

        seen_cards.add(card_identity)

def get_remaining_cards(known_cards: list[Card]) -> list[Card]:

    validate_known_cards(known_cards)

    known_cards_set = {
        (card.suit, card.rank)
        for card in known_cards
    }

    remaining_cards = []

    card_id = 0

    for suit in Suit:
        for rank in Rank:
            if (suit, rank) not in known_cards_set:
                remaining_cards.append(
                    Card(card_id, suit, rank)
                )

            card_id += 1

    return remaining_cards


def monte_carlo_equity(
    hole_cards: list[Card],
    community_cards: list[Card],
    num_opponents: int,
    simulations: int = 1000,
    rng=None
) -> dict:
    """Estimate the chance of winning the hand by Monte Carlo simulation.

    Assumptions (kept deliberately simple and explicit):
      * every opponent holds two cards drawn uniformly at random from the
        cards that are not visible to the player;
      * the unseen community cards are drawn uniformly at random from the
        same pool;
      * nobody folds - each opponent plays to showdown.

    Returns ``{"win": w, "tie": t, "loss": l}`` where the three values
    sum to 1. ``rng`` may be a ``random.Random`` instance for reproducible
    results; by default the module-level random generator is used.
    """
    if len(hole_cards) != 2:
        raise ValueError("Exactly 2 hole cards are required")

    if len(community_cards) > 5:
        raise ValueError("At most 5 community cards are allowed")

    if num_opponents < 1:
        raise ValueError("At least one opponent is required")

    if simulations <= 0:
        raise ValueError("simulations must be greater than zero")

    known_cards = list(hole_cards) + list(community_cards)
    validate_known_cards(known_cards)

    remaining_cards = get_remaining_cards(known_cards)
    missing_community = 5 - len(community_cards)
    cards_needed = missing_community + 2 * num_opponents

    if cards_needed > len(remaining_cards):
        raise ValueError("Too many opponents for the remaining cards")

    generator = rng if rng is not None else random

    wins = 0
    ties = 0
    losses = 0

    for _ in range(simulations):
        drawn = generator.sample(remaining_cards, cards_needed)

        board = list(community_cards) + drawn[:missing_community]
        hero = evaluate(list(hole_cards) + board)

        best_opponent = None
        for opponent in range(num_opponents):
            start = missing_community + 2 * opponent
            opponent_hand = evaluate(drawn[start:start + 2] + board)

            if best_opponent is None or best_opponent < opponent_hand:
                best_opponent = opponent_hand

        if best_opponent < hero:
            wins += 1
        elif hero < best_opponent:
            losses += 1
        else:
            ties += 1

    return {
        "win": wins / simulations,
        "tie": ties / simulations,
        "loss": losses / simulations,
    }
