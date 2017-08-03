import argparse
import random
import copy as c

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

        self.battlefield = []

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

    def chooseTargets(self, player, targets):
        chosenTargets = []

        opponent = self.opponentOf(player)
        ownCreatures = c.copy(player.creatures)

        opponentCreatures = c.copy(opponent.creatures)
        for creature in opponentCreatures:
            if creature.hasHexproof():
                opponentCreatures.remove(creature)

        targetNumber = 1
        for targetType in targets:
            print("Possible targets for the target number" + targetNumber + ":")
            optionNumber = 1
            curList = []
            if "OwnCreature" in targetType:
                for creature in ownCreatures:
                    curList.append[creature]
                    print(optionNumber + ") " + creature.stats)
                    optionNumber += 1
            if "OpponentCreature" in targetType:
                for creature in opponentCreatures:
                    curList.append[creature]
                    print(optionNumber + ") " + creature.stats)
                    optionNumber += 1
            if "Player" in targetType:
                curList.append[player]
                print(optionNumber + ") You")
                optionNumber += 1
                curList.append[opponent]
                print(optionNumber + ") Opponent")
                optionNumber += 1
            if "Opponent" in targetType:
                curList.append[opponent]
                print(optionNumber + ") Opponent")
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
                return False
            else:
                return True

        if card.cost <= player.untappedLands:
            if.card.ctype == "Sorcery":
                return self.canTarget(player, card.targets)
            else:
                return True

    def play(self, player, card):
        paidMana = 0
        player.hand.remove(card)
        if card.ctype == "Land":
            player.lands.append(Permanent(card, player))
            player.untappedLands += 1
        while paidMana < card.cost:
            for land in player.lands:
                if not land.isTapped():
                    land.tap()
                    player.untappedLands -= 1
                    paidMana += 1
        if card.ctype == "Sorcery":
            card.effect(self.chooseTargets(player, targets))
            player.graveyard.append(card)
        elif card.ctype == "Creature":
            player.creatures.append(Creature(card, player))
            if self.canTarget(player, card.targets):
                card.etb(self.chooseTargets(player, targets))

    def turnRoutine(self, tNumber):

        activePlayer = self.pqueue[0]
        opponent = self.pqueue[1]
        landDrop = False

        ## Beggining Phase
        # Untap - untap permanents of active player
        for permanent in activePlayer.battlefield:
            permanent.untap()
            permanent.removeSickness()

        # Upkeep (not present in version alpha)
        self.checkSBA()

        # Draw
        if tNumber > 1:
            activePlayer.draw()
        self.checkSBA()

        ## Precombat Main Phase TODO: Show legal actions
        activePlayer.showHand()
        c = ''
        while c != '0':
            c = input("Choose a card from your hand to play (0 will pass priority):")
            ## TODO: play the card
            if c != '0' and int(c) <= len(activePlayer.hand):
                card = player.hand[int(c)-1]
                if self.canPlay(activePlayer, card):
                    player.play(card)
                else:
                    if card.ctype != "Land":
                        print("Not enough untapped lands.")
                    else:
                        print("Already played a land this turn.")
                    c = ''
            self.checkSBA()

        while c != 0:
            activePlayer.showHand()
            c = input("Choose a card from your hand to play (0 will pass priority):")
            ## TODO: play the card
            self.checkSBA()

        ## Combat Phase

        # Declare Attackers - Active Player
        combatPairings = {}
        for permanent in activePlayer.battlefield:
            if permanent.canAttack():
                c = input("Declare " + permanent.card.name + " as an attacker? (y/N) ")
                if confirm(c):
                    permanent.attack()
                    combatPairings.[permanent] = []


        # Declare Blockers - Not Active Player
        for attacker in combatPairings:
            c = input("Block " + attacker.card.name + "? (y/N) ")
            if confirm(c):
                for permanent in opponent.battlefied:
                    if permanent.canBlock(attacker):
                        c = input("With " + b.card.name + "? (y/N) ")
                        if confirm(c):
                            permanent.block(attacker)
                            combatPairings[attacker].append(permanent)

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
                    blocker.dealDamage(attacker, curPower)

        self.checkSBA()

        # - Combat Damage

        for attacker in combatPairings:

            if not attacker.hasFirstStrike() or attacker.hasDoubleStrike():
                remainingDamage = attacker.power

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
                    blocker.dealDamage(attacker, curPower)

        self.checkSBA()

        # End of Combat
        for attacker in combatPairings:
            attacker.attacking = False
            for blocker in combatPairings[attacker]:
                blocker.blocking = False

        ## Postcombat Main Phase
        activePlayer.showHand()
        c = input("Choose a card from your hand to play (0 will pass priority):")
        ## TODO: play the card
        self.checkSBA()

        while c != 0:
            activePlayer.showHand()
            c = input("Choose a card from your hand to play (0 will pass priority):")
            ## TODO: play the card
            self.checkSBA()

        ## End Phase
        # End

        # Cleanup
        for permanent in activePlayer.battlefied:
            permanent.removeDamage()
            permanent.resetPTA()
            while activePlayer.cardsInHand > 7:
                activePlayer.showHand()
                c = input("Choose a card from your hand to discard:")
                ## TODO: discard the chosen card

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

    def opponentOf(self, player):
        if self.player_1 == player:
            return self.player_2

        return self.player_1

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
