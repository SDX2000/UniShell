import sys

debugLevel = 0


def dbg(*s, **kwargs):
    if debugLevel:
        print(*s, **kwargs)


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


def logFn(fn, write=sys.stdout.write):
    """ logFn calls to a function.
    
    Returns a decorated version of the input function which "logFn" calls
    made to it by writing out the function's name and the arguments it was
    called with.
    """
    import functools
    # Unpack function's arg count, arg names, arg defaults
    code = fn.__code__
    argCount = code.co_argcount
    argNames = code.co_varnames[:argCount]
    fn_defaults = fn.__defaults__ or []
    argDefinitions = dict(zip(argNames[-len(fn_defaults):], fn_defaults))

    @functools.wraps(fn)
    def wrapped(*v, **k):
        # Collect function arguments by chaining together positional,
        # defaulted, extra positional and keyword arguments.
        positional = list(map(format_arg_value, zip(argNames, v)))
        defaulted = [format_arg_value((a, argDefinitions[a]))
                     for a in argNames[len(v):] if a not in k]
        nameless = list(map(repr, v[argCount:]))
        keyword = list(map(format_arg_value, k.items()))
        args = positional + defaulted + nameless + keyword
        write("%s(%s)\n" % (fn.__name__, ", ".join(args)))
        result = fn(*v, **k)
        write("%s(%s) returned: %s\n" % (fn.__name__, ", ".join(args), result))

    return wrapped


if __name__ == '__main__':
    @logFn
    def f(x):
        pass

    @logFn
    def g(x, y):
        pass

    @logFn
    def h(x=1, y=2):
        pass

    @logFn
    def i(x, y, *v):
        pass

    @logFn
    def j(x, y, *v, **k):
        pass

    class X(object):
        @logFn
        def m(self, x):
            pass

        @classmethod
        @logFn
        def cm(cls, x):
            pass

    def reversed_write(s):
        sys.stdout.write(''.join(reversed(s)))

    def k(**kw):
        pass

    k = logFn(k, write=reversed_write)

    f(10)
    g("spam", 42)
    g(y="spam", x=42)
    h()
    i("spam", 42, "extra", "args", 1, 2, 3)
    j(("green", "eggs"), y="spam", z=42)
    X().m("method call")
    X.cm("classmethod call")
    k(born="Mon", christened="Tues", married="Weds")

