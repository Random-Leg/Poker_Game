from card import Card

class Player:
    def __init__(self, name: str, chips: int):
        if chips < 0:
            raise ValueError("Chips cannot be negative")
        
        self.name = name
        self.chips = chips
        self.hand = []
        self.folded = False
        self.all_in = False

    def add_card(self, card: Card):
        if len(self.hand) >= 2:
            raise ValueError("Player can only have 2 cards in hand")
        self.hand.append(card)

    def clear_hand(self):
        self.hand = []

    def fold(self):
        self.folded = True

    def bet(self, amount: int):
        if amount <= 0:
            raise ValueError("Bet amount must be positive")
        if amount > self.chips:
            raise ValueError("Cannot bet more chips than the player has")
        
        self.chips -= amount
        if self.chips == 0:
            self.all_in = True
        
        return amount