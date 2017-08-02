import random

class Player:

    def __init__(self, number):
        self.life = 20
        self.hand = []
        self.library = []
        self.lose = False
        self.number = number
        self.battlefield = []
        self.active = False

    def setLibrary(self, library):
        self.library = library

    def untapStep(self):
        self.untappedLands = 0
        for permanent in self.battlefield:
            if permanent.ctype == "Land" and permanent.tapped == False:
                self.untappedLands += 1

    def draw(self, n=1):
        if (len(self.library) == 0):
            self.lose = True
            return

        for i in range(n):
            card = self.library.pop()
            self.hand.append(card)

    def shuffle(self):
        random.shuffle(self.library)

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
            asterisk = ''
            if self.canPlay(card):
                asterisk = '*'
            print(i, asterisk, ") ", card)
            i += 1
        return

    def canPlay(self, card, landDrop):

        if not card.validTargets():
            return False

        if card.ctype == "Land":
            if landDrop == True:
                return False
            else
                return True

        if self.cost <= self.untappedLands:
            return True

        return False

    def play(self, card):
        mana = 0
        while mana < card.cost:
            for permanent in self.battlefield:
                if permanent.ctype == "Land":
                    permanent.tap()
                    self.untappedLands -= 1
                    mana += 1



    def scry():
        card = self.library.pop()
        s = ""
        while s != "1" or s != "2":
            s = input("The top card is " + card.name ". Do you want to (1) keep it in top or (2) put it at the bottom of the library?")
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
        if confirm(c) or c == "":
            print("\n")
            if n < 7:
                self.scry()
            return True

        while self.hand != []:
            self.library.append(self.hand.pop())

        self.shuffle()
        self.draw(n - 1)

        return False
