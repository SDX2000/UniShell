import os
import sys

sys.path.append("..")

from objects import FileInfo

class InvalidArgumentError(ValueError):
    def __init__(self, argName, argValue):
        self.argName = argName
        self.argValue = argValue

    def __str__(self):
        return "Invalid argument {}='{}'.".format(self.argName, self.argValue)

def cmdStat(args):
    if not args:
        raise InvalidArgumentError("filePath", ", ".join(args))
    filePath = args[0]
    return FileInfo(filePath)


def cmdChangeDirectory(args):
    try:
        os.chdir(args[0])
    except IndexError:
        return os.getcwd()


def cmdExit(args):
    try:
        sys.exit(args[0])
    except IndexError:
        sys.exit(0)

def cmdClearScreen(args):
    print("\x1Bc", end="")
