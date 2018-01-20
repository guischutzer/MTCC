import argparse
import random
from player import *
from card import *
from permanent import *
import utils
from copy import copy
import re

class Game:

    def __init__(self, agent1, deck1, agent2, deck2, verbosity):

        actPlayerID = random.randrange(1, 3)

        if agent1 is None:
            self.player_1 = Player(1)
        elif agent1 == "random" or agent1 == "Random":
            self.player_1 = RandomAgent(1, actPlayerID is 1, verbosity)
        else:
            self.player_1 = MulliganAgent(1, actPlayerID is 1, verbosity)

        if agent2 is None:
            self.player_2 = Player(2)
        elif agent2 == "random" or agent2 == "Random":
            self.player_2 = RandomAgent(2, actPlayerID is 2, verbosity)
        else:
            self.player_2 = MulliganAgent(2, actPlayerID is 2, verbosity)

        # name = input("Choose a name for Player 1: ")
        self.player_1.rename("Red")
        # name = input("Choose a name for Player 2: ")
        self.player_2.rename("White")

        self.readDeck(deck1, self.player_1)
        self.readDeck(deck2, self.player_2)

        actPlayerID = random.randrange(1, 3)
        self.activePlayer = self.setActivePlayer(actPlayerID)
        self.opponent = self.opponentOf(self.activePlayer)

        self.battlefield = []

        self.player_1.shuffle()
        self.player_2.shuffle()
        self.player_1.draw(7)
        self.player_2.draw(7)

        print("\nPlayer " + self.activePlayer.name + " starts the game.")

        p1keep = False
        p2keep = False
        while  not p1keep or not p2keep:
            if not p1keep:
                p1keep = self.activePlayer.mulligan()
            if not p2keep:
                p2keep = self.opponent.mulligan()

        n = 0
        endGame = False # flag for ending the game (name may change)
        while not endGame:
            n += 1
            endGame = self.turnRoutine(n)
            self.changeActivePlayer()

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

        opponent = self.opponentOf(player)
        ownCreatures = copy(player.creatures)
        if card.ctype == 'Creature':
            ownCreatures.append(Creature(card, player))

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

        card.setLegalTargets(legalTargets)
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
            if player.lose or player.life <= 0:
                print("Player " + player.name + " has lost the game.")
                return True

            for creature in player.creatures:
                if creature.dealtLethal:
                    player.creatures.remove(creature)
                    creature.putOnGraveyard()

        return False

    def play(self, action):

        card = action[0]
        targets = []
        if len(action) > 1:
            targets = action[1]

        player = self.activePlayer

        paidMana = 0
        player.hand.remove(card)

        if card.ctype == "Land":
            player.landDrop = True
            permanent = Land(card, player)
            player.lands.append(permanent)
            return permanent

        for land in player.lands:
            if not land.isTapped() and paidMana < card.cmc():
                land.tap()
                paidMana += 1

        if card.ctype == "Creature":
            permanent = Creature(card, player)
            player.creatures.append(permanent)
            for target in targets:
                for i in range(len(targets)):
                    if targets[i] not in player.creatures:
                        targets[i] = permanent
                        break
            card.effect(targets)
            return permanent

        if card.ctype == "Sorcery":
            card.effect(targets)
            player.graveyard.append(card)
            return None

    def printGameState(self):
        print("")
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

        print("\n")

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

        # Upkeep (not present in version alpha)
        if self.checkSBA():
            return True

        # Draw
        if tNumber > 1:
            activePlayer.draw()
        if self.checkSBA():
            return True

        ## Precombat Main Phase TODO: Show legal actions
        print("----------------------------------------------------------")
        print("Precombat Main Phase")
        print("----------------------------------------------------------")

        self.mainPhase()

        ## Combat Phase

        print("----------------------------------------------------------")
        print("Combat Phase")
        print("----------------------------------------------------------")


        # Declare Attackers - Active Player
        legalActions = self.getAttackingActions()
        attackers = activePlayer.declareAttackers(legalActions)

        combatPairings = {}
        for creature in attackers:
            creature.attack()
            combatPairings[creature] = []

        # print(activePlayer.name + ", declare attackers:")
        # combatPairings = {}
        # for creature in activePlayer.creatures:
        #     if creature.canAttack():
        #         c = input("Declare " + creature.card.name + " as an attacker? (y/N) ")
        #         if utils.confirm(c):
        #             creature.attack()
        #             combatPairings[creature] = []


        # Declare Blockers - Not Active Player
        # Declare Attackers - Active Player
        legalActions = self.getBlockingActions(attackers)
        combatPairings = opponent.declareBlockers(legalActions, combatPairings)

        # print(opponent.name + ", declare blockers: ")
        # for attacker in combatPairings:
        #     for creature in opponent.creatures:
        #         if creature.canBlock(attacker):
        #             c = input("Block " + attacker.card.name + " with " + creature.card.name + "? (y/N) ")
        #             if utils.confirm(c):
        #                 creature.block(attacker)
        #                 combatPairings[attacker].append(creature)

        ## Choosing Block Order - Active Player
        combatPairings = activePlayer.assignBlockOrder(combatPairings)

        # for attacker in combatPairings:
        #     if len(combatPairings[attacker]) > 1:
        #         print("Blocking " + attacker.stats() + ": ")
        #         i = 1
        #         auxList = []
        #         for blocker in combatPairings[attacker]:
        #             print(str(i) + ") " + blocker.stats())
        #             auxList.append(blocker)
        #             i + 1
        #         order = input("Desired order (numbers with commas): ")
        #         order.split(" ")
        #         i = 0
        #         for number in order:
        #             auxList[n] = combatPairings[attacker][int(number) - 1]
        #             i += 1
        #         combatPairings[attacker] = auxList

        # Combat Damage
        # - First & Double Strike Damage
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

        for attacker in combatPairings:

            print(combatPairings[attacker])

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

        self.printGameState()

        ## End Phase
        print("----------------------------------------------------------")
        print("End Phase")
        print("----------------------------------------------------------")
        # End

        # Cleanup
        for permanent in activePlayer.creatures:
            permanent.removeDamage()
            permanent.resetPTA()
        if activePlayer.cardsInHand() > 7:
            activePlayer.discardExcess()

        return False

    def getMainActions(self):

        legalActions = [['Pass']]
        player = self.activePlayer

        for card in player.hand:
            if self.canPlay(player, card):
                legalTargets = self.findLegalTargets(player, card)
                targetCombinations = utils.listCombinations(legalTargets)
                action = [card]
                for combination in targetCombinations:
                    action += [combination]
                legalActions += [action]

        return legalActions

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

    def mainPhase(self):

        action = ''

        while action != 'Pass':
            legalActions = self.getMainActions()
            action = self.activePlayer.mainPhaseAction(legalActions)

            if action == 'Print':
                self.printGameState()

            if isinstance(action[0], Card):
                self.play(action)
                if self.checkSBA():
                    return True

        return False

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
# parser.add_argument('--decks', help='select decks')
# parser.add_argument('deck1',
#                     help='Deck file (player 1)')
# parser.add_argument('deck2',
#                     help='Deck file (player 2)')

args = parser.parse_args()

jogo = Game(args.agent1, "deck1.txt", args.agent2, "deck2.txt", args.verbose)
