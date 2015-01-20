import os
import sys

sys.path.append("..")

from objects import FileInfo
from pprint import pprint

#TODO: Change back calls to String objects once the string interpolation regex
#is incorporated in the main grammar

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
    filePath = args[0](context)
    return FileInfo(filePath)


def cmdChangeDirectory(args, flags, context):
    """
    Change directory
    """
    try:
        os.chdir(args[0](context))
    except IndexError:
        pass

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
    #NOTE: args must be a list of Strings or literals
    
    msg = ' '.join(map(lambda x: x(context) if callable(x) else str(x), args))
    #print("ECHO>", msg)
    return msg


def cmdSet(args, flags, context):
    """
    Set variable.

    Syntax:-
        set [-x] name value

        -x    Export variable to child processes
    """
    #print("args:{} flags:{}".format(args, flags))

    name = args[0](context)
    value = args[1](context)
    exported = len([flag for flag in flags if flag.name == "x"]) > 0

    context.setVar(name, value, exported)
    

def cmdListDir(args, flags, context):
    """
    List contents of target directory. If no directory is specified use
    current directory as target.

    Syntax: -
        ls [target_dir]
    """
    target = (args[0](context) if args else None) or '.'
    for x in os.listdir(target):
        print(x)

def cmdEnv(args, flags, context):
    """
    Show environment
    """
    print("Variables")
    print("=========")
    for varName in context.getVarNames():
        value = context.getVar(varName)
        print("{}{}={}".format("(exported) " if context.isExported(varName) else "", varName, value))
    
        
def cmdHelp(args, flags, context):
    """
    Show commands
    """
    print("Commands")
    print("========")
    for cmdName in context.getCmdNames():
        print("{}\t{}".format(cmdName, context.getCmd(cmdName).__doc__))
