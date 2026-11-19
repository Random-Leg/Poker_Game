"""Shared scaffolding for the tests: card shorthand, a stacked deck, game
builders and small drivers that play a hand."""
import random

from betting import BettingAction
from card import Card, Rank, Suit
from deck import Deck
from game import BETTING_STATES, GameState, PokerGame
from player import Player

SUIT_LETTERS = {"H": Suit.HEARTS, "D": Suit.DIAMONDS, "C": Suit.CLUBS, "S": Suit.SPADES}
RANK_LETTERS = {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
SUIT_ORDER = list(Suit)


def card(text):
    """'AH' is the ace of hearts, '10S' or 'TS' the ten of spades."""
    suit = SUIT_LETTERS[text[-1]]
    symbol = text[:-1]
    value = RANK_LETTERS.get(symbol) or int(symbol)
    card_id = SUIT_ORDER.index(suit) * 13 + (value - 2)
    return Card(card_id, suit, Rank(value))


def cards(text):
    return [card(item) for item in text.split()]


def stack_deck(monkeypatch, order):
    """Make the next shuffled deck deal ``order`` first ('??' = any card).

    Draw order in a hand: hole cards one at a time round the table (twice),
    then burn, flop x3, burn, turn, burn, river.
    """
    def stacked_shuffle(self):
        wanted_ids = {card(item).card_id for item in order if item != "??"}
        spare = [c for c in self.cards if c.card_id not in wanted_ids]
        sequence = []
        for item in order:
            if item == "??":
                sequence.append(spare.pop())
            else:
                wanted = card(item)
                sequence.append(next(c for c in self.cards if c.card_id == wanted.card_id))
        self.cards = spare + list(reversed(sequence))

    monkeypatch.setattr(Deck, "shuffle", stacked_shuffle)


def table(chips, human_name="You", human_seat=0, **kwargs):
    """A nine-seat game. ``chips`` is a list; missing seats get 0 chips.

    Seats are named "Player 1" to "Player 9", except the human's seat.
    """
    chips = list(chips) + [0] * (9 - len(chips))
    names = [f"Player {i}" for i in range(1, 10)]
    names[human_seat] = human_name
    players = [Player(name, amount) for name, amount in zip(names, chips)]
    return PokerGame(players, human_name=human_name, **kwargs)


def full_table(**kwargs):
    return table([1000] * 9, **kwargs)


def snapshot(game):
    return (
        game.state,
        game.current_player.name if game.current_player else None,
        game.pot.amount,
        tuple(sorted((p.name, a) for p, a in game.pot.contributions.items())),
        tuple((p.name, p.chips, p.folded, p.all_in, len(p.hand)) for p in game.players),
        game.betting_round.current_bet,
        game.betting_round.minimum_raise,
        len(game.community_cards),
        len(game.deck),
    )


def act(game, *actions):
    """Perform actions in turn; each item is an action or (action, amount)."""
    for item in actions:
        action, amount = item if isinstance(item, tuple) else (item, None)
        game.perform_action(action, amount)


def check_or_call(game):
    legal = game.betting_round.get_legal_actions(game.current_player, game.pot)
    game.perform_action(BettingAction.CHECK if BettingAction.CHECK in legal else BettingAction.CALL)


def check_down(game):
    """Everyone checks or calls until the betting is over."""
    while game.state in BETTING_STATES:
        check_or_call(game)


def fold_until_done(game):
    while game.state in BETTING_STATES:
        game.perform_action(BettingAction.FOLD)


def play_to(game, target):
    """Check/call until the game reaches ``target`` (a GameState)."""
    while game.state != target:
        check_or_call(game)


def finish(game):
    """Take a hand that has reached showdown to HAND_COMPLETE."""
    if game.state == GameState.SHOWDOWN:
        game.complete_hand()
