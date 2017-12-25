import re
import colors

class Card:

    def __init__(self, name, owner):
        self.name = name
        self.cost = ""
        self.supertype = ""
        self.ctype = ""
        self.subtype = ""
        self.text = ""
        self.targets = []
        self.owner = owner

    def cmc(self):
        m = re.match("(\d?)(\w*)", self.cost).groups()
        c = 0
        if m[0] != "":
            c += int(m[0])
        c += len(m[1])
        return c

    def color(self, cost):
        c = []
        for color in colors:
            if re.search(color, cost) is not None:
                c.append(color)

        return c

    def abilities(self):
        return

    def effect(self, targets):
        return

    def __str__(self):
        s = self.name + "\n"
        s += self.cost + "\n"
        s += self.supertype + "\n"
        s += self.ctype + "\n"
        s += self.subtype + "\n"
        s += self.text + "\n"
        return s

class Mountain(Card):
    def __init__(self, owner):
        self.name = "Mountain"
        self.cost = ""
        self.supertype = "Basic"
        self.ctype = "Land"
        self.subtype = "Mountain"
        self.text = "{T}: Add {R} to your mana pool."
        self.targets = []
        self.owner = owner

class Swamp(Card):
    def __init__(self, owner):
        self.name = "Swamp"
        self.cost = ""
        self.supertype = "Basic"
        self.ctype = "Land"
        self.subtype = "Swamp"
        self.text = "{T}: Add {B} to your mana pool."
        self.targets = []
        self.owner = owner

class Plains(Card):
    def __init__(self, owner):
        self.name = "Plains"
        self.cost = ""
        self.supertype = "Basic"
        self.ctype = "Land"
        self.subtype = "Plains"
        self.text = "{T}: Add {W} to your mana pool."
        self.targets = []
        self.owner = owner

class VolcanicHammer(Card):
    def __init__(self, owner):
        self.name = "Volcanic Hammer"
        self.cost = "1R"
        self.supertype = ""
        self.ctype = "Sorcery"
        self.subtype = ""
        self.text = "Volcanic Hammer deals 3 damage to target creature or player."
        self.targets = [("OwnCreature", "OpponentCreature", "Player")]
        self.owner = owner

    def effect(self, targets):
        targets[0].takeDamage(3)

class FoulImp(Card):
    def __init__(self, owner):
        self.name = "Foul Imp"
        self.cost = "B"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Imp"
        self.text = "Flying. When Foul Imp enters the battlefield you lose 1 life. 1/1"
        self.abilities = ["Flying"]
        self.targets = []
        self.owner = owner
        self.power = 1
        self.tou = 1

    def effect(self, targets):
        self.owner.loseLife(1)

class AngelofMercy(Card):
    def __init__(self,owner):
        self.name = "Angel of Mercy"
        self.cost = "4W"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Angel"
        self.text = "Flying. When Angel of Mercy enters the battlefield, you gain 3 life. 3/3"
        self.abilities = ["Flying"]
        self.targets = []
        self.owner = owner
        self.power = 3
        self.tou = 3

    def effect(self, targets):
        self.owner.gainLife(3)

class GuardianofPilgrims(Card):
    def __init__(self,owner):
        self.name = "Guardian of Pilgrims"
        self.cost = "1W"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Spirit Cleric"
        self.text = "When Guardian of Pilgrims enters the battlefield, target creature gets +1/+1 until end of turn. 2/2"
        self.abilities = []
        self.targets = [("OwnCreature", "OpponentCreature")]
        self.owner = owner
        self.power = 2
        self.tou = 2

    def effect(self, targets):
        targets[0].curPower = targets[0].curPower + 1
        targets[0].curTou = targets[0].curTou + 1

class NestRobber(Card):
    def __init__(self,owner):
        self.name = "Nest Robber"
        self.cost = "1R"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Dinosaur"
        self.text = "Haste. 2/1"
        self.abilities = ["Haste"]
        self.targets = []
        self.owner = owner
        self.power = 2
        self.tou = 1

class LightningHounds(Card):
    def __init__(self,owner):
        self.name = "Lightning Hounds"
        self.cost = "2RR"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Hound"
        self.text = "First strike. 3/2"
        self.abilities = ["First strike"]
        self.targets = []
        self.owner = owner
        self.power = 3
        self.tou = 2

class FlametongueKavu(Card):
    def __init__(self,owner):
        self.name = "Flametongue Kavu"
        self.cost = "3R"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Kavu"
        self.text = "When Flametongue Kavu enters the battlefield, it deals 4 damage to target creature. 4/2"
        self.abilities = []
        self.targets = [("OwnCreature", "OpponentCreature")]
        self.owner = owner
        self.power = 4
        self.tou = 2

    def effect(self, targets):
        targets[0].takeDamage(4)

class PathofPeace(Card):
    def __init__(self, owner):
        self.name = "Path of Peace"
        self.cost = "3W"
        self.supertype = ""
        self.ctype = "Sorcery"
        self.subtype = ""
        self.text = "Destroy target creature. It's owner gains 4 life."
        self.targets = [("OwnCreature", "OpponentCreature")]
        self.owner = owner

    def effect(self, targets):
        targets[0].owner.gainLife(4)
        targets[0].putOnGraveyard()
