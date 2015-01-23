import os
import sys

from objects import FileInfo
from lib.exceptions import ArgumentError

# TODO: Remove calls to String objects once the string interpolation regex
# is incorporated in the main grammar

#TODO: Implement a check signature method which will check the arguments
#against a specified signature.

def cmdStat(args, flags, context):
    """
    Display file or file system status
    """
    if not args:
        raise ArgumentError("No argument supplied.")

    filePath = args[0]

    if not type(args[0]) is str:
        raise ArgumentError("Argument must be a string.")

    return FileInfo(filePath)


def cmdChangeDirectory(args, flags, context):
    """
    Change directory
    """
    if args and not type(args[0]) is str:
        raise ArgumentError("The argument supplied is of incorrect type.")

    try:
        os.chdir(args[0])
    except IndexError:
        pass

    return os.getcwd()


def cmdExit(args, flags, context):
    """
    Exit shell
    """
    if args and not type(args[0]) is int:
        raise ArgumentError("The argument supplied is of incorrect type.")

    try:
        sys.exit(args[0])
    except IndexError:
        sys.exit(0)


def cmdClearScreen(args, flags, context):
    """
    Clear screen
    """
    if args:
        raise ArgumentError("No arguments expected")
    print("\x1Bc", end="")


def cmdEcho(args, flags, context):
    """
    Echo arguments to output
    """
    #NOTE: args must be a list of Strings or literals

    msg = ' '.join(map(lambda x: str(x), args))
    print(msg)
    return msg


def cmdSet(args, flags, context):
    """
    Set variable.

    Syntax:-
        set [-x] name value

        -x    Export variable to child processes
    """
    # print("args:{} flags:{}".format(args, flags))

    try:
        name = args[0]
        if not type(name) is str:
            raise ArgumentError("The variable name needs to be a string.")

        value = args[1]
    except IndexError as e:
        raise ArgumentError("Incorrect number of arguments specified") from e

    exported = any(flag.name == "x" for flag in flags)

    context["vars"][name] = value

    if exported:
        context["exported_vars"][name] = True

    return value


def cmdListDir(args, flags, context):
    """
    List contents of target directory. If no directory is specified use
    current directory as target.

    Syntax: -
        ls [target_dir]
    """
    target = (args[0] if args else None) or '.'

    if not type(target) is str:
        raise ArgumentError("The argument needs to be a string.")

    for x in os.listdir(target):
        print(x)


def cmdEnv(args, flags, context):
    """
    Show environment
    """
    print("Variables")
    print("=========")
    for varName in context["vars"].keys():
        value = context["vars"][varName]
        if not callable(value):
            print("{}{}={}".format("(exported) " if varName in context["exported_vars"] else "", varName, value))


def cmdHelp(args, flags, context):
    """
    Show commands
    """
    print("Commands")
    print("========")
    for varName in context["vars"].keys():
        value = context["vars"][varName]
        if callable(value):
            print("{}{}={}".format("(exported) " if varName in context["exported_vars"] else "", varName, value))
