

# todo: transform this class into a Dictionary child class

class DataBase:

    def __init__(self, filename):
        self.db = {}

        self.f = open(filename, 'rw')
        self.content = []
        line = f.readline()
        while line:
            self.content.append(line.splitlines[0])
            line = f.readline()


    def searchCard(self, cardName):
        if self.db[cardName]:
            return self.db[cardName]

        for i in range(len(self.content)):
            if self.content[i] == cardName:
                card = Card(self.content[i],   self.content[i+1],
                            self.content[i+2], self.content[i+3],
                            self.content[i+4], self.content[i+5],
                            self.content[i+5], self.content[i+7])
                self.db[cardName] = card

                for j in range(8):
                    self.content.pop(i)

                return self.db[cardName]

        print('Card not found in the database. Adding card...')
        return self.addCard(cardName)

    def addCard(self, cardName):
        if cardName == '':
            name = input("Card name: ")
        else:
            name = cardName

        cost = input("Card cost: ")
        text = input("Card text: ")
        ctype = input("Card type: ")
        supertype = input("Card supertype: ")
        subtype = input("Card subtype: ")

        if ctype == 'Creature':
            power = input("Card power: ")
            tou = input("Card toughness: ")
        else:
            power = ''
            tou = ''

        self.db[name] = Card(name, cost, text, ctype, supertype, subtype, power, tou)

        return self.db[name]
