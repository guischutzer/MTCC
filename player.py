import random
import utils
import collections
import copy as c
from card import Card

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
        self.landDrop = False
        self.lost = False

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
            self.lost = True
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
            chosenTargets.append(chosenTarget)

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
                return 'Print'
            c = int(c)
            if c > 0 and c <= len(self.hand):
                card = self.hand[c - 1]
                if isLegalAction(card, legalActions):
                    legalTargets = card.legalTargets
                    targets = self.chooseTargets(legalTargets)
                    action = []
                    action.append(card)
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

        return 'Pass'

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

    def update(self, state, legalActions, nextState, nextLegalActions, reward):
        return

class MulliganAgent(Player):

    def __init__(self, number, onThePlay, verbosity=False):
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
        self.landRewards = []
        self.landDrop = False
        self.lost = False

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

    def printMainAction(self, action):
        if action[0] is 'Pass':
            print("Agent " + self.name + " passes priority.")
            return action[0]
        card = action[0]
        targets = action[1]
        print("Agent " + self.name + " plays " + action[0].name, end='')
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

    def printAttackers(self, attackers):
        if attackers == []:
            print("Player " + self.name + " has declared no attacking creatures.")
            return attackers

        print("Player " + self.name + " has declared:")
        for creature in attackers:
            print(" - " + creature.stats())
        print("as attacker(s).")

    def printBlockers(self, action, combatPairings):
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

    def printAssignedBlockOrder(self, combatPairings, attacker):
        print("Player " + self.name + " blocks " + attacker.stats())
        i = 1
        for blocker in combatPairings[attacker]:
            print(" - " + utils.getOrdinal(i) + " with " + blocker.stats())
            i += 1


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

    def mainPhaseAction(self, state, legalActions):
        if not legalActions:
            return ['End']
        index = random.randrange(0, len(legalActions))
        action = legalActions[index]
        self.printMainAction(action)
        return action

    def declareAttackers(self, legalActions):

        if len(legalActions) == 0:
            print("Player " + self.name + " has declared no attacking creatures.")
            return []

        index = random.randrange(0, len(legalActions))
        attackers = legalActions[index]
        self.printAttackers(attackers)

        return attackers

    def declareBlockers(self, legalActions, combatPairings):

        if len(legalActions) == 0:
            return {}

        index = random.randrange(0, len(legalActions))
        action = legalActions[index]
        combatPairings = self.printBlockers(action, combatPairings)

        return combatPairings

    def assignBlockOrder(self, combatPairings):

        for attacker in combatPairings:
            n = len(combatPairings[attacker])
            if n > 1:
                random.shuffle(combatPairings[attacker])
                self.printAssignedBlockOrder(combatPairings, attacker)

        return combatPairings

    def discardExcess(self):

        while self.cardsInHand() > 7:
            index = random.randrange(0, self.cardsInHand())
            self.discard(self.hand[index])

class QLearningAgent(RandomAgent):

    def __init__(self, number, onThePlay, verbosity, epsilon=0.8, alpha=0.5, discount=0.8, weights=collections.Counter()):
        super().__init__(number, onThePlay, verbosity)
        self.epsilon = epsilon
        self.alpha = alpha
        self.discount = discount
        self.weights = weights

    def computeActionFromQValues(self, state, legalActions):
        qMax = None
        maxActions = []
        if state.game.activePlayer is not self:
             return ['Wait']

        print("Choosing action:")
        for i in range(len(legalActions)):
            curState = c.deepcopy(state)
            fakeAction = curState.game.activePlayer.currentActions[i]
            if isinstance(fakeAction[0], Card):
                curState.game.play(fakeAction)
            qValue = self.getQValue(curState, i)
            action = legalActions[i]
            print("action: " + str(action))
            print("qValue: " + str(qValue))
            if qMax == None:
                qMax = qValue
                maxActions = [action]
            elif qValue > qMax:
                qMax = qValue
                maxActions = [action]
            elif qValue == qMax:
                maxActions.append(action)

        if not maxActions:
            return None

        return random.choice(maxActions)


    def mainPhaseAction(self, state, legalActions):
        action = self.computeActionFromQValues(state, legalActions)
        self.printMainAction(action)
        return action

    # def declareAttackers(self, state, legalActions, combatPairings):
    #
    #     if len(legalActions) == 0:
    #         print("Player " + self.name + " has declared no attacking creatures.")
    #         return []
    #
    #     attackers = self.getActionFromQValues(state, legalActions)
    #     self.printAttackers(attackers)
    #
    #     return attackers

    # def declareBlockers(self, state, legalActions, combatPairings):
    #
    #     if len(legalActions) == 0:
    #         return {}
    #
    #     action = self.getActionFromQValues(state, legalActions)
    #     combatPairings = self.printBlockers(action, combatPairings)
    #
    #     return combatPairings

    def getFeatures(self, state):

        features = collections.Counter()

        features["#-of-lands"] = len(state.getLands())
        features["#-of-untappedLands"] = state.getUntappedLands()
        features["#-of-own-creatures"] = len(state.getOwnCreatures())
        features["#-of-opponent-creatures"] = len(state.getOpponentCreatures())

        return features

    def getWeights(self):
        return self.weights

    def getQValue(self, state, action):
        qValue = 0
        if state.isTerminal() or if action[0] = 'Wait':
            return qValue

        feats = self.getFeatures(state)
        weights = self.getWeights()

        for entry in feats:
            qValue += weights[entry] * feats[entry]

        return qValue

    def update(self, state, action, nextState, nextLegalActions, reward):
        state.stats()
        print(str(action) + "-->")
        nextState.stats()
        maxAction = self.computeActionFromQValues(nextState)
        feats = self.getFeatures(nextState)

        delta = (reward + self.discount * self.getQValue(nextState, maxAction)) - self.getQValue(state, action)
        print(reward)
        for i in feats:
            self.weights[i] = self.weights[i] + self.alpha * delta * feats[i]
        print(self.weights)
        print(feats)

class State:

    def __init__(self, game, lossReward=-100, winReward=100, phase='Main'):
        self.game = game
        self.player = game.activePlayer
        self.opponent = game.opponent
        self.lossReward = lossReward
        self.winReward = winReward
        self.phase = phase

    def getReward(self):
        if self.player.lost:
            return self.lossReward
        if self.opponent.lost:
            return self.winReward
        lifeDiff = self.getOwnLifeTotal() - self.getOpponentLifeTotal()
        powerDiff = self.getPowerTotal(self.player.creatures) - self.getPowerTotal(self.opponent.creatures)
        return (lifeDiff + powerDiff)/100

    def getLands(self):
        return self.player.lands

    def getUntappedLands(self):
        return self.player.untappedLands

    def getOwnCreatures(self):
        return self.player.creatures

    def getOpponentCreatures(self):
        return self.opponent.creatures

    def getOwnLifeTotal(self):
        return self.player.life

    def getOpponentLifeTotal(self):
        return self.opponent.life

    def getPowerTotal(self, creatures):
        total = 0
        for creature in creatures:
            total += creature.curPower
        return total

    def getToughnessTotal(self, creatures):
        total = 0
        for creature in creatures:
            total += creature.curTou
        return total

    def isTerminal(self):
        if self.player.lost or self.opponent.lost:
            return True

        return False

    def stats(self):
        print(self.player.name + ": " + str(self.getOwnLifeTotal()) + " life")
        for creature in self.getOwnCreatures():
            print(" - " + creature.stats())
        print(self.opponent.name + ": " + str(self.getOpponentLifeTotal()) + " life")
        for creature in self.getOpponentCreatures():
            print(" - " + creature.stats())

def isLegalAction(card, legalActions):
    for action in legalActions:
        if action[0] is card:
            return True

    return False
