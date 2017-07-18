

import argparse
import random

parser = argparse.ArgumentParser(description='Magic: the Gathering utilitary')
parser.add_argument('deck1',
                    help='Deck file (player 1)')
parser.add_argument('deck2',
                    help='Deck file (player 2)')

args = parser.parse_args()
db = DataBase()

class Game:

    def __init__(self, deck1, deck2):
        self.player_1 = Player(1)
        self.player_2 = Player(2)

        player_1.setLibrary(readDeck(deck1))
        player_2.setLibrary(readDeck(deck2))

        self.pqueue = []
        activePlayer = randrange(1, 3)
        setActivePlayer(activePlayer)

        keep = [False, False]
        while not all(keep):
            keep = [pqueue[0].mulligan(), pqueue[1].mulligan()]



    def readDeck(self, filename):

        library = []
        f = open(filename, 'r')

        deckList = f.readlines()
        for entry in deckList:
            entry = entry.split(" ")
            number = int(entry[0])
            name = " ".join(entry[1:])
            for i in range(number):
                library.append(db.addCard(name))

        return library

    def changeActivePlayer(self):
        self.player_1.setActive(!player_1.isActive())
        self.player_2.setActive(!player_2.isActive())
        self.pqueue = pqueue.reverse()

    def setActivePlayer(self, activePlayer):
        self.player_1.setActive(activePlayer == 1)
        self.player_2.setActive(activePlayer == 2)

        if activePlayer == 1:
            pqueue.append(self.player_1)
            pqueue.append(self.player_2)
        else:
            pqueue.append(self.player_2)
            pqueue.append(self.player_1)

class Player:

    def __init__(self, id):
        self.life = 20
        self.hand = []
        self.library = []
        self.lose = False

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

    def start(self):
        shuffle()
        draw(7)
        self.keep = False

    def mulligan(self):
