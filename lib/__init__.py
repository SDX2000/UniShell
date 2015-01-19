def partition(pred, _list):
    return ([x for x in _list if not pred(x)], [x for x in _list if pred(x)])
