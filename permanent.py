import copy as c
import inspect

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

    def isPlayer(self):
        return False

    def isTapped(self):
        return self.tapped

    def getController(self):
        return self.controller

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

class Creature(Permanent):

    def __init__(self, card, player):
        super().__init__()
        self.dealtLethal = False

        self.power = card.power
        self.tou = card.tou
        self.curPower = self.power
        self.curTou = self.tou
        self.attacking = False
        self.blocking = False
        self.damage = 0
        self.currentAbilities = self.abilities
        if "Haste" not in self.currentAbilities:
            self.sick = True


    def dealDamage(self, target, amount):
        target.takeDamage(amount)
        if self.hasLifelink() in self.currentAbilities:
            self.controller.gainLife(amount)
        if self.hasDeathtouch() and inspect.isinstance(target, Creature):
                target.die()

    def takeDamage(self, amount):
        self.damage += amount
        if self.damage >= self.curTou:
            self.die()

    def die(self):
        self.dealtLethal = True

    def resetPTA(self):
        self.curPower = self.power
        self.curTou = self.tou
        self.currentAbilities = self.abilities

    def removeDamage(self):
        self.damage = 0

    def attack(self):
        if "Vigilance" not in self.currentAbilities:
            self.tapped = True
        self.attacking = True

    def block(self, attacker):
        attacker.isBlocked()
        self.blocking = True

    def canAttack(self):
        return self.controller.isActive and not self.tapped and not self.sick

    def canBlock(self, attacker):

        if not self.tapped or self.blocking or self.controller.isActive:
            return False

        if "Flying" in attacker.currentAbilities:
            if "Flying" in self.currentAbilities or "Reach" in self.currentAbilities:
                return True
            else:
                return False

        return True

    def hasFirstStrike(self):
        return "First Strike" in self.currentAbilities

    def hasDoubleStrike(self):
        return "Double Strike" in self.currentAbilities

    def hasLifelink(self):
        return "Lifelink" in self.currentAbilities

    def hasDeathtouch(self):
        return "Deathtouch" in self.currentAbilities

    def hasTrample(self):
        return "Trample" in self.currentAbilities

    def hasHexproof(self):
        return "Hexproof" in self.currentAbilities

    def stats(self):
        return self.card.name + " " + str(self.curPower) "/" + str(self.curTou) + "(" + str(self.damage) + ")"
