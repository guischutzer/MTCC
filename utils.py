import math
import copy as c

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


colors = ['W', 'U', 'B', 'R', 'G']
