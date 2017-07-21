import copy as c

# Class of the cards in the battlefield.
# Todo: make it extend Card Class to eliminate some redundancy
# and long attribution chains.

class Permanent:

    def __init__(self, card, player):
        self.card = card
        self.abilities = c.copy(card.abilities)
        self.owner = player
        self.tapped = False
        self.sick = False

        if self.card.ctype == "Creature":
            if "Haste" not in self.abilities:
                self.sick = True
            self.power = card.power
            self.tou = card.tou
            self.attacking = False
            self.blocking = False
        else:
            self.sickness = False

        if "ETB" in self.abilities:
            self.abilities["ETB"]()

    def tap(self):
        self.tapped = True

    def untap(self):
        self.tapped = False

    def attack(self):
        if "Vigilance" not in self.abilities:
            self.tapped = True
        self.attacking = True

    def block(self, attacker):
        attacker.isBlocked()
        self.blocking = True

    def canAttack(self):
        return self.card.ctype == "Creature" and not self.tapped and not self.sick

    def canBlock(self, attacker):

        if not self.card.ctype == "Creature" or not self.tapped or self.blocking:
            return False

        if "Unblockable" in attacker.abilities:
            return False

        if "Flying" in attacker.abilities:
            if "Flying" in self.abilities or "Reach" in self.abilities:
                return True
            else:
                return False

        return True

    def takeDamage(self, damage):
        if damage >= 1:
            self.tou = self.tou - damage
            return True
        return False

    def hasFirstStrike(self):
        return "First Strike" in self.abilities

    def hasDoubleStrike(self):
        return "Double Strike" in self.abilities

    def hasDeathtouch(self):
        return "Deathtouch" in self.abilities

    def hasTrample(self):
        return "Trample" in self.abilities

    def stats(self):
        return self.card.name + " " + str(self.power) "/" + str(self.tou)
