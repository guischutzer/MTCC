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

class Agent(Player):

    def __init__(self, number):
        super.__init__(number)
        self.landRewards = []
        if self.onThePlay:
            self.landRewards = [-7, -3, 3, 4, 2, -1, -4, -6]
        else
            self.landRewards = [-4,  0, 5, 6, 3,  0, -3, -5]

        self.mullUtilities = [None, None, None, None, None, None, None]
        self.keepRewards  = [[None, None, None, None, None, None, None, None],
                             [None, None, None, None, None, None, None],
                             [None, None, None, None, None, None],
                             [None, None, None, None, None],
                             [None, None, None, None],
                             [None, None, None],
                             [None, None],
                             [None]]
        self.mullProbblty = [[None, None, None, None, None, None, None],
                             [None, None, None, None, None, None],
                             [None, None, None, None, None],
                             [None, None, None, None],
                             [None, None, None],
                             [None, None],
                             [None]]

    def setLibrary(self, deck):
        self.library = deck

        self.landsInLibrary = 0
        for card in self.library:
            if card.ctype is 'Land':
                self.landsInLibrary += 1

    def getKeepReward(self, hand):

        alpha = 3

        lands = 0
        nonlands = 0

        for card in hand:
            if card.ctype is 'Land':
                lands += 1
            else
                nonlands += 1

        if self.keepRewards[len(hand)][lands] is not None:
            return self.keepRewards[len(hand)][lands]

        reward = self.landRewards[lands] + alpha*len(hand)
        self.keepRewards[len(hand)][lands] = reward

        return reward

    def getMullProb(self, i, j):

        if self.mullProbblty[i][j] is not None:
            return self.mullProbblty[i][j]

        prob = utils.binom(self.landsInLibrary, j)*utils.binom(60 - self.landsInLibrary, i - j)/utils.binom(60, i)
        self.mullProbblty[i][j] = prob

        return prob

    def getMullUtility(self, i):

        if self.mullUtilities[i] is not None:
            return self.mullUtilities[i]

        utility = 0
        for j in range(i - 1):
            utility += getMullProb(i - 1, j)*getMullUtility(i - 1)

        self.mullUtilities[i] = utility

    def mulligan(self):

        n = len(self.hand)
        if n == 0:
            return True

        keepReward = getKeepReward(self.hand)
        if keepReward >= self.getMullUtility(n):
            print("\nPlayer " + self.name + " has kept this hand.")
            if n < 7:
                self.scry()
            return True

        print("\nPlayer " + self.name + " mulligans down to " + str(n - 1) + " cards.")

        while self.hand != []:
            self.library.append(self.hand.pop())

        self.shuffle()
        self.draw(n - 1)

        return False
