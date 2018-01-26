import argparse
import random
from player import *
from card import *
from permanent import *
import utils
from copy import copy
import re

class Game:

    # A new game takes the following arguments:
    # - agent1/agent2 is the type of each agent
    # - deck1/deck2 are the deck files
    # - verbosity prints extra data
    # - choosename is used to input different names for the players
    def __init__(self, agent1, deck1, agent2, deck2, verbosity, choosename):

        actPlayerID = random.randrange(-1, 1)
        self.permanentID = 0

        # Players initialization
        if agent1 is None:
            self.player_1 = Player(0)
        elif agent1 == "random" or agent1 == "Random":
            self.player_1 = RandomAgent(0, actPlayerID is 0, verbosity)
        elif agent1 == "search" or agent1 == "Search":
            self.player_1 = SearchAgent(0, actPlayerID is 0, verbosity)
        else:
            self.player_1 = MulliganAgent(0, actPlayerID is 0, verbosity)

        if agent2 is None:
            self.player_2 = Player(-1)
        elif agent2 == "random" or agent2 == "Random":
            self.player_2 = RandomAgent(-1, actPlayerID is -1, verbosity)
        elif agent2 == "search" or agent2 == "Search":
            self.player_2 = SearchAgent(-1, actPlayerID is -1, verbosity)
        else:
            self.player_2 = MulliganAgent(-1, actPlayerID is -1, verbosity)

        if choosename:
            name1 = input("Choose a name for Player 1: ")
            name2 = input("Choose a name for Player 2: ")
        else:
            name1 = "Red"
            name2 = "White"

        self.player_1.rename(name1)
        self.player_2.rename(name2)

        self.readDeck(deck1, self.player_1)
        self.readDeck(deck2, self.player_2)

        self.activePlayer = self.setActivePlayer(actPlayerID)
        self.opponent = self.opponentOf(self.activePlayer)

        # Each player shuffles its library and draws seven cards
        self.player_1.shuffle()
        self.player_2.shuffle()
        self.player_1.draw(7)
        self.player_2.draw(7)

        print("\nPlayer " + self.activePlayer.name + " starts the game.")

        # Mulligan is done until both players have kept their hands
        p1keep = False
        p2keep = False
        while  not p1keep or not p2keep:
            if not p1keep:
                p1keep = self.activePlayer.mulligan()
            if not p2keep:
                p2keep = self.opponent.mulligan()

        # Proper game starts
        n = 0
        endGame = False # flag for ending the game
        while not endGame:
            n += 1
            endGame = self.turnRoutine(n)
            self.changeActivePlayer()

    # turnRoutine(tNumber):
    # calls the necessary methods in the correct order and deals
    # with events like a normal Magic turn
    def turnRoutine(self, tNumber):


        activePlayer = self.activePlayer
        opponent = self.opponent

        activePlayer.landDrop = False

        ## Beggining Phase
        # Untap - untap permanents of active player
        print("----------------------------------------------------------")
        print("Turn " + str(tNumber) + " (" + activePlayer.name + ")")

        for creature in activePlayer.creatures:
            creature.untap()
            creature.removeSickness()

        for land in activePlayer.lands:
            land.untap()
            land.removeSickness()

        # Upkeep
        if self.checkSBA():
            return True

        # Draw
        if tNumber > 1:
            activePlayer.draw()
        if self.checkSBA():
            return True

        ## Precombat Main Phase
        print("----------------------------------------------------------")
        print("Precombat Main Phase")
        print("----------------------------------------------------------")

        # Main Phase method
        if self.mainPhase():
            return True

        ## Combat Phase

        print("----------------------------------------------------------")
        print("Combat Phase")
        print("----------------------------------------------------------")

        # Declare Attackers - Active Player

        # Get all legal actions in the form of:
        # [creature1 - attacking or not, creature2 - attacking or not, ...]
        legalActions = self.getAttackingActions()
        # Active player chooses how creatures attack
        attackers = activePlayer.declareAttackers(legalActions)

        # combatPairings pair attackers with their assigned blockers
        combatPairings = {}
        for creature in attackers:
            creature.attack()
            combatPairings[creature] = []

        # Declare Blockers - Not Active Player

        # Similarly, legal actions for blocking are all the
        # arrangements possible for each of its creatures to block
        # the opponent's attacking creatures. Each type of player/agent
        # then chooses the action differently
        legalActions = self.getBlockingActions(attackers)
        combatPairings = opponent.declareBlockers(legalActions, combatPairings)

        ## Choosing Block Order - Active Player
        combatPairings = activePlayer.assignBlockOrder(combatPairings)

        # Combat Damage
        # - First & Double Strike Damage
        # All the first-strikers and double-strikers deal first strike damage
        for attacker in combatPairings:

            if attacker.hasFirstStrike() or attacker.hasDoubleStrike():
                remainingDamage = attacker.curPower

                for blocker in combatPairings[attacker]:
                    neededDamage = blocker.curTou - blocker.damage
                    if attacker.hasDeathtouch():
                        neededDamage = 1
                    if remainingDamage > 0:
                        if remainingDamage > neededDamage:
                            attacker.dealDamage(blocker, neededDamage)
                            remainingDamage -= neededDamage

                if combatPairings[attacker] != [] and not attacker.hasTrample():
                    attacker.dealDamage(blocker, remainingDamage)

                else:
                    attacker.dealDamage(opponent, remainingDamage)

            for blocker in combatPairings[attacker]:
                if blocker.hasFirstStrike() or blocker.hasDoubleStrike():
                    blocker.dealDamage(attacker, blocker.curPower)

        if self.checkSBA():
            return True

        # - Combat Damage
        # All the double-strikers and not-first-strikers deal combat damage
        for attacker in combatPairings:

            if not attacker.hasFirstStrike() or attacker.hasDoubleStrike():
                remainingDamage = attacker.curPower

                for blocker in combatPairings[attacker]:
                    neededDamage = blocker.curTou - blocker.damage
                    if attacker.hasDeathtouch():
                        neededDamage = 1
                    if remainingDamage > 0:
                        if remainingDamage > neededDamage:
                            attacker.dealDamage(blocker, neededDamage)
                            remainingDamage -= neededDamage

                if combatPairings[attacker] != [] and not attacker.hasTrample():
                    attacker.dealDamage(blocker, remainingDamage)

                else:
                    attacker.dealDamage(opponent, remainingDamage)

            for blocker in combatPairings[attacker]:
                if not blocker.hasFirstStrike() or blocker.hasDoubleStrike():
                    blocker.dealDamage(attacker, blocker.curPower)

        if self.checkSBA():
            return True

        # End of Combat
        for attacker in combatPairings:
            attacker.attacking = False
            for blocker in combatPairings[attacker]:
                blocker.blocking = False

        ## Postcombat Main Phase
        print("----------------------------------------------------------")
        print("Postcombat Main Phase")
        print("----------------------------------------------------------")

        if self.mainPhase():
            return True

        ## End Phase
        print("----------------------------------------------------------")
        print("End Phase")
        print("----------------------------------------------------------")
        # End

        # per default, we have a glimpse of the board state
        # at the end of the turn
        self.printGameState()

        # Cleanup
        for permanent in activePlayer.creatures + opponent.creatures:
            permanent.removeDamage()
            permanent.resetPTA()
        if activePlayer.cardsInHand() > 7:
            activePlayer.discardExcess()

        print("")

        return False

    # Main phase method. Lets players play cards
    def mainPhase(self):

        player = self.activePlayer

        if isinstance(player, SearchAgent):
            state = State(self, [])
            actions = player.breadthFirstSearch(state)
            for i in range(len(actions) - 1):
                action = actions[i]
                card = player.hand[action[0]]
                self.play(action)
                targets = []
                for ID in action[1]:
                    targets.append(self.getPermanentFromID(ID))
                player.printMainAction(card, targets)
                if self.checkSBA():
                    return True
        else:
            action = ['','']
            # Players can play cards until they decide to pass priority
            while action[0] != 'Pass':

                # getMainActions() determine legal actions for the active player
                legalActions = self.getMainActions()
                # active player then chooses which action to perform
                action = player.mainPhaseAction(legalActions)
                targets = []

                # human player can choose to print game state
                if action[0] == 'Print':
                    self.printGameState()

                # an action of playing a card is structured as following:
                # [card, [target1, target2, ...]]
                # since action is an element of legalActions, it can be played
                if type(action[0]) == int:
                    card = player.hand[action[0]]
                    self.play(action)
                    for ID in action[1]:
                        targets.append(self.getPermanentFromID(ID))
                    player.printMainAction(card, targets)
                    if self.checkSBA():
                        return True

        print("Player " + player.name + " passes priority.")
        return False

    # getMainActions() returns active players legal actions
    # in any main phase. Actions can be
    # - ['Pass'] to pass the turn
    # - ['Print'] to print the board state
    # - [card, targets] to play a card targetting a list of legalTargets
    def getMainActions(self):

        # every player always has the option to pass
        legalActions = [['Pass', []]]
        player = self.activePlayer

        # each card in the active player's hand is a potential source of actions
        for i in range(len(player.hand)):
            card = player.hand[i]
            card.setLegalTargets([])
            # if the card can be played, there is at least one legal action to play it
            if self.canPlay(player, card):
                # finds all the legal targets for each of the card's effects
                legalTargets = self.findLegalTargets(player, card)
                card.setLegalTargets(legalTargets)
                # returns every legal combination of targets
                targetCombinations = utils.listCombinations(legalTargets)
                action = [i]
                targets = []
                if targetCombinations == []:
                    action += [targets]
                    legalActions.append(action)
                for targets in targetCombinations:
                    targetIDs = []
                    for t in targets:
                        targetIDs.append(t.ID)
                    action = [i, targetIDs]
                    legalActions.append(action)

        # if player.verbose:
        #     print("Legal actions:")
        #     for action in legalActions:
        #         print(" - " + str(action))

        return legalActions

    def canTarget(self, player, targets):

        opponent = self.opponentOf(player)
        ownCreatures = c.copy(player.creatures)

        opponentCreatures = c.copy(opponent.creatures)
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

    def findLegalTargets(self, player, card):

        legalTargets = []
        if card.targets == []:
            return legalTargets

        opponent = self.opponentOf(player)
        ownCreatures = copy(player.creatures)
        if card.ctype == 'Creature':
            ownCreatures.append(Creature(card, player, self.permanentID + 1))

        opponentCreatures = copy(opponent.creatures)
        for creature in opponentCreatures:
            if creature.hasHexproof():
                opponentCreatures.remove(creature)

        for possibleTarget in card.targets:
            curList = []
            if "OwnCreature" in possibleTarget:
                for creature in ownCreatures:
                    curList.append(creature)

            if "OpponentCreature" in possibleTarget:
                for creature in opponentCreatures:
                    curList.append(creature)

            if "Player" in possibleTarget:
                curList.append(player)
                curList.append(opponent)

            if "Opponent" in possibleTarget:
                curList.append(opponent)

            legalTargets.append(curList)

        return legalTargets

    def canPlay(self, player, card):

        if card.ctype == "Land":
            if self.activePlayer.landDrop == True:
                return False
            else:
                return True

        if card.cmc() <= player.untappedLands:
            if card.ctype == "Sorcery":
                if not self.canTarget(player, card.targets):
                    return False
                return True
            else:
                return True

        return False

    def checkSBA(self):
        for player in self.activePlayer, self.opponent:
            if player.life <= 0:
                player.lose = True
            if player.lose:
                print("Player " + player.name + " has lost the game.")
                return True

            for creature in player.creatures:
                if creature.dealtLethal or creature.destroyed:
                    player.creatures.remove(creature)
                    creature.putOnGraveyard()

            for land in player.lands:
                if land.destroyed:
                    player.lands.remove(land)
                    land.putOnGraveyard()

        return False

    def play(self, action):

        card = self.activePlayer.hand[action[0]]
        targetIDs = action[1]

        player = self.activePlayer
        opponent = self.opponent

        paidMana = 0
        player.hand.remove(card)

        if card.ctype == "Land":
            player.landDrop = True
            permanent = Land(card, player, self.newPermanentID())
            player.lands.append(permanent)
            return permanent

        for land in player.lands:
            if not land.isTapped() and paidMana < card.cmc():
                land.tap()
                paidMana += 1

        if card.ctype == "Creature":
            permanent = Creature(card, player, self.newPermanentID())
            player.creatures.append(permanent)
            targets = []
            for ID in targetIDs:
                targets.append(self.getPermanentFromID(ID))
            for target in targets:
                for i in range(len(targets)):
                    if targets[i] not in player.creatures + opponent.creatures:
                        targets[i] = permanent
                        break
            card.effect(targets)
            return permanent

        if card.ctype == "Sorcery":
            targets = []
            for ID in targetIDs:
                targets.append(self.getPermanentFromID(ID))
            card.effect(targets)
            player.graveyard.append(card)
            return None

    def newPermanentID(self):
        self.permanentID += 1
        return self.permanentID

    def getPermanentFromID(self, permanentID):
        if permanentID == 0:
            return self.player_1
        elif permanentID == -1:
            return self.player_2
        creatures = self.activePlayer.creatures
        if len(creatures) > 0:
            if creatures[0].ID <= permanentID and creatures[-1].ID >= permanentID:
                for creature in creatures:
                    if creature.ID == permanentID:
                        return creature
        creatures = self.opponent.creatures
        if len(creatures) > 0:
            if creatures[0].ID <= permanentID and creatures[-1].ID >= permanentID:
                for creature in creatures:
                    if creature.ID == permanentID:
                        return creature
        lands = self.activePlayer.lands
        if len(lands) > 0:
            if lands[0].ID <= permanentID and lands[-1].ID >= permanentID:
                for land in lands:
                    if land.ID == permanentID:
                        return land
        lands = self.opponent.lands
        if len(lands) > 0:
            if lands[0].ID <= permanentID and lands[-1].ID >= permanentID:
                for land in lands:
                    if land.ID == permanentID:
                        return land
        print("Permanent with ID " + str(permanentID) + " was not found.")
        return None


    def printGameState(self):
        print("Active Player: " + self.activePlayer.name + " - " + str(self.activePlayer.life) + " life")
        for land in self.activePlayer.lands:
            print(land.stats())
        for creature in self.activePlayer.creatures:
            print(creature.stats())

        print("\nOpponent: " + self.opponent.name + " - " + str(self.opponent.life) + " life")
        for land in self.opponent.lands:
            print(land.stats())
        for creature in self.opponent.creatures:
            print(creature.stats())

    def getAttackingActions(self):

        player = self.activePlayer

        possibleAttackers = [creature for creature in player.creatures if creature.canAttack()]
        return utils.listArrangements(possibleAttackers)

    def getBlockingActions(self, attackers):

        player = self.opponent

        possibleBlocksList = []
        for creature in player.creatures:
            possibleBlocks = [[]]
            for attacker in attackers:
                if creature.canBlock(attacker):
                    possibleBlocks.append(attacker)
            possibleBlocksList.append(possibleBlocks)

        return utils.listCombinations(possibleBlocksList)

    def readDeck(self, filename, owner):

        library = []
        f = open(filename, 'r')

        deckList = f.readlines()
        for entry in deckList:
            entry = entry.split(" ")
            number = int(entry[0])
            name = " ".join(entry[1:])
            for i in range(number):
                library.append(self.createCard(name, owner))

        owner.setLibrary(library)

    def opponentOf(self, player):
        if self.player_1 == player:
            return self.player_2

        return self.player_1

    def changeActivePlayer(self):
        self.player_1.setActive(not self.player_1.isActive())
        self.player_2.setActive(not self.player_2.isActive())
        aux = self.activePlayer
        self.activePlayer = self.opponent
        self.opponent = aux

    def setActivePlayer(self, ID):
        self.player_1.setActive(ID == 1)
        self.player_2.setActive(ID == 2)
        if self.player_1.isActive():
            return self.player_1
        return self.player_2

    def createCard(self, cardname, owner):
        card = None
        classname = re.sub("[ \n]", "", cardname)
        variables = locals()
        command = "card = " + classname + "(owner)"
        exec(command, globals(), variables)
        return variables['card']

class State:

    def __init__(self, game, actionPath):
        self.game = game
        self.actionPath = actionPath
        if len(actionPath) > 0:
            self.parentAction = actionPath[-1]
        else:
            self.parentAction = None
        self.ownLifeTotal = game.activePlayer.life
        self.opponentLifeTotal = game.opponent.life
        self.ownPower = 0
        self.opponentPower = 0
        self.landNumber = len(game.activePlayer.lands)
        self.handSize = len(game.activePlayer.hand)
        self.winReward = 100
        self.lossReward = -100
        for creature in game.activePlayer.creatures:
            self.ownPower += creature.curPower
        for creature in game.opponent.creatures:
            self.opponentPower += creature.curPower

    def isTerminal(self):
        if self.parentAction == None:
            return False
        if self.parentAction[0] == 'Pass' or self.opponentLifeTotal <= 0 or self.ownLifeTotal <= 0:
            return True
        return False

    def getChildren(self):
        children = []
        for action in self.game.getMainActions():
            game = self.game
            if action[0] != 'Pass':
                game = c.deepcopy(self.game)
                game.play(action)
            children.append(State(game, self.actionPath + [action]))
        return children

    def getReward(self):
        if self.opponentLifeTotal <= 0:
            return self.winReward
        if self.ownLifeTotal <= 0:
            return self.lossReward
        # print(self)
        reward = (self.ownLifeTotal - self.opponentLifeTotal)/4 + self.ownPower - self.opponentPower + 1.1*self.landNumber + self.handSize
        # print("Reward: " + str(reward))
        return reward

    def getPath(self):
        return self.actionPath

    def __str__(self):
        s = "own life: " + str(self.ownLifeTotal)
        s += "\nopp life: " + str(self.opponentLifeTotal)
        s += "\nown power: " + str(self.ownPower)
        s += "\nopp power: " + str(self.opponentPower)
        s += "\naction path: "
        for action in self.actionPath:
            s += "\n" + str(action)
        return s


parser = argparse.ArgumentParser(description='Magic: the Gathering AI utilitary')
parser.add_argument("-a1", "--agent1",
                    help="specify agent for player 1")
parser.add_argument("-a2", "--agent2",
                    help="specify agent for player 2")
parser.add_argument("-d1", "--deck1", default='deck1.txt',
                    help="specify deck for player 1")
parser.add_argument("-d2", "--deck2", default='deck2.txt',
                    help="specify deck for player 2")
parser.add_argument("-v", "--verbose",  action="store_true")
parser.add_argument("-n", "--name", action="store_true",
                    help="choose names for the players")

args = parser.parse_args()

jogo = Game(args.agent1, "deck1.txt", args.agent2, "deck2.txt", args.verbose, args.name)
