import math
import copy as c
import itertools

def confirm(c):
    if (c == 'y') or (c == 'Y'):
        return True
    return False

def binom(a, b):
    return math.factorial(a)/(math.factorial(b)*math.factorial(a - b))

# In: a list of lists; Out: a list with all the combinations of
# elements of each list

def listCombinations(lst):

    if len(lst) == 0:
        return []

    if len(lst) == 1:
        lists = []
        for item in lst[0]:
            lists += [[item]]
        return lists

    top = lst[-1]

    finalLists = []
    for item in top:
        lists = listCombinations(lst[:-1])
        for l in lists:
            l += [item]
        finalLists += lists

    return finalLists

# In : a list; Out: a list of all subsets (as lists) of said list

def listArrangements(lst):

    if len(lst) == 0:
        return []

    if len(lst) == 1:
        return [[], [lst[0]]]

    finalLists = []
    lists = listArrangements(lst[1:])
    for item in lists:
        finalLists.append([lst[0]] + item)
        finalLists.append([] + item)
    return finalLists

def intraPermutations(d):

    if len(d) == 0:
        return {}

    if len(d) == 1:
        dictList = []
        element = next(iter(d.keys()))
        for perm in itertools.permutations(d[element]):
            newDict = {element : perm}
            dictList.append(newDict)
        return dictList

    dictList = []
    element = next(iter(d.keys()))
    curList = d[element]
    newDict = c.copy(d)
    del newDict[element]
    for perm in itertools.permutations(curList):
        for dictFromLists in intraPermutations(newDict):
            dictFromLists[element] = perm
            dictList.append(dictFromLists)
    return dictList

def getOrdinal(number):
    return ordinals[number]

ordinals = ['zeroth', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth']
colors = ['W', 'U', 'B', 'R', 'G']
