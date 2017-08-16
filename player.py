import random
import utils

class Player:

    def __init__(self, number):
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
            print(str(i) + ") " + card)
            i += 1
        return

    def scry():
        card = self.library.pop()
        s = ""
        while s != "1" or s != "2":
            s = input("The top card is " + card.name + ". Do you want to (1) keep it in top or (2) put it at the bottom of the library?")
            if s == "1":
                self.library.append(card)
            elif s == "2":
                self.library.insert(0, card)

    def mulligan(self):

        n = len(self.hand)
        if n == 0:
            return True

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
