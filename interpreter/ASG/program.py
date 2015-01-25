from lib.logger import dbg

__author__ = 'sandeepd'


class Program:
    def __init__(self, expressions):
        self.expressions = expressions

    def __call__(self, context):
        result = []
        for expr in self.expressions:
            if callable(expr):
                result.append(expr(context))
            else:
                result.append(expr)  # A literal
        dbg("Program result:", result)
        return result

    def __repr__(self):
        return repr("Program({})".format(repr(self.expressions)))