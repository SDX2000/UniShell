from lib.exceptions import ArgumentError


def printList(val):
    if not issubclass(type(val), list):
        raise ArgumentError("Val must be a list")

    for elem in val:
        print(elem)


def printDict(val):
    if not issubclass(type(val), dict):
        raise ArgumentError("Val must be a dict")

    for key in val.keys():
        print("{}: {}".format(key, val[key]))
