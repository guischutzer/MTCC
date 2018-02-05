import re
import utils

class Card:

    def __init__(self, name, owner):
        self.name = name
        self.cost = ""
        self.supertype = ""
        self.ctype = ""
        self.subtype = ""
        self.text = ""
        self.targets = []
        self.owner = owner

    def cmc(self):
        m = re.match("(\d?)(\w*)", self.cost).groups()
        c = 0
        if m[0] != "":
            c += int(m[0])
        c += len(m[1])
        return c

    def color(self, cost):
        c = []
        for color in colors:
            if re.search(color, cost) is not None:
                c.append(color)

        return c

    def abilities(self):
        return

    def effect(self, game, targets):
        return

    def __str__(self):
        s = self.name + "\n"
        s += self.cost + "\n"
        s += self.supertype + "\n"
        s += self.ctype + "\n"
        s += self.subtype + "\n"
        s += self.text + "\n"
        return s

    def setLegalTargets(self, legalTargets):
        self.legalTargets = legalTargets

class Mountain(Card):
    def __init__(self, owner):
        self.name = "Mountain"
        self.cost = ""
        self.supertype = "Basic"
        self.ctype = "Land"
        self.subtype = "Mountain"
        self.text = "{T}: Add {R} to your mana pool."
        self.targets = []
        self.owner = owner

class Swamp(Card):
    def __init__(self, owner):
        self.name = "Swamp"
        self.cost = ""
        self.supertype = "Basic"
        self.ctype = "Land"
        self.subtype = "Swamp"
        self.text = "{T}: Add {B} to your mana pool."
        self.targets = []
        self.owner = owner

class Plains(Card):
    def __init__(self, owner):
        self.name = "Plains"
        self.cost = ""
        self.supertype = "Basic"
        self.ctype = "Land"
        self.subtype = "Plains"
        self.text = "{T}: Add {W} to your mana pool."
        self.targets = []
        self.owner = owner

class VolcanicHammer(Card):
    def __init__(self, owner):
        self.name = "Volcanic Hammer"
        self.cost = "1R"
        self.supertype = ""
        self.ctype = "Sorcery"
        self.subtype = ""
        self.text = "Volcanic Hammer deals 3 damage to target creature or player."
        self.targets = [["OwnCreature", "OpponentCreature", "Player"]]
        self.owner = owner

    def effect(self, game, targets):
        targets[0].takeDamage(3)

class LavaAxe(Card):
    def __init__(self, owner):
        self.name = "Lava Axe"
        self.cost = "4R"
        self.supertype = ""
        self.ctype = "Sorcery"
        self.subtype = ""
        self.text = "Lava Axe deals 5 damage to target player."
        self.targets = [["Player"]]
        self.owner = owner

    def effect(self, game, targets):
        targets[0].takeDamage(5)

class BlazingVolley(Card):
    def __init__(self, owner):
        self.name = "Blazing Volley"
        self.cost = "R"
        self.supertype = ""
        self.ctype = "Sorcery"
        self.subtype = ""
        self.text = "Blazing Volley deals 1 damage to each creature your opponents control."
        self.targets = []
        self.owner = owner

    def effect(self, game, targets):
        for creature in game.opponent.creatures:
            creature.takeDamage(1)


class InspiringRoar(Card):
    def __init__(self, owner):
        self.name = "Inspiring Roar"
        self.cost = "3W"
        self.supertype = ""
        self.ctype = "Sorcery"
        self.subtype = ""
        self.text = "Put a +1/+1 counter on each creature you control."
        self.targets = []
        self.owner = owner

    def effect(self, game, targets):
        for creature in self.owner.creatures:
            creature.power += 1
            creature.tou += 1
            creature.curTou += 1
            creature.curPower += 1

class BatheinDragonfire(Card):
    def __init__(self, owner):
        self.name = "Bathe in Dragonfire"
        self.cost = "2R"
        self.supertype = ""
        self.ctype = "Sorcery"
        self.subtype = ""
        self.text = "Bathe in Dragonfire deals 4 damage to target creature."
        self.targets = [["OwnCreature", "OpponentCreature"]]
        self.owner = owner

    def effect(self, game, targets):
        targets[0].takeDamage(4)

class DayofJudgment(Card):
    def __init__(self, owner):
        self.name = "Day of Judgment"
        self.cost = "2WW"
        self.supertype = ""
        self.ctype = "Sorcery"
        self.subtype = ""
        self.text = "Destroy all creatures."
        self.targets = []
        self.owner = owner

    def effect(self, game, targets):

        for creature in self.owner.creatures:
            creature.destroy()

        for creature in game.opponent.creatures:
            creature.destroy()

class GriffinSentinel(Card):
    def __init__(self, owner):
        self.name = "Griffin Sentinel"
        self.cost = "2W"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Griffin"
        self.text = "Flying, vigilance. 1/3"
        self.abilities = ["Flying", "Vigilance"]
        self.targets = []
        self.owner = owner
        self.power = 1
        self.tou = 3

class SiegeMastodon(Card):
    def __init__(self, owner):
        self.name = "Siege Mastodon"
        self.cost = "4W"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Elephant"
        self.text = "3/5"
        self.abilities = []
        self.targets = []
        self.owner = owner
        self.power = 3
        self.tou = 5

class BrazenScourge(Card):
    def __init__(self, owner):
        self.name = "Brazen Scourge"
        self.cost = "1RR"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Gremlin"
        self.text = "3/3"
        self.abilities = ["Haste"]
        self.targets = []
        self.owner = owner
        self.power = 3
        self.tou = 3

class SkyrakerGiant(Card):
    def __init__(self, owner):
        self.name = "Skyraker Giant"
        self.cost = "2RR"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Giant"
        self.text = "4/3"
        self.abilities = ["Reach"]
        self.targets = []
        self.owner = owner
        self.power = 4
        self.tou = 3

class FencingAce(Card):
    def __init__(self, owner):
        self.name = "Fencing Ace"
        self.cost = "1W"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Human Soldier"
        self.text = "Double strike. 1/1"
        self.abilities = ["Double strike"]
        self.targets = []
        self.owner = owner
        self.power = 1
        self.tou = 1

class ChampionofArashin(Card):
    def __init__(self, owner):
        self.name = "Champion of Arashin"
        self.cost = "3W"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Hound Warrior"
        self.text = "3/2"
        self.abilities = ["Lifelink"]
        self.targets = []
        self.owner = owner
        self.power = 3
        self.tou = 2

class FrenziedRaptor(Card):
    def __init__(self, owner):
        self.name = "Frenzied Raptor"
        self.cost = "2R"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Dinosaur"
        self.text = "4/2"
        self.abilities = []
        self.targets = []
        self.owner = owner
        self.power = 4
        self.tou = 2

class HeavyInfantry(Card):
    def __init__(self, owner):
        self.name = "Heavy Infantry"
        self.cost = "4W"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Human Soldier"
        self.text = "When Heavy Infantry enters the battlefield, tap target creature an opponent controls. 3/4"
        self.abilities = []
        self.targets = [["OpponentCreature"]]
        self.owner = owner
        self.power = 3
        self.tou = 4

    def effect(self, game, targets):
        if len(targets) > 0:
            targets[0].tap()

class FoulImp(Card):
    def __init__(self, owner):
        self.name = "Foul Imp"
        self.cost = "B"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Imp"
        self.text = "Flying. When Foul Imp enters the battlefield you lose 1 life. 1/1"
        self.abilities = ["Flying"]
        self.targets = []
        self.owner = owner
        self.power = 1
        self.tou = 1

    def effect(self, game, targets):
        self.owner.loseLife(1)

class AngelofMercy(Card):
    def __init__(self,owner):
        self.name = "Angel of Mercy"
        self.cost = "4W"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Angel"
        self.text = "Flying. When Angel of Mercy enters the battlefield, you gain 3 life. 3/3"
        self.abilities = ["Flying"]
        self.targets = []
        self.owner = owner
        self.power = 3
        self.tou = 3

    def effect(self, game, targets):
        self.owner.gainLife(3)

class GuardianofPilgrims(Card):
    def __init__(self,owner):
        self.name = "Guardian of Pilgrims"
        self.cost = "1W"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Spirit Cleric"
        self.text = "When Guardian of Pilgrims enters the battlefield, target creature gets +1/+1 until end of turn. 2/2"
        self.abilities = []
        self.targets = [["OwnCreature", "OpponentCreature"]]
        self.owner = owner
        self.power = 2
        self.tou = 2

    def effect(self, game, targets):
        targets[0].curPower = targets[0].curPower + 1
        targets[0].curTou = targets[0].curTou + 1

class NestRobber(Card):
    def __init__(self,owner):
        self.name = "Nest Robber"
        self.cost = "1R"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Dinosaur"
        self.text = "Haste. 2/1"
        self.abilities = ["Haste"]
        self.targets = []
        self.owner = owner
        self.power = 2
        self.tou = 1

class LightningHounds(Card):
    def __init__(self,owner):
        self.name = "Lightning Hounds"
        self.cost = "2RR"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Hound"
        self.text = "First strike. 3/2"
        self.abilities = ["First strike"]
        self.targets = []
        self.owner = owner
        self.power = 3
        self.tou = 2

class FlametongueKavu(Card):
    def __init__(self,owner):
        self.name = "Flametongue Kavu"
        self.cost = "3R"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Kavu"
        self.text = "When Flametongue Kavu enters the battlefield, it deals 4 damage to target creature. 4/2"
        self.abilities = []
        self.targets = [["OwnCreature", "OpponentCreature"]]
        self.owner = owner
        self.power = 4
        self.tou = 2

    def effect(self, game, targets):
        targets[0].takeDamage(4)

class PathofPeace(Card):
    def __init__(self, owner):
        self.name = "Path of Peace"
        self.cost = "3W"
        self.supertype = ""
        self.ctype = "Sorcery"
        self.subtype = ""
        self.text = "Destroy target creature. It's owner gains 4 life."
        self.targets = [["OwnCreature", "OpponentCreature"]]
        self.owner = owner

    def effect(self, game, targets):
        targets[0].owner.gainLife(4)
        targets[0].destroy()

class HumanToken(Card):
    def __init__(self,owner):
        self.name = "Human"
        self.cost = "0"
        self.supertype = ""
        self.ctype = "Creature"
        self.subtype = "Human"
        self.text = ""
        self.abilities = []
        self.targets = []
        self.owner = owner
        self.power = 1
        self.tou = 1

class GathertheTownsfolk(Card):
    def __init__(self, owner):
        self.name = "Gather the Townsfolk"
        self.cost = "1W"
        self.supertype = ""
        self.ctype = "Sorcery"
        self.subtype = ""
        self.text = "Create two 1/1 white Human creature tokens. \\ Fateful hour — If you have 5 or less life, create five of those tokens instead."
        self.targets = []
        self.owner = owner

    def effect(self, game, targets):
        tokens = 2
        if self.owner.life <= 5:
            tokens = 5
        for i in range(tokens):
            game.createPermanent(HumanToken(self.owner), self.owner)

class TimelyReinforcements(Card):
    def __init__(self, owner):
        self.name = "Timely Reinforcements"
        self.cost = "2W"
        self.supertype = ""
        self.ctype = "Sorcery"
        self.subtype = ""
        self.text = "If you have less life than an opponent, you gain 6 life. If you control fewer creatures than an opponent, create three 1/1 white Soldier creature tokens."
        self.targets = []
        self.owner = owner

    def effect(self, game, targets):
        if self.owner.life < game.opponent.life:
            self.owner.gainLife(6)
        if len(self.owner.creatures) < len(game.opponent.creatures):
            for i in range(3):
                game.createPermanent(HumanToken(self.owner), self.owner)
