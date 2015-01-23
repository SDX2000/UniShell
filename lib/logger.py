import sys

debugLevel = 0


def dbg(*str, **kwargs):
    if debugLevel:
        print(*str, **kwargs)


def setDebugLevel(level):
    global debugLevel
    debugLevel = level


def getDebugLevel():
    return debugLevel


def format_arg_value(arg_val):
    """ Return a string representing a (name, value) pair.
    
    >>> format_arg_value(('x', (1, 2, 3)))
    'x=(1, 2, 3)'
    """
    arg, val = arg_val
    return "%s=%r" % (arg, val)


def logfn(fn, write=sys.stdout.write):
    """ logfn calls to a function.
    
    Returns a decorated version of the input function which "logfnes" calls
    made to it by writing out the function's name and the arguments it was
    called with.
    """
    import functools
    # Unpack function's arg count, arg names, arg defaults
    code = fn.__code__
    argcount = code.co_argcount
    argnames = code.co_varnames[:argcount]
    fn_defaults = fn.__defaults__ or []
    argdefs = dict(zip(argnames[-len(fn_defaults):], fn_defaults))

    @functools.wraps(fn)
    def wrapped(*v, **k):
        # Collect function arguments by chaining together positional,
        # defaulted, extra positional and keyword arguments.
        positional = list(map(format_arg_value, zip(argnames, v)))
        defaulted = [format_arg_value((a, argdefs[a]))
                     for a in argnames[len(v):] if a not in k]
        nameless = list(map(repr, v[argcount:]))
        keyword = list(map(format_arg_value, k.items()))
        args = positional + defaulted + nameless + keyword
        write("%s(%s)\n" % (fn.__name__, ", ".join(args)))
        result = fn(*v, **k)
        write("%s(%s) returned: %s\n" % (fn.__name__, ", ".join(args), result))

    return wrapped


if __name__ == '__main__':
    @logfn
    def f(x): pass

    @logfn
    def g(x, y): pass

    @logfn
    def h(x=1, y=2): pass

    @logfn
    def i(x, y, *v): pass

    @logfn
    def j(x, y, *v, **k): pass

    class X(object):
        @logfn
        def m(self, x): pass

        @classmethod
        @logfn
        def cm(klass, x): pass

    def reversed_write(s): sys.stdout.write(''.join(reversed(s)))

    def k(**kw): pass

    k = logfn(k, write=reversed_write)

    f(10)
    g("spam", 42)
    g(y="spam", x=42)
    h()
    i("spam", 42, "extra", "args", 1, 2, 3)
    j(("green", "eggs"), y="spam", z=42)
    X().m("method call")
    X.cm("classmethod call")
    k(born="Mon", christened="Tues", married="Weds")

