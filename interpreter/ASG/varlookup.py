from lib.logger import dbg

class VarLookup:
    def __init__(self, varName):
        if not type(varName) is str:
            raise TypeError("Argument is not a string")
        self.varName = varName

    def __call__(self, context):
        result = context["vars"][self.varName]
        dbg("VarLookup({}) returning:{}".format(repr(self.varName), repr(result)))
        return result

    def __repr__(self):
        return "VarLookup({})".format(repr(self.varName))