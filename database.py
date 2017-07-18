class DataBase:

    def __init__(self, filename):
        self.db = {}

        f = open(filename, 'r')
        self.content = []
        line = f.readline()
        while line:
            self.content.append(line.splitlines[0])
            line = f.readline()

        f.close()

    def readCard(self, cardName):

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

        return None


    def getCard(self, cardName):
        if self.db[cardName]:
            return self.db[cardName]

        read = readCard(cardName)
        if read is not None:
            return read

        print('Card not found in the database. Adding card... (enter \'q\' anytime to quit)')
        return self.addCard(cardName)

    def addCard(self, cardName):

        if cardName != '':
            c = input("Is this name correct: " + cardName + "? (Y/n/q) ")
            if c == "" or c == "y" or c == "yes":
                name = cardName
            elif c == "q":
                return
            elif:
                cardName = ''

        if cardName == '':
            name = input("Card name: ")
        if name == "q":
            return

        cost = input("Card cost: ")
        if cost == "q":
            return

        text = input("Card text: ")
        if text == "q":
            return

        ctype = input("Card type: ")
        if ctype == "q":
            return
        supertype = input("Card supertype: ")
        if supertype == "q":
            return
        subtype = input("Card subtype: ")
        if subtype == "q":
            return

        if ctype == 'Creature':
            power = input("Card power: ")
            if power == "q":
                return

            tou = input("Card toughness: ")
            if tou == "q":
                return
        else:
            power = ''
            tou = ''

        self.db[name] = Card(name, cost, text, ctype, supertype, subtype, power, tou)

        return self.db[name]

    def saveDataBase(self, filename):
        f = open(filename, 'w')

        for card in self.db:
            print(self.db[card], f)

        f.close()
