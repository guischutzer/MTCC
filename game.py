

import argparse
import random

# parser = argparse.ArgumentParser(description='Magic: the Gathering utilitary')
# parser.add_argument('deck1',
#                     help='Deck file (player 1)')
# parser.add_argument('deck2',
#                     help='Deck file (player 2)')
#
# args = parser.parse_args()
# db = DataBase()

class Player:

    def __init__(self, number):
        self.life = 20
        self.hand = []
        self.library = []
        self.lose = False
        self.number = number

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


    def mulligan(self):

        n = len(self.hand)
        if n == 0:
            return True

        self.showHand()
        c = input("Keep hand? (Y/n)")
        if c == "y" or c == "Y" or c == "":
            print("\n")
            return True

        while self.hand != []:
            self.library.append(self.hand.pop())

        self.shuffle()
        self.draw(n - 1)

        return False

class Game:

    def __init__(self, deck1, deck2):
        self.player_1 = Player(1)
        self.player_2 = Player(2)

        self.player_1.setLibrary(self.readDeck(deck1))
        self.player_2.setLibrary(self.readDeck(deck2))

        self.pqueue = []
        activePlayer = random.randrange(1, 3)
        self.setActivePlayer(activePlayer)

        self.player_1.shuffle()
        self.player_2.shuffle()
        self.player_1.draw(7)
        self.player_2.draw(7)

        keep = [False, False]
        while not all(keep):
            keep = [self.pqueue[0].mulligan(), self.pqueue[1].mulligan()]

    def readDeck(self, filename):

        library = []
        f = open(filename, 'r')

        deckList = f.readlines()
        for entry in deckList:
            entry = entry.split(" ")
            number = int(entry[0])
            name = " ".join(entry[1:])
            for i in range(number):
                library.append(name)

        return library

    def changeActivePlayer(self):
        self.player_1.setActive(not player_1.isActive())
        self.player_2.setActive(not player_2.isActive())
        self.pqueue = pqueue.reverse()

    def setActivePlayer(self, activePlayer):
        self.player_1.setActive(activePlayer == 1)
        self.player_2.setActive(activePlayer == 2)

        if activePlayer == 1:
            self.pqueue.append(self.player_1)
            self.pqueue.append(self.player_2)
        else:
            self.pqueue.append(self.player_2)
            self.pqueue.append(self.player_1)

jogo = Game("deck1.txt", "deck2.txt")
