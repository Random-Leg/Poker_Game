from game import GameState
import pytest
from evaluator import HandRank
from bot import Bot
from betting import BettingAction


def test_bot_rejects_empty_legal_actions():
    bot = Bot()

    with pytest.raises(ValueError):
        bot.choose_action([])


def test_bot_returns_legal_action():
    bot = Bot()

    legal_actions = [
        BettingAction.CHECK,
        BettingAction.CALL,
        BettingAction.FOLD,
    ]

    action = bot.choose_action(legal_actions)

    assert action in legal_actions


def test_passive_bot_prefers_check():
    bot = Bot("passive")

    legal_actions = [
        BettingAction.CHECK,
        BettingAction.CALL,
        BettingAction.FOLD,
    ]

    assert bot.choose_action(legal_actions) == BettingAction.CHECK


def test_passive_bot_prefers_call_over_fold():
    bot = Bot("passive")

    legal_actions = [
        BettingAction.CALL,
        BettingAction.FOLD,
    ]

    assert bot.choose_action(legal_actions) == BettingAction.CALL


def test_aggressive_bot_can_raise():
    bot = Bot("aggressive")

    legal_actions = [
        BettingAction.CALL,
        BettingAction.RAISE
    ]

    probabilities = {
        HandRank.ROYAL_FLUSH: 1.0
    }

    actions = []

    for _ in range(100):
        actions.append(
            bot.choose_action(
                legal_actions,
                probabilities
            )
        )

    assert BettingAction.RAISE in actions


def test_aggressive_bot_can_bet():
    bot = Bot("aggressive")

    legal_actions = [
        BettingAction.CHECK,
        BettingAction.BET
    ]

    probabilities = {
        HandRank.ROYAL_FLUSH: 1.0
    }

    actions = []

    for _ in range(100):
        actions.append(
            bot.choose_action(
                legal_actions,
                probabilities
            )
        )

    assert BettingAction.BET in actions


def test_balanced_bot_prefers_check():
    bot = Bot("balanced")

    legal_actions = [
        BettingAction.CHECK,
        BettingAction.CALL,
        BettingAction.BET,
    ]

    assert bot.choose_action(legal_actions) == BettingAction.CHECK


def test_invalid_strategy():
    with pytest.raises(ValueError):
        Bot("invalid")


def test_single_legal_action():
    bot = Bot()

    assert bot.choose_action(
        [BettingAction.CHECK]
    ) == BettingAction.CHECK

import pytest

from bot import Bot
from betting import BettingAction


def test_passive_bot_checks_when_possible():
    bot = Bot("passive")

    actions = [
        BettingAction.CHECK,
        BettingAction.CALL,
        BettingAction.FOLD
    ]

    assert bot.choose_action(actions) == BettingAction.CHECK


def test_passive_bot_calls_when_check_is_not_possible():
    bot = Bot("passive")

    actions = [
        BettingAction.CALL,
        BettingAction.FOLD
    ]

    assert bot.choose_action(actions) == BettingAction.CALL


def test_passive_bot_folds_when_only_fold_is_reasonable():
    bot = Bot("passive")

    actions = [
        BettingAction.FOLD
    ]

    assert bot.choose_action(actions) == BettingAction.FOLD


def test_aggressive_bot_returns_legal_action():
    bot = Bot("aggressive")

    actions = [
        BettingAction.CHECK,
        BettingAction.CALL,
        BettingAction.RAISE,
        BettingAction.FOLD
    ]

    for _ in range(100):
        action = bot.choose_action(actions)
        assert action in actions


def test_balanced_bot_returns_legal_action():
    bot = Bot("balanced")

    actions = [
        BettingAction.CHECK,
        BettingAction.CALL,
        BettingAction.BET,
        BettingAction.RAISE,
        BettingAction.FOLD
    ]

    for _ in range(100):
        action = bot.choose_action(actions)
        assert action in actions


def test_bot_rejects_invalid_strategy():
    with pytest.raises(ValueError):
        Bot("invalid")


def test_bot_rejects_empty_legal_actions():
    bot = Bot("balanced")

    with pytest.raises(ValueError):
        bot.choose_action([])


def test_bot_can_choose_using_probability_report():
    bot = Bot("aggressive")

    legal_actions = [
        BettingAction.CALL,
        BettingAction.RAISE,
        BettingAction.FOLD
    ]

    probabilities = {
        HandRank.ONE_PAIR: 0.60,
        HandRank.TWO_PAIR: 0.20,
        HandRank.THREE_OF_A_KIND: 0.10,
        HandRank.STRAIGHT: 0.05,
        HandRank.FLUSH: 0.04,
        HandRank.FULL_HOUSE: 0.01,
        HandRank.FOUR_OF_A_KIND: 0.0,
        HandRank.STRAIGHT_FLUSH: 0.0,
        HandRank.ROYAL_FLUSH: 0.0,
    }

    action = bot.choose_action(
        legal_actions,
        probabilities
    )

    assert action in legal_actions


def test_aggressive_bot_has_higher_raise_probability_than_balanced():
    aggressive = Bot("aggressive")
    balanced = Bot("balanced")

    probability = {
        HandRank.FLUSH: 1.0
    }

    aggressive_chance = aggressive.get_raise_probability(
        probability
    )

    balanced_chance = balanced.get_raise_probability(
        probability
    )

    assert aggressive_chance > balanced_chance


def test_balanced_bot_has_higher_raise_probability_than_passive():
    balanced = Bot("balanced")
    passive = Bot("passive")

    probability = {
        HandRank.FLUSH: 1.0
    }

    balanced_chance = balanced.get_raise_probability(
        probability
    )

    passive_chance = passive.get_raise_probability(
        probability
    )

    assert balanced_chance > passive_chance


def test_stronger_hand_has_higher_raise_probability():
    bot = Bot("aggressive")

    one_pair_probability = {
        HandRank.ONE_PAIR: 1.0
    }

    flush_probability = {
        HandRank.FLUSH: 1.0
    }

    one_pair_chance = bot.get_raise_probability(
        one_pair_probability
    )

    flush_chance = bot.get_raise_probability(
        flush_probability
    )

    assert flush_chance > one_pair_chance

# --- decision making used by the game ---------------------------------

import random as _random

from bot import pre_flop_score
from card import Card, Rank, Suit
from game import PokerGame
from player import Player


def _pair(rank_a, rank_b, suited=False):
    second_suit = Suit.HEARTS if suited else Suit.SPADES
    return [Card(0, Suit.HEARTS, rank_a), Card(1, second_suit, rank_b)]


def _situation(hole, board=(), to_call=0, pot=30, chips=1000, opponents=3):
    return {
        "hole_cards": hole,
        "community_cards": list(board),
        "num_opponents": opponents,
        "pot": pot,
        "to_call": to_call,
        "current_bet": to_call,
        "min_raise": 20,
        "max_raise": max(20, chips - to_call),
        "min_bet": 20,
        "chips": chips,
        "big_blind": 20,
    }


def test_pre_flop_score_orders_hands_sensibly():
    aces = pre_flop_score(_pair(Rank.ACE, Rank.ACE))
    ace_king_suited = pre_flop_score(_pair(Rank.ACE, Rank.KING, suited=True))
    seven_deuce = pre_flop_score(_pair(Rank.SEVEN, Rank.TWO))

    assert aces > ace_king_suited > seven_deuce


def test_bot_folds_trash_to_a_raise_pre_flop():
    random_state = _random.getstate()
    _random.seed(1)
    bot = Bot("balanced")
    legal = [BettingAction.FOLD, BettingAction.CALL, BettingAction.RAISE, BettingAction.ALL_IN]

    action, _ = bot.decide(legal, _situation(_pair(Rank.SEVEN, Rank.TWO), to_call=100))

    _random.setstate(random_state)
    assert action == BettingAction.FOLD


def test_bot_never_folds_when_it_can_check():
    bot = Bot("passive")
    legal = [BettingAction.FOLD, BettingAction.CHECK, BettingAction.BET, BettingAction.ALL_IN]

    for seed in range(50):
        _random.seed(seed)
        action, _ = bot.decide(legal, _situation(_pair(Rank.SEVEN, Rank.TWO)))
        assert action != BettingAction.FOLD


def test_bot_returns_legal_amounts():
    legal = [BettingAction.FOLD, BettingAction.CALL, BettingAction.RAISE, BettingAction.ALL_IN]

    for strategy in ("passive", "balanced", "aggressive"):
        bot = Bot(strategy)
        for seed in range(100):
            _random.seed(seed)
            situation = _situation(_pair(Rank.ACE, Rank.ACE), to_call=40, chips=500)
            action, amount = bot.decide(legal, situation)
            assert action in legal
            if action == BettingAction.RAISE:
                assert situation["min_raise"] <= amount <= situation["max_raise"]


def test_bot_post_flop_calls_with_strong_equity_and_folds_with_weak():
    legal = [BettingAction.FOLD, BettingAction.CALL, BettingAction.ALL_IN]
    board = [
        Card(2, Suit.CLUBS, Rank.TWO),
        Card(3, Suit.DIAMONDS, Rank.NINE),
        Card(4, Suit.SPADES, Rank.JACK),
    ]
    situation = _situation(_pair(Rank.SEVEN, Rank.THREE), board, to_call=100, pot=200)

    _random.seed(0)
    weak, _ = Bot("balanced").decide(legal, situation, equity=0.05)
    _random.seed(0)
    strong, _ = Bot("balanced").decide(legal, situation, equity=0.9)

    assert weak == BettingAction.FOLD
    assert strong == BettingAction.CALL


def test_bots_play_a_full_hand_through_the_game_without_errors():
    _random.seed(5)
    players = [Player(f"P{i}", 1000) for i in range(9)]
    game = PokerGame(players, human_name="P0")
    bots = {p.name: Bot("balanced") for p in players}

    game.start_hand()
    while game.state in (
        GameState.PRE_FLOP, GameState.FLOP, GameState.TURN, GameState.RIVER
    ):
        player = game.current_player
        legal = game.betting_round.get_legal_actions(player, game.pot)
        action, amount = bots[player.name].decide(
            legal, game.get_bot_situation(player), equity=_random.random()
        )
        game.perform_action(action, amount)

    assert sum(p.chips for p in players) + game.pot.amount == 9000
