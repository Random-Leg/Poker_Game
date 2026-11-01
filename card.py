from enum import Enum

class Suit(Enum):
    HEARTS = 'Hearts'
    DIAMONDS = 'Diamonds'
    CLUBS = 'Clubs'
    SPADES = 'Spades'

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

class Card:
    def __init__(self, card_id: int, suit: Suit, rank: Rank):
        if not 0 <= card_id <= 51:
            raise ValueError("card_id must be between 0 and 51")
        self.card_id = card_id
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank.name} of {self.suit.value}"

    _RANK_SYMBOLS = {
        11: "J", 12: "Q", 13: "K", 14: "A"
    }

    _SUIT_SYMBOLS = {
        "Hearts": "\u2665",
        "Diamonds": "\u2666",
        "Clubs": "\u2663",
        "Spades": "\u2660",
    }

    def short(self):
        """Compact display form, e.g. 'A\u2665' or '10\u2660'."""
        rank = self._RANK_SYMBOLS.get(self.rank.value, str(self.rank.value))
        return f"{rank}{self._SUIT_SYMBOLS[self.suit.value]}"

    def __repr__(self):
        return f"Card({self.short()})"
