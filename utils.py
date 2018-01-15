import math

def confirm(c):
    if (c == 'y') or (c == 'Y'):
        return True
    return False

def binom(a, b):
    return math.factorial(a)/(math.factorial(b)*math.factorial(a - b))

colors = ['W', 'U', 'B', 'R', 'G']
