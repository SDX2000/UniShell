from lib.exceptions import ArgumentError


def toString(obj):
    if callable(obj):
        return obj.__name__

    if issubclass(type(obj), list):
        r = []
        for el in obj:
            r.append(toString(el))
        return r

    if issubclass(type(obj), dict):
        r = {}
        for key in obj:
            r[key] = toString(obj[key])
        return r

    return str(obj)


def printObject(obj):
    print(toString(obj))


def printList(val):
    if not issubclass(type(val), list):
        raise ArgumentError("Val must be a list")

    for elem in val:
        print(toString(elem))


def printDict(val):
    if not issubclass(type(val), dict):
        raise ArgumentError("Val must be a dict")

    for key in sorted(val.keys()):
        print("{}: {}".format(toString(key), toString(val[key])))
