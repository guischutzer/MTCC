import copy as c

# Class of the cards in the battlefield.
# Todo: make it extend Card Class to eliminate some redundancy
# and long attribution chains.

class Permanent:

    def __init__(self, card, player):
        self.card = card
        self.abilities = c.copy(card.abilities)
        self.owner = player
        self.controller = player
        self.tapped = False
        self.sick = False

        if "ETB" in self.abilities:
            self.abilities["ETB"]()

    def tap(self):
        self.tapped = True

    def removeSickness(self):
        self.sick = False

    def canAttack(self):
        return False

    def canBlock(self):
        return False

    def untap(self):
        self.tapped = False

    def stats(self):
        return self.card.name

    def resetPT(self):
        return

    def removeDamage(self):
        return
