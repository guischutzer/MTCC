

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

def confirm(s):
    return s == "y" or s == "Y" or s == "Yes"

class Game:

    def __init__(self, deck1, deck2):
        self.player_1 = Player(1)
        self.player_2 = Player(2)

        self.player_1.setLibrary(self.readDeck(deck1))
        self.player_2.setLibrary(self.readDeck(deck2))

        self.pqueue = []
        actPlayerID = random.randrange(1, 3)
        self.setActivePlayer(actPlayerID)

        self.player_1.shuffle()
        self.player_2.shuffle()
        self.player_1.draw(7)
        self.player_2.draw(7)

        keep = [False, False]
        while not all(keep):
            keep = [self.pqueue[0].mulligan(), self.pqueue[1].mulligan()]

        n = 0
        gameState = True # flag for ending the game (name may change)
        while gameState:
            n += 1
            gameState = self.turnRoutine(n)
            self.changeActivePlayer()

    def turnRoutine(self, tNumber):

        activePlayer = self.pqueue[0]
        opponent = self.pqueue[1]

        ## Beggining Phase
        # Untap - untap permanents of active player
        for permanent in activePlayer.battlefield:
            permanent.untap()

        # Upkeep (not present in version alpha)

        # Draw
        if tNumber > 1:
            activePlayer.draw()

        ## Precombat Main Phase

        ## Combat Phase
        # Beggining of Combat (not present in version alpha)

        # Declare Attackers
        attackers = []
        for permanent in activePlayer.battlefield:
            if permanent.canAttack():
                c = input("Declare " + permanent.card.name + " as an attacker? (y/N) ")
                if confirm(c):
                    permanent.attack()
                    attackers.append(permanent)


        # Declare Blockers
        combatPairings = {}
        for attacker in attacking:
            c = input("Block " + attacker.card.name + "? (y/N) ")
            if confirm(c):
                for permanent in opponent.battlefied:
                    if permanent.canBlock(attacker):
                        c = input("With " + b.card.name + "? (y/N)":
                        if confirm(c):
                            permanent.block(attacker)

        # Combat Damage
        # - First & Double Strike Damage

        # - Combat Damage

        # End of Combat

        ## Postcombat Main Phase

        ## End Phase
        # End

        # Cleanup

        return True

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

    def setActivePlayer(self, ID):
        self.player_1.setActive(ID == 1)
        self.player_2.setActive(ID == 2)

        if ID == 1:
            self.pqueue.append(self.player_1)
            self.pqueue.append(self.player_2)
        else:
            self.pqueue.append(self.player_2)
            self.pqueue.append(self.player_1)



jogo = Game("deck1.txt", "deck2.txt")
