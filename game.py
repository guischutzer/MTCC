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
    # - choosefname is used to input different names for the players
    def __init__(self, agent1, deck1, agent2, deck2, verbosity, choosename):

        actPlayerID = random.randrange(-1, 1)
        self.permanentID = 0

        # Players initialization
        if agent1 is None:
            self.player_1 = Player(0)
        elif agent1 == "random" or agent1 == "Random":
            self.player_1 = RandomAgent(0, actPlayerID == 0, verbosity)
        elif agent1 == "search" or agent1 == "Search":
            self.player_1 = SearchAgent(0, actPlayerID == 0, verbosity)
        else:
            self.player_1 = MulliganAgent(0, actPlayerID == 0, verbosity)

        if agent2 is None:
            self.player_2 = Player(-1)
        elif agent2 == "random" or agent2 == "Random":
            self.player_2 = RandomAgent(-1, actPlayerID == -1, verbosity)
        elif agent2 == "search" or agent2 == "Search":
            self.player_2 = SearchAgent(-1, actPlayerID == -1, verbosity)
        else:
            self.player_2 = MulliganAgent(-1, actPlayerID == -1, verbosity)

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

        if self.player_1.hasLost():
            print("Player " + self.player_1.name + " has lost the game.")
        if self.player_2.hasLost():
            print("Player " + self.player_2.name + " has lost the game.")
    # turnRoutine(tNumber):
    # calls the necessary methods in the correct order and deals
    # with events like a normal Magic turn
    def turnRoutine(self, tNumber):

        activePlayer = self.activePlayer
        opponent = self.opponent

        activePlayer.landDrop = False
        self.attackers = None

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

        self.printGameState()

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
        if self.mainPhase(1):
            return True

        ## Combat Phase

        print("----------------------------------------------------------")
        print("Combat Phase")
        print("----------------------------------------------------------")

        # Declare Attackers - Active Player

        # Active player chooses how creatures attack
        if self.attackers == None:
            legalActions = self.getAttackingActions()
            attIDs = activePlayer.declareAttackers(legalActions)
            self.attackers = []
            for ID in attIDs:
                self.attackers.append(self.getPermanentFromID(ID))
        else:
            liveAttackers = []
            for attacker in self.attackers:
                if not attacker.destroyed:
                    liveAttackers.append(attacker)
            self.attackers = liveAttackers
        combatPairings = self.attack(self.attackers)
        activePlayer.printAttackers(self.attackers)

        # Declare Blockers - Not Active Player

        # Similarly, legal actions for blocking are all the
        # arrangements possible for each of its creatures to block
        # the opponent's attacking creatures. Each type of player/agent
        # then chooses the action differently
        legalActions = self.getBlockingActions(self.attackers)
        state = State(self, 'Combat', [])
        combatPairings = opponent.declareBlockers(legalActions, combatPairings, state)

        ## Choosing Block Order - Active Player
        combatPairings = activePlayer.assignBlockOrder(combatPairings, self)

        if self.resolveCombat(combatPairings):
            return True

        ## Postcombat Main Phase
        print("----------------------------------------------------------")
        print("Postcombat Main Phase")
        print("----------------------------------------------------------")

        if self.mainPhase(2):
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

    ############### MAIN PHASE HANDLING ###############
    #
    # Main phase method. Lets players play cards.
    # checkSBA() called (returns True if game has ended)
    def mainPhase(self, number):

        player = self.activePlayer

        if isinstance(player, SearchAgent):
            phase = ''
            if number == 1:
                phase = 'First Main'
            else:
                phase = 'Second Main'
            state = State(self, phase, [])
            actionPath = player.breadthFirstSearch(state)
            print(actionPath)
            action = actionPath[0]
            i = 0
            while action[0] != 'Pass':
                card = player.hand[action[0]]
                self.play(action)
                targets = []
                for ID in action[1]:
                    targets.append(self.getPermanentFromID(ID))
                player.printMainAction(card, targets)
                if self.checkSBA():
                    return True
                i += 1
                action = actionPath[i]
            if phase == 'First Main':
                self.attackers = []
                for attID in actionPath[i+1]:
                    self.attackers.append(self.getPermanentFromID(attID))

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
    #
    # returns active players legal actions in any main phase. Actions can be
    # - ['Pass'] to pass the turn
    # - ['Print'] to print the board state
    # - [card, targets] to play a card targeting a list of legalTargets (found by ID)
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

        return legalActions
    #
    # Plays the selected card with selected targets.
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
                        if "OwnCreature" in card.targets:
                            targets[i] = permanent
                            break
            card.effect(self, targets)
            return permanent

        if card.ctype == "Sorcery":
            targets = []
            for ID in targetIDs:
                targets.append(self.getPermanentFromID(ID))
            card.effect(self, targets)
            player.graveyard.append(card)
            return None
    #
    # Returns True if player can play card, False if not.
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
    #
    # Returns True if an effect can be applied to any target, False if not.
    def canTarget(self, player, targets):

        opponent = self.opponentOf(player)
        ownCreatures = c.copy(player.creatures)

        opponentCreatures = c.copy(opponent.creatures)
        for creature in opponentCreatures:
            if creature.hasHexproof():
                opponentCreatures.remove(creature)

        for target in targets:
            for targetType in target:
                foundTarget = False
                if foundTarget:
                    break
                if targetType == "Player" or targetType == "Opponent":
                    foundTarget = True
                elif targetType == "Creature":
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
    #
    # Returns list of every possible target to the card's effect
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
            for targetType in possibleTarget:
                if targetType == "OwnCreature":
                    for creature in ownCreatures:
                        curList.append(creature)

                if targetType == "OpponentCreature":
                    for creature in opponentCreatures:
                        curList.append(creature)

                if targetType == "Player":
                    curList.append(player)
                    curList.append(opponent)

                if targetType == "Opponent":
                    curList.append(opponent)

            legalTargets.append(curList)

        return legalTargets

    ############### STATE-BASED ACTIONS CHECKING - VERY IMPORTANT ###############
    #
    # This method is called several times throughout program execution to handle
    # mainly permanents being destroyed and players losing (end of game).
    def checkSBA(self):
        for player in self.activePlayer, self.opponent:
            for creature in player.creatures:
                if creature.damage >= creature.curTou:
                    creature.dealtLethal = True
                if creature.dealtLethal or creature.destroyed:
                    player.creatures.remove(creature)
                    creature.putOnGraveyard()

            for land in player.lands:
                if land.destroyed:
                    player.lands.remove(land)
                    land.putOnGraveyard()
            if player.life <= 0:
                player.lose = True
            if player.lose:
                return True

        return False

    ############### COMBAT HANDLING ###############
    #
    # Returns every combination of legal attackers possible.
    def getAttackingActions(self):
        player = self.activePlayer
        possibleAttackers = [creature.ID for creature in player.creatures if creature.canAttack()]
        return utils.listArrangements(possibleAttackers)
    #
    # Calls attack() for each attacking creature.
    def attack(self, attackers):
        # combatPairings pair attackers with their assigned blockers
        combatPairings = {}
        for creature in attackers:
            creature.attack()
            combatPairings[creature] = []
        return combatPairings
    #
    # Return every combination of legal pairings of current attackers
    # and blocking creatures possible.
    def getBlockingActions(self, attackers):

        player = self.opponent

        possibleBlocksList = []
        for creature in player.creatures:
            possibleBlocks = [None]
            for attacker in attackers:
                if creature.canBlock(attacker):
                    possibleBlocks.append(attacker)
            possibleBlocksList.append(possibleBlocks)
        if possibleBlocksList == []:
            possibleBlocksList = [[]]

        return utils.listCombinations(possibleBlocksList)
    #
    # Each attacker deals damage to its' blockers and vice-versa;
    # Each unblocked attacker deals damage to defending player;
    # checkSBA() called (returns True if game has ended)
    def resolveCombat(self, combatPairings):
        activePlayer = self.activePlayer
        opponent = self.opponent
        # - First & Double Strike Damage
        # All the first-strikers and double-strikers deal first strike damage
        for attacker in combatPairings:
            if attacker.hasFirstStrike() or attacker.hasDoubleStrike():
                remainingDamage = attacker.curPower

                for i in range(len(combatPairings[attacker])):
                    blocker = combatPairings[attacker][i]
                    neededDamage = blocker.curTou - blocker.damage
                    if attacker.hasDeathtouch():
                        neededDamage = 1
                    if remainingDamage > 0:
                        if remainingDamage >= neededDamage:
                            if len(combatPairings[attacker][i:]) > 1:
                                attacker.dealDamage(blocker, neededDamage)
                                remainingDamage -= neededDamage
                            else:
                                attacker.dealDamage(blocker, remainingDamage)
                                remainingDamage = 0
                        else:
                            attacker.dealDamage(blocker, remainingDamage)
                            remainingDamage = 0

                if combatPairings[attacker] == []:
                    attacker.dealDamage(opponent, remainingDamage)

                elif attacker.hasTrample():
                    if remainingDamage > 0:
                        attacker.dealDamage(opponent, remainingDamage)

            for blocker in combatPairings[attacker]:
                if blocker.hasFirstStrike() or blocker.hasDoubleStrike():
                    blocker.dealDamage(attacker, blocker.curPower)

        if self.checkSBA():
            return True

        # - Combat Damage
        # All the double-strikers and not-first-strikers deal combat damage
        for attacker in combatPairings:
            if not attacker.destroyed:
                if not attacker.hasFirstStrike() or attacker.hasDoubleStrike():
                    remainingDamage = attacker.curPower

                    for i in range(len(combatPairings[attacker])):
                        blocker = combatPairings[attacker][i]
                        neededDamage = blocker.curTou - blocker.damage
                        if attacker.hasDeathtouch():
                            neededDamage = 1
                        if remainingDamage > 0:
                            if remainingDamage >= neededDamage:
                                if len(combatPairings[attacker][i:]) > 1:
                                    attacker.dealDamage(blocker, neededDamage)
                                    remainingDamage -= neededDamage
                                else:
                                    attacker.dealDamage(blocker, remainingDamage)
                                    remainingDamage = 0
                            else:
                                attacker.dealDamage(blocker, remainingDamage)
                                remainingDamage = 0

                    if combatPairings[attacker] == []:
                        attacker.dealDamage(opponent, remainingDamage)

                    elif attacker.hasTrample():
                        if remainingDamage > 0:
                            attacker.dealDamage(opponent, remainingDamage)
            for blocker in combatPairings[attacker]:
                if not blocker.destroyed:
                    if not blocker.hasFirstStrike() or blocker.hasDoubleStrike():
                        blocker.dealDamage(attacker, blocker.curPower)

        if self.checkSBA():
            return True

        # End of Combat
        for attacker in combatPairings:
            attacker.attacking = False
            for blocker in combatPairings[attacker]:
                blocker.blocking = False

        return False

    ############### CARD AND PERMANENT HANDLING ###############
    #
    # Read deck from text file.
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
    #
    # Create card based on read name.
    def createCard(self, cardname, owner):
        card = None
        classname = re.sub("[ \n]", "", cardname)
        variables = locals()
        command = "card = " + classname + "(owner)"
        exec(command, globals(), variables)
        return variables['card']
    #
    # Create permanent (usually) when played.
    def createPermanent(self, card, owner):
        lst = []
        permanent = None
        if card.ctype == 'Creature':
            permanent = Creature(card, owner, self.newPermanentID())
            lst = owner.creatures
        else:
            permanent = Land(card, owner, self.newPermanentID)
            lst = owner.lands
        lst.append(permanent)
    #
    # Each created permanent has a new ID.
    def newPermanentID(self):
        self.permanentID += 1
        return self.permanentID
    #
    # Returns permanent from ID (like a query).
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
    #
    # Returns Creature combat pairings with combat pairings
    # comprising of ID integers
    def getCombatPairingsFromIDs(self, combatPairingsIDs):
        combatPairings = {}
        for attID in combatPairingsIDs:
            attacker = self.getPermanentFromID(attID)
            combatPairings[attacker] = []
            for blkID in combatPairingsIDs[attID]:
                blocker = self.getPermanentFromID(blkID)
                combatPairings[attacker].append(blocker)
        return combatPairings

    ############### ACTIVE PLAYER METHODS ###############
    #
    # Some administrative methods to class Game
    #
    def opponentOf(self, player):
        if self.player_1 == player:
            return self.player_2

        return self.player_1
    #
    def changeActivePlayer(self):
        self.player_1.setActive(not self.player_1.isActive())
        self.player_2.setActive(not self.player_2.isActive())
        aux = self.activePlayer
        self.activePlayer = self.opponent
        self.opponent = aux
    #
    def setActivePlayer(self, ID):
        self.player_1.setActive(ID == 1)
        self.player_2.setActive(ID == 2)
        if self.player_1.isActive():
            return self.player_1
        return self.player_2

    ############### GAME INFO ###############
    #
    # Prints board state and life totals.
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
