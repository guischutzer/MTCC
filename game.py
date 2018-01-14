import argparse
import random
from player import Player
from card import *
from permanent import *
import utils
from copy import copy
import re

parser = argparse.ArgumentParser(description='Magic: the Gathering AI utilitary')
parser.add_argument("-a1", "--agent1",
                    help="specify agent for player 1")
parser.add_argument("-a2", "--agent2",
                    help="specify agent for player 2")
parser.add_argument("-d1", "--deck1", default='deck1.txt',
                    help="specify deck for player 1")
parser.add_argument("-d2", "--deck2", default='deck2.txt',
                    help="specify deck for player 2")
# parser.add_argument('--decks', help='select decks')
# parser.add_argument('deck1',
#                     help='Deck file (player 1)')
# parser.add_argument('deck2',
#                     help='Deck file (player 2)')

args = parser.parse_args()

jogo = Game(args.agent1, "deck1.txt", args.agent1, "deck2.txt")


class Game:

    def __init__(self, agent1, deck1, agent2, deck2):

        if agent1 is None:
            self.player_1 = Player(1)
        else:
            self.player_1 = Agent(1)

        if agent2 is None:
            self.player_2 = Player(2)
        else:
            self.player_2 = Agent(2)

        name = input("Choose a name for Player 1: ")
        self.player_1.rename(name)
        name = input("Choose a name for Player 2: ")
        self.player_2.rename(name)

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

    def getLegalTargets(self, player, targets):
        legalTargets = []

        opponent = self.opponentOf(player)
        ownCreatures = copy(player.creatures)

        opponentCreatures = copy(opponent.creatures)
        for creature in opponentCreatures:
            if creature.hasHexproof():
                opponentCreatures.remove(creature)

        for possibleTarget in targets:
            curList = []
            for targetType in possibleTarget:
                if "OwnCreature" in targetType:
                    for creature in ownCreatures:
                        curList.append(creature)

                if "OpponentCreature" in targetType:
                    for creature in opponentCreatures:
                        curList.append(creature)

                if "Player" in targetType:
                    curList.append(player)
                    curList.append(opponent)

                if "Opponent" in targetType:
                    curList.append(opponent)

            legalTargets.append(curList)

        return legalTargets

    def chooseTargets(self, player, targets):
        chosenTargets = []

        opponent = self.opponentOf(player)
        ownCreatures = copy(player.creatures)

        opponentCreatures = copy(opponent.creatures)
        for creature in opponentCreatures:
            if creature.hasHexproof():
                opponentCreatures.remove(creature)

        targetNumber = 1
        for targetType in targets:
            print("Possible targets for the target number " + str(targetNumber) + ":")
            optionNumber = 1
            curList = []
            if "OwnCreature" in targetType:
                for creature in ownCreatures:
                    curList.append(creature)
                    print(str(optionNumber) + ") " + creature.stats())
                    optionNumber += 1
            if "OpponentCreature" in targetType:
                for creature in opponentCreatures:
                    curList.append(creature)
                    print(str(optionNumber) + ") " + creature.stats())
                    optionNumber += 1
            if "Player" in targetType:
                curList.append(player)
                print(str(optionNumber) + ") You")
                optionNumber += 1
                curList.append(opponent)
                print(str(optionNumber) + ") Opponent")
                optionNumber += 1
            if "Opponent" in targetType:
                curList.append(opponent)
                print(str(optionNumber) + ") Opponent")
                optionNumber += 1
            c = 0
            while c < 1 or c > len(curList):
                c = int(input("Choose a target: "))
            chosenTarget = curList[c - 1]
            chosenTargets.append(chosenTarget)
            if not chosenTarget.isPlayer():
                if chosenTarget.getController() == player:
                    ownCreatures.remove(chosenTarget)
                else:
                    opponentCreatures.remove(chosenTarget)

        return chosenTargets


    def canPlay(self, player, card):

        if card.ctype == "Land":
            if self.landDrop == True:
                print("Already played a land this turn.")
                return False
            else:
                return True

        if card.cmc() <= player.untappedLands:
            if card.ctype == "Sorcery":
                if not self.canTarget(player, card.targets):
                    print("No valid targets.")
                    return False
                return True
            else:
                return True

        print("Not enough untapped lands.")
        return False

    def checkSBA(self):
        for player in self.activePlayer, self.opponent:
            if player.lose:
                print("Player " + player.number + " has lost the game.")
                return True

            for creature in player.creatures:
                if creature.dealtLethal:
                    player.creatures.remove(creature)
                    creature.putOnGraveyard()

        return False

    def play(self, player, card):
        paidMana = 0
        player.hand.remove(card)
        if card.ctype == "Land":
            self.landDrop = True
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
            if self.canTarget(player, card.targets):
                legalTargets = self.getLegalTargets(player, card.targets)
                card.effect(player.chooseTargets(legalTargets))
            return permanent

        if card.ctype == "Sorcery":
            card.effect(self.chooseTargets(player, card.targets))
            player.graveyard.append(card)
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

        print("\n")

    def turnRoutine(self, tNumber):

        self.landDrop = False
        activePlayer = self.activePlayer
        opponent = self.opponent

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
        print(activePlayer.name + ", declare attackers:")
        combatPairings = {}
        for creature in activePlayer.creatures:
            if creature.canAttack():
                c = input("Declare " + creature.card.name + " as an attacker? (y/N) ")
                if utils.confirm(c):
                    creature.attack()
                    combatPairings[creature] = []


        # Declare Blockers - Not Active Player
        print(opponent.name + ", declare blockers: ")
        for attacker in combatPairings:
            for creature in opponent.creatures:
                if creature.canBlock(attacker):
                    c = input("Block " + attacker.card.name + " with " + creature.card.name + "? (y/N) ")
                    if utils.confirm(c):
                        creature.block(attacker)
                        combatPairings[attacker].append(creature)

        ## Choosing Block Order - Not Active Player
        for attacker in combatPairings:
            if len(combatPairings[attacker]) > 1:
                print("Blocking " + attacker.stats() + ": ")
                i = 1
                auxList = []
                for blocker in combatPairings[attacker]:
                    print(str(i) + ") " + blocker.stats())
                    auxList.append("")
                    i + 1
                order = input("Desired order (numbers with commas): ")
                order.split(" ")
                i = 0
                for number in order:
                    auxList[n] = combatPairings[attacker][int(number) - 1]
                    i += 1
                combatPairings[attacker] = auxList

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

        self.mainPhase()

        ## End Phase
        print("----------------------------------------------------------")
        print("End Phase")
        print("----------------------------------------------------------")
        # End

        # Cleanup
        for permanent in activePlayer.creatures:
            permanent.removeDamage()
            permanent.resetPTA()
        while activePlayer.cardsInHand() > 7:
            activePlayer.showHand()
            c = 0
            while c < 1 or c > activePlayer.cardsInHand():
                c = int(input("Choose a card from your hand to discard: "))
            card = activePlayer.hand[c - 1]
            activePlayer.discard(card)

        return False

    def mainPhase(self):
        c = ''
        while c != 0:
            self.activePlayer.showHand()
            c = input("Choose a card from your hand (0 will pass priority, 'p' prints the game state): ")
            if c == 'p':
                c = -1
                self.printGameState()
            c = int(c)
            if c > 0 and c <= len(self.activePlayer.hand):
                card = self.activePlayer.hand[c - 1]
                print("\n" + str(card))
                if self.canPlay(self.activePlayer, card):
                    self.play(self.activePlayer, card)
                else:
                    c = ''

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
