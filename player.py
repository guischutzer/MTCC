import random
import utils

class Player:

    def __init__(self, number):
        self.name = 'Unknown Player'
        self.life = 20
        self.hand = []
        self.library = []
        self.lose = False
        self.number = number
        self.creatures = []
        self.lands = []
        self.active = False
        self.graveyard = []
        self.untappedLands = 0

    def rename(self, name):
        self.name = name

    def setLibrary(self, library):
        self.library = library

    def untapStep(self):

        for land in self.lands:
            land.untap()

        for creature in self.creatures:
            creature.untap()

    def draw(self, n=1):
        if (len(self.library) == 0):
            self.lose = True
            return

        for i in range(n):
            card = self.library.pop()
            self.hand.append(card)

    def discard(self, card):
        self.hand.remove(card)
        self.graveyard.append(card)

    def shuffle(self):
        random.shuffle(self.library)

    def isPlayer(self):
        return True

    def gainLife(self, x):
        self.life += x

    def loseLife(self, x):
        self.gainLife(-x)

    def takeDamage(self, x):
        self.loseLife(x)

    def setActive(self, b):
        self.active = b

    def isActive(self):
        return self.active

    def cardsInHand(self):
        return len(self.hand)

    def showHand(self):
        i = 1
        for card in self.hand:
            print(str(i) + ") " + card.name)
            i += 1
        return

    def play(self, card):
        if card.ctype == "Land":
            permanent = Land(card, self)
            self.lands.append(permanent)
            return permanent

        if card.ctype == "Creature":
            permanent = Creature(card, self)
            self.creatures.append(permanent)
            return permanent

        else:
            self.graveyard.append(card)
            return None

    def scry(self):
        card = self.library.pop()
        s = ""
        s = input("The top card is " + card.name + ". Do you want to put it at the bottom of the library? (y/n) ")
        if utils.confirm(s):
            self.library.insert(0, card)
        else:
            self.library.append(card)


    def mulligan(self):

        n = len(self.hand)
        if n == 0:
            return True

        print ("\nPlayer " + self.name + ":")
        self.showHand()
        c = input("Keep hand? (Y/n)")
        if utils.confirm(c) or c == "":
            print("\n")
            if n < 7:
                self.scry()
            return True

        while self.hand != []:
            self.library.append(self.hand.pop())

        self.shuffle()
        self.draw(n - 1)

        return False
