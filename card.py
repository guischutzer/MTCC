import re
import colors

class Card:

    def __init__(self, name, cost, text, ctype, supertype, subtype, power, tou):
        self.name = name
        self.cost = cost
        self.text = text
        self.ctype = ctype
        self.supertype = supertype
        self.subtype = subtype
        self.power = power
        self.tou = tou
        self.targets = []

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

    def __str__(self):
        s = self.name + "\n"
        s += self.cost + "\n"
        s += self.text + "\n"
        s += self.ctype + "\n"
        s += self.supertype + "\n"
        s += self.subtype + "\n"
        s += self.power + "\n"
        s += self.tou + "\n"
        return s

class
