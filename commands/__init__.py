import os
import sys


from objects import FileInfo
from pprint import pprint


from lib.logger  import dbg, getDebugLevel
from lib.interpreter import String
from lib.exceptions import ArgumentError

#TODO: Remove calls to String objects once the string interpolation regex
#is incorporated in the main grammar

#TODO: Implement a check signature method which will check the arguments
#against a specified signature.

def cmdStat(args, flags, context):
    """
    Display file or file system status
    """
    if not args:
        ArgumentError("Expecting at least one argument")

        
    
    filePath = args[0](context)
    return FileInfo(filePath)


def cmdChangeDirectory(args, flags, context):
    """
    Change directory
    """
    if args and not type(args[0]) is String:
        ArgumentError("The argument supplied is of incorrect type.")
    
    try:
        os.chdir(args[0](context))
    except IndexError:
        pass

    return os.getcwd()


def cmdExit(args, flags, context):
    """
    Exit shell
    """
    if args and not type(args[0]) is int:
        ArgumentError("The argument supplied is of incorrect type.")
        
    try:
        sys.exit(args[0])
    except IndexError:
        sys.exit(0)


def cmdClearScreen(args, flags, context):
    """
    Clear screen
    """
    if args: 
        ArgumentError("No arguments expected")
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
