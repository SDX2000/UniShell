"""
Execution context
"""

class Variable:
    def __init__(self, name, value, exported=False):
        self.name = name
        self.value = value
        self.exported = exported

    def __repr__(self):
        return "Variable(name='{}', value={}, exported={})".format(self.name, repr(self.value), self.exported)

#TODO Check if we really need to differentiate between commands and variables. If not then replace
#the execution context class with a single dictionary containing both commands and variables.
#Use a separate dictionary for script options.
class ExecutionContext:
    def __init__(self):
        self.variables = {}
        self.commands = {}

    def getCmdNames(self):
        return sorted(self.commands.keys())

    def getCmd(self, name):
        return self.commands[name]

    def setCmd(self, name, command):
        self.commands[name] = command

    def delCmd(self, name):
        try:
            del self.commands[name]
        except KeyError:
            pass

    def getVarNames(self):
        return sorted(self.variables.keys())
    
    def getVar(self, name):
        return self.variables[name].value

    def isExported(self, varName):
        return self.variables[varName].exported

    def setVar(self, name, value, exported=False):
        self.variables[name] = Variable(name, value, exported)

    def delVar(self, name):
        try:
            del self.variables[name]
        except KeyError:
            pass
