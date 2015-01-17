import os
import sys

sys.path.append("..")

from objects import FileInfo
from pprint import pprint

class InvalidArgumentError(ValueError):
    def __init__(self, argName, argValue):
        self.argName = argName
        self.argValue = argValue

    def __str__(self):
        return "Invalid argument {}='{}'.".format(self.argName, self.argValue)

def cmdStat(args, flags, context):
    """
    Display file or file system status
    """
    if not args:
        raise InvalidArgumentError("filePath", ", ".join(args))
    filePath = args[0]
    return FileInfo(filePath)


def cmdChangeDirectory(args, flags, context):
    """
    Change directory
    """
    try:
        os.chdir(args[0])
    except IndexError:
        return os.getcwd()


def cmdExit(args, flags, context):
    """
    Exit shell
    """
    try:
        sys.exit(args[0])
    except IndexError:
        sys.exit(0)

def cmdClearScreen(args, flags, context):
    """
    Clear screen
    """
    print("\x1Bc", end="")

def cmdEcho(args, flags, context):
    """
    Echo arguments to output
    """
    print(' '.join(args))



def cmdSet(args, flags, context):
    """
    Set variable. set [-x] name value
    """
    #print("args:{} flags:{}".format(args, flags))
    if [flag for flag in flags if flag.name == "x"]:
        context["exportedVariables"][args[0]] = args[1]
    else:
        context["variables"][args[0]] = args[1]

def cmdListDir(args, flags, context):
    """
    List contents of target directory
    """
    target = (args[0] if args else None) or '.'
    for x in os.listdir(target):
        print(x)

def cmdEnv(args, flags, context):
    """
    Show environment
    """
    print("Variables")
    print("=========")
    pprint(context["variables"])

    print("\nExported Variables")
    print("==================")
    pprint(context["exportedVariables"])

    print("\nCommands")
    print("========")
    for cmdName in sorted(context["commands"].keys()):
        print("{}\t{}".format(cmdName, context["commands"][cmdName].__doc__))
    
        
    
