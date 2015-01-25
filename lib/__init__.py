def partition(predicate, _list):
    return [x for x in _list if not predicate(x)], [x for x in _list if predicate(x)]
