from lib.logger import dbg


class String:
    def __init__(self, parts):
        dbg("String init:", parts)
        self.parts = parts

    def __call__(self, context):
        result = ""

        for part in self.parts:
            if callable(part):
                result += str(part(context))
            else:
                result += str(part)

        dbg("String({}) returning:{}".format(repr(self.parts), repr(result)))

        return result

    def __repr__(self):
        return "String({})".format(repr(self.parts))


