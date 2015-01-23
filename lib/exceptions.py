class ArgumentError(Exception):
    def __init__(self, argName):
        super().__init__(self, argName)


class ArgumentNullError(Exception):
    def __init__(self, argName):
        super().__init__(self, argName)


class BadCommand(Exception):
    def __init__(self, cmdName):
        super().__init__(self, cmdName)


class BadExit(Exception):
    def __init__(self, exitCode, msg=""):
        super().__init__(self, msg)
        self.exitCode = exitCode
