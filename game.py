

import argparse
import random

parser = argparse.ArgumentParser(description='Magic: the Gathering utilitary')
parser.add_argument('deck1',
                    help='Deck file (player 1)')
parser.add_argument('deck2',
                    help='Deck file (player 2)')

args = parser.parse_args()

class Game:

    def __init__(self, deck1, deck2, dbFilename='default.db'):
        self.player_1 = Player(1)
        self.player_2 = Player(2)

        self.db = DataBase(dbFilename)
        player_1.setLibrary(readDeck(deck1))
        player_2.setLibrary(readDeck(deck2))

    def readDeck(self, filename):

        library = []
        f = open(filename, 'r')

        deckList = f.readlines()
        for item in deckList:
            


class Player:

    def __init__(self, id):
        self.life = 20
        self.hand = []
        self.library = []
        self.lose = False

    def setLibrary(self, library):
        self.library = library

    def draw(self):
        if (len(self.library) == 0):
            self.lose = True
            return

        card = self.library.pop()
        self.hand.append(card)

    def shuffle(self):
        random.shuffle(self.library)

    def gainLife(self, x):
        self.life += x

    def loseLife(self, x):
        self.gainLife(-x)
