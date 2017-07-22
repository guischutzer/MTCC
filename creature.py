import permanent
import inspect

class Creature(permanent.Permanent):

    def __init__(self, card, player):
        self.card = card
        self.abilities = c.copy(card.abilities)
        self.owner = player
        self.controller = player
        self.tapped = False
        self.sick = False
        self.dealtLethal = False
        if "Haste" not in self.abilities:
            self.sick = True
        self.power = card.power
        self.tou = card.tou
        self.curPower = self.power
        self.curTou = self.tou
        self.attacking = False
        self.blocking = False
        self.damage = 0

    def dealDamage(self, target, amount):
        target.takeDamage(amount)
        if "Lifelink" in self.abilities:
            self.controller.gainLife(amount)
        if "Deathtouch" in self.abilities and inspect.isinstance(target, Creature):
                target.die()

    def takeDamage(self, amount):
        self.damage += amount
        if self.damage >= self.curTou:
            self.die()

    def die(self):
        self.dealtLethal = True

    def resetPT(self):
        self.curPower = self.power
        self.curTou = self.tou

    def removeDamage(self):
        self.damage = 0

    def attack(self):
        if "Vigilance" not in self.abilities:
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

        if "Flying" in attacker.abilities:
            if "Flying" in self.abilities or "Reach" in self.abilities:
                return True
            else:
                return False

        return True

    def hasFirstStrike(self):
        return "First Strike" in self.abilities

    def hasDoubleStrike(self):
        return "Double Strike" in self.abilities

    def hasDeathtouch(self):
        return "Deathtouch" in self.abilities

    def hasTrample(self):
        return "Trample" in self.abilities

    def stats(self):
        return self.card.name + " " + str(self.curPower) "/" + str(self.curTou) + "(" + str(self.damage) + ")"
