import random

class Player:

    def __init__(self, number):
        self.life = 20
        self.hand = []
        self.library = []
        self.lose = False
        self.number = number
        self.battlefield = []

    def setLibrary(self, library):
        self.library = library

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

    def setActive(self, b):
        self.active = b

    def isActive(self):
        return self.active

    def showHand(self):
        for card in self.hand:
            print(card)
        return

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
