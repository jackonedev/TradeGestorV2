from functools import reduce


def productoria(lista):
    return reduce(lambda x, y: x*y, lista)