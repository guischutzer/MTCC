import copy as c
import inspect

# Class of the cards in the battlefield.
# Todo: make it extend Card Class to eliminate some redundancy
# and long attribution chains.

class Permanent:

    def __init__(self, card, player):
        self.card = card
        self.abilities = c.copy(card.abilities)
        self.ctype = card.ctype
        self.owner = card.owner
        self.controller = player
        self.tapped = False
        self.sick = False

    def putOnGraveyard(self):
        self.owner.graveyard.append(self.card)

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
        virado = 'U'
        if self.isTapped():
            virado = 'T'
        return (self.card.name + " " + virado)

    def resetPT(self):
        return

    def removeDamage(self):
        return

class Land(Permanent):

    def __init__(self, card, player):
        super().__init__(card, player)
        self.controller.untappedLands += 1

    def untap(self):
        if self.tapped:
            self.controller.untappedLands += 1
        self.tapped = False

    def tap(self):
        if not self.tapped:
            self.controller.untappedLands -= 1
        self.tapped = True


class Creature(Permanent):

    def __init__(self, card, player):
        super().__init__(card, player)
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
        self.blocking = True

    def canAttack(self):
        return self.controller.isActive and not self.tapped and not self.sick

    def canBlock(self, attacker):

        if self.tapped or self.blocking:
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
        virado = 'U'
        if self.tapped:
            virado = 'T'
        return self.card.name + " " + virado + " " + str(self.curPower) + "/" + str(self.curTou) + "(" + str(self.damage) + ")"
