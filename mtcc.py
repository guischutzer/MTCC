import argparse
from game import Game

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
# parser.add_argument('--decks', help='select decks')
# parser.add_argument('deck1',
#                     help='Deck file (player 1)')
# parser.add_argument('deck2',
#                     help='Deck file (player 2)')

args = parser.parse_args()

jogo = Game(args.agent1, "deck1.txt", args.agent2, "deck2.txt", args.verbose, args.name)
