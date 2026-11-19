"""Requirement group 6: bots."""
import random

import pytest

from betting import BettingAction as A
from bot import Bot
from card import Card
from game import BETTING_STATES
from helpers import full_table

STRATEGIES = ("passive", "balanced", "aggressive")


def collect_situations(count=250, seed=7):
    """Play seeded hands with random bot choices and record what each bot was asked."""
    rng = random.Random(seed)
    random.seed(seed)
    game = full_table(blind_levels=[(25, 50)], hands_per_level=10)
    chooser = Bot("balanced")
    found = []
    while len(found) < count and not game.is_game_over():
        game.start_hand()
        while game.state in BETTING_STATES:
            player = game.current_player
            legal = game.betting_round.get_legal_actions(player, game.pot)
            situation = game.get_bot_situation(player)
            equity = rng.random()
            found.append((legal, situation, equity))
            action, amount = chooser.decide(legal, situation, equity=equity)
            game.perform_action(action, amount)
        if game.state.name == "SHOWDOWN":
            game.complete_hand()
        if not game.is_game_over():
            game.reset_hand()
    return found[:count]


SITUATIONS = collect_situations()


def decisions(strategy, repeats=1, seed=1):
    random.seed(seed)
    bot = Bot(strategy)
    for _ in range(repeats):
        for legal, situation, equity in SITUATIONS:
            action, amount = bot.decide(legal, situation, equity=equity)
            yield legal, situation, action, amount


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_bot_only_returns_legal_actions_with_amounts_in_range(strategy):
    # 6.1
    seen = set()
    for legal, situation, action, amount in decisions(strategy, repeats=3):
        assert action in legal
        seen.add(action)
        if action == A.BET:
            assert min(situation["min_bet"], situation["chips"]) <= amount <= situation["chips"]
        elif action == A.RAISE:
            assert situation["min_raise"] <= amount <= situation["max_raise"]
        else:
            assert amount is None
    assert len(seen) >= 3                      # the sample is varied enough to mean something


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_bot_never_folds_when_it_can_check_for_free(strategy):
    # 6.3
    free = [d for d in decisions(strategy, repeats=3) if A.CHECK in d[0]]
    assert len(free) > 100
    assert all(action != A.FOLD for _, _, action, _ in free)


def test_unknown_strategy_and_empty_legal_actions_are_rejected():
    # 6.4
    with pytest.raises(ValueError):
        Bot("reckless")
    legal, situation, _ = SITUATIONS[0]
    with pytest.raises(ValueError):
        Bot("balanced").decide([], situation)


def test_the_three_styles_bet_and_raise_in_different_amounts():
    # 6.5 2,000 identical decision situations (250 situations x 8 repeats) per style
    share = {}
    for strategy in STRATEGIES:
        taken = [action for _, _, action, _ in decisions(strategy, repeats=8)]
        assert len(taken) == 2000
        share[strategy] = sum(a in (A.BET, A.RAISE) for a in taken) / len(taken)
    assert share["aggressive"] > share["balanced"] > share["passive"], share


def test_a_bot_is_given_only_its_own_hole_cards_and_public_information():
    # 6.2 everything in the situation that is a card is the bot's own or on the board
    game = full_table()
    game.start_hand()
    for player in game.players:
        situation = game.get_bot_situation(player)
        cards_given = []

        def walk(value):
            if isinstance(value, Card):
                cards_given.append(value)
            elif isinstance(value, (list, tuple, set)):
                for item in value:
                    walk(item)
            elif isinstance(value, dict):
                for item in value.values():
                    walk(item)

        walk(situation)
        allowed = {c.card_id for c in player.hand} | {c.card_id for c in game.community_cards}
        assert {c.card_id for c in cards_given} <= allowed
        assert situation["hole_cards"] == player.hand
