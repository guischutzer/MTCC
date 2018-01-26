import random
import utils
import copy as c
import queue

class Player:

    def __init__(self, ID):
        self.name = 'Unknown Player'
        self.life = 20
        self.hand = []
        self.library = []
        self.lose = False
        self.ID = ID
        self.creatures = []
        self.lands = []
        self.active = False
        self.graveyard = []
        self.untappedLands = 0
        self.landDrop = False

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
        print("Player " + self.name + " has discarded " + card.name + ".")

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

    def chooseTargets(self, legalTargets):

        chosenTargets = []

        targetNumber = 1
        for target in legalTargets:
            print("Possible targets for the target number " + str(targetNumber) + ":")
            targetNumber += 1
            optionNumber = 1
            for entry in target:
                if not isinstance(entry, Player):
                    print(entry.owner.name + "'s " + str(optionNumber) + ") " + entry.stats())
                elif entry is self:
                    print(str(optionNumber) + ") You")
                else:
                    print(str(optionNumber) + ") Opponent")
                optionNumber += 1
            c = 0
            while c < 1 or c > len(target):
                c = int(input("Choose a target: "))
            chosenTarget = target[c - 1]
            chosenTargets.append(chosenTarget.ID)

        return chosenTargets

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

    def mainPhaseAction(self, legalActions):
        c = ''

        while c != 0:
            self.showHand()
            c = input("Choose a card from your hand (0 will pass priority, 'p' prints the game state): ")
            if c == 'p':
                return ['Print', []]
            c = int(c)
            if c > 0 and c <= len(self.hand):
                index = c - 1
                card = self.hand[index]
                if isLegalAction(index, legalActions):
                    legalTargets = card.legalTargets
                    targets = self.chooseTargets(legalTargets)
                    action = []
                    action.append(index)
                    action.append(targets)
                    return action
                else:
                    if card.ctype is "Land":
                        print("Already played a land this turn.")
                    elif card.cmc() > self.untappedLands:
                        print("Not enough untapped lands.")
                    else:
                        print("There are no valid targets.")
                    c = ''

        return ['Pass']

    def printMainAction(self, source, targets):
        return

    def declareAttackers(self, legalActions):

        attackers = []
        print(self.name + ", declare attackers:")
        for creature in self.creatures:
            if creature.canAttack():
                c = input("Declare " + creature.card.name + " as an attacker? (y/N) ")
                if utils.confirm(c):
                    attackers.append(creature)

        return attackers

    def assignBlockOrder(self, combatPairings):

        for attacker in combatPairings:
            n = len(combatPairings[attacker])
            if n > 1:
                print("Declare block order for " + attacker.stats())
                auxList = []
                for blocker in combatPairings[attacker]:
                    auxList.append(blocker)
                i = 1
                combatPairings[attacker] = []
                while len(combatPairings[attacker]) < n - 1:
                    for j in range(len(auxList)):
                        print(str(j + 1) + ") " + auxList[j].stats())
                    c = 0
                    while int(c - 1) > len(auxlist) or int(c - 1) < 0:
                        c = input("Choose " + utils.getOrdinal(i) + " creature to assign damage: ")
                    creature = auxList[c - 1]
                    auxList.remove(creature)
                    combatPairings[attacker].append(creature)
                    i += 1
                combatPairings[attacker].append(auxList[0])

        return combatPairings


    def declareBlockers(self, legalActions, combatPairings):

        print(self.name + ", declare blockers: ")
        for attacker in combatPairings:
            for creature in self.creatures:
                if creature.canBlock(attacker):
                    c = input("Block " + attacker.card.name + " with " + creature.card.name + "? (y/N) ")
                    if utils.confirm(c):
                        creature.block(attacker)
                        combatPairings[attacker].append(creature)

        return combatPairings

    def discardExcess(self):
        self.showHand()
        c = 0
        while c < 1 or c > self.cardsInHand():
            c = int(input("Choose a card from your hand to discard: "))
        card = self.hand[c - 1]
        self.discard(card)

    def canTarget(self, targets, oppCreatures):

        ownCreatures = c.copy(self.creatures)

        opponentCreatures = c.copy(oppCreatures)
        for creature in opponentCreatures:
            if creature.hasHexproof():
                opponentCreatures.remove(creature)

        for target in targets:
            foundTarget = False
            if "Player" not in target and "Opponent" not in target:
                for targetType in target:
                    if foundTarget:
                        break
                    if targetType == "Creature":
                        if len(ownCreatures) > 0:
                            ownCreatures.pop()
                            foundTarget = True
                        elif len(opponentCreatures) > 0:
                            opponentCreatures.pop()
                            foundTarget = True
                    elif targetType == "OwnCreature":
                        if len(ownCreatures) > 0:
                            ownCreatures.pop()
                            foundTarget = True
                    elif targetType == "OpponentCreature":
                        if len(opponentCreatures) > 0:
                            opponentCreatures.pop()
                            foundTarget = True
                if not foundTarget:
                    return False

        return True

class MulliganAgent(Player):

    def __init__(self, ID, onThePlay, verbosity=False):
        self.name = 'Unknown Player'
        self.life = 20
        self.hand = []
        self.library = []
        self.lose = False
        self.ID = ID
        self.creatures = []
        self.lands = []
        self.active = False
        self.graveyard = []
        self.untappedLands = 0
        self.landRewards = []
        self.landDrop = False

        self.verbose = verbosity
        self.onThePlay = onThePlay

        if self.onThePlay:
            self.landRewards = [-7, -3, 3, 4, 2, -1, -4, -6]
        else:
            self.landRewards = [-4,  0, 5, 6, 3,  0, -3, -5]

        self.mulliganValue = [[None, None, None, None, None, None, None, None],
                               [None, None, None, None, None, None, None],
                               [None, None, None, None, None, None],
                               [None, None, None, None, None],
                               [None, None, None, None],
                               [None, None, None],
                               [None, None],
                               [None]]
        self.keepRewards =  [[None, None, None, None, None, None, None, None],
                              [None, None, None, None, None, None, None],
                              [None, None, None, None, None, None],
                              [None, None, None, None, None],
                              [None, None, None, None],
                              [None, None, None],
                              [None, None],
                             [None]]
        self.mulliganProb = [[None, None, None, None, None, None, None],
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

    def getHandReward(self, hand):

        lands = 0

        for card in hand:
            if card.ctype is 'Land':
                lands += 1

        return self.getKeepReward(len(hand), lands)

    def getKeepReward(self, i, j):

        alpha = 3.5

        if self.keepRewards[7 - i][j] is not None:
            return self.keepRewards[7 - i][j]

        reward = self.landRewards[j] + alpha*i
        self.keepRewards[7 - i][j] = reward

        return reward


    def mulliganValueIteration(self):

        for i in range(7, -1, -1):
            for j in range(i + 1):
                self.mulliganValue[7 - i][j] = self.getKeepReward(i, j)

        for epoch in range(1, 9):
            for i in range(7, -1, -1):
                for j in range(i + 1):
                    mullValue = 0
                    for jLine in range(i):
                        mullValue += self.getMulliganProb(i - 1, jLine)*self.mulliganValue[7 - (i - 1)][jLine]
                    if mullValue >= self.getKeepReward(i, j):
                        self.mulliganValue[7 - i][j] = mullValue


    def getMulliganProb(self, i, j):

        if self.mulliganProb[6 - i][j] is not None:
            return self.mulliganProb[6 - i][j]

        prob = utils.binom(self.landsInLibrary, j)*utils.binom(60 - self.landsInLibrary, i - j)/utils.binom(60, i)
        self.mulliganProb[6 - i][j] = prob

        return prob

    def getMulliganValue(self, hand):

        lands = 0

        for card in hand:
            if card.ctype is 'Land':
                lands += 1

        return self.mulliganValue[7 - len(hand)][lands]

    def mulligan(self):

        if self.mulliganValue[0][0] is None:
            self.mulliganValueIteration()

        if self.verbose:
            print(self.mulliganValue)

        n = len(self.hand)
        if n == 0:
            return True

        keepReward = self.getHandReward(self.hand)
        mullValue = self.getMulliganValue(self.hand)

        if keepReward == mullValue:
            print("\nAgent " + self.name + " has kept this hand.")
            if n < 7:
                self.scry()
            if self.verbose:
                print(str(self.mulliganValue) + "\n")
                print(str(self.mulliganProb) + "\n")
                print(str(self.keepRewards))
            return True

        print("\nAgent " + self.name + " mulligans down to " + str(n - 1) + " cards.")

        while self.hand != []:
            self.library.append(self.hand.pop())

        self.shuffle()
        self.draw(n - 1)


        return False

    def scry(self):
        card = self.library.pop()
        bottom = random.choice([True, False])
        if bottom:
            self.library.insert(0, card)
            print("\nAgent " + self.name + " puts the top card of its library at the bottom.")
        else:
            self.library.append(card)
            print("\nAgent " + self.name + " keeps the top card of its library.")

class RandomAgent(MulliganAgent):

    def mainPhaseAction(self, legalActions):
        index = random.randrange(0, len(legalActions))
        action = legalActions[index]
        return action

    def printMainAction(self, card, targets):
        if card == 'Pass':
            return
        print("Player " + self.name + " plays " + card.name, end='')
        if len(targets) > 0:
            print(" targetting ", end='')
            for i in range(len(targets)):
                if not isinstance(targets[i], Player):
                    print(targets[i].card.name, end='')
                else:
                    print(targets[i].name, end='')
                if len(targets[i+1:]) == 1:
                    print(" and ", end='')
                elif len(targets[i+1:]) > 1:
                    print(", ", end='')
        print(".")

    def declareAttackers(self, legalActions):

        if len(legalActions) == 0:
            print("Player " + self.name + " has declared no attacking creatures.")
            return []

        index = random.randrange(0, len(legalActions))
        attackers = legalActions[index]

        if attackers == []:
            print("Player " + self.name + " has declared no attacking creatures.")
            return attackers

        print("Player " + self.name + " has declared:")
        for creature in attackers:
            print(" - " + creature.stats())
        print("as attacker(s).")
        return attackers

    def assignBlockOrder(self, combatPairings):

        for attacker in combatPairings:
            n = len(combatPairings[attacker])
            if n > 1:
                random.shuffle(combatPairings[attacker])
                print("Player " + self.name + " blocks " + attacker.stats())
                i = 1
                for blocker in combatPairings[attacker]:
                    print(" - " + utils.getOrdinal(i) + " with " + blocker.stats())
                    i += 1

        return combatPairings

    def declareBlockers(self, legalActions, combatPairings):

        if len(legalActions) == 0:
            return {}

        index = random.randrange(0, len(legalActions))
        action = legalActions[index]

        noBlocks = True
        print("Player " + self.name + " has declared ", end='')
        for i in range(len(self.creatures)):
            blockingCreature = self.creatures[i]
            blockedCreature = action[i]
            if blockedCreature != []:
                noBlocks = False
                print("")
                print(" - " + blockingCreature.stats() + " blocking " + blockedCreature.stats(), end='')
                combatPairings[blockedCreature].append(blockingCreature)

        if noBlocks:
            print("no blockers.")
        else:
            print("")
        return combatPairings

    def discardExcess(self):

        while self.cardsInHand() > 7:
            index = random.randrange(0, self.cardsInHand())
            self.discard(self.hand[index])

class SearchAgent(RandomAgent):

    def breadthFirstSearch(self, startState):

        q = queue.Queue()
        q.put(startState)
        maxReward = 0
        actionPath = []

        while not q.empty():
            state = q.get()
            if state.isTerminal():
                reward = state.getReward()
                if reward >= maxReward:
                    maxreward = reward
                    actionPath = state.getPath()
            else:
                for s in state.getChildren():
                    q.put(s)

        return actionPath


def isLegalAction(card, legalActions):
    for action in legalActions:
        if action[0] is card:
            return True

    return False
