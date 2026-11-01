import random
from card import Card, Suit, Rank

class Deck:
    def __init__(self):
        self.cards = []
        card_id = 0

        for suit in Suit:
            for rank in Rank:
                self.cards.append(Card(card_id, suit, rank))
                card_id += 1

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if len(self.cards) == 0:
            raise ValueError("No cards left in the deck")
        return self.cards.pop()

    def __len__(self):
        return len(self.cards)