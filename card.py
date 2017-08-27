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

    def cmc(self, cost):
        m = re.match("(\d?)(\w*)", cost).groups()
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

    def abtilities(self):
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

class VolcanicHammer(Card):
    def __init__(self, owner):
        self.name = "Volcanic Hammer"
        self.cost = "1R"
        self.supertype = ""
        self.ctype = "Sorcery"
        self.subtype = ""
        self.text = "Volcanic Hammer deals 3 damage to target creature or player."
        self.targets = [("Creature", "Player")]
        self.owner = owner

    def effect(self, target):
        target.takeDamage(3)

class FoulImp(Card):
    def __init__(self, owner):
        self.name = "Foul Imp"
        self.cost = "BB"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Imp"
        self.text = "Flying. When Foul Imp enters the battlefield you lose 2 life. 2/2"
        self.abilities = ["Flying"]
        self.owner = owner

    def effect(self):
        self.owner.loseLife(2)
