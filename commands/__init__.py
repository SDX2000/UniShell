import os
import sys

from pipeline import FileInfo
from lib.exceptions import ArgumentError

# TODO: Remove calls to String object once the string interpolation regex
# is incorporated in the main grammar

# TODO: Implement a check signature method which will check the arguments
# against a specified signature.


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


def cmdCd(args, flags, context):
    """
    Change directory
    """
    if args and not type(args[0]) is str:
        raise ArgumentError("The argument supplied is of incorrect type.")

    try:
        os.chdir(args[0])
        # TODO: Revert hack
        return None  # Do not print the current dir when changing the directory
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


def cmdCls(args, flags, context):
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
    # NOTE: args must be a list of Strings or literals

    msg = ' '.join(map(lambda x: str(x), args))
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


def cmdPushOpt(args, flags, context):
    """
    Set and push script option on the options stack.

    Syntax:-
        pushopt option value
    """
    # print("args:{} flags:{}".format(args, flags))

    try:
        name = args[0]
        if not type(name) is str:
            raise ArgumentError("The option name needs to be a string.")
        if name not in context["options"]:
            raise ArgumentError("Invalid option {}".format(name))
        value = args[1]
    except IndexError as e:
        raise ArgumentError("Incorrect number of arguments specified") from e

    if type(value) is str:
        if value.lower() in ["on", "true", "yes"]:
            value = True
        elif value.lower() in ["off", "false", "no"]:
            value = False

    context["options"][name].append(value)

    return value


def cmdPeekOpt(args, flags, context):
    """
    Get script option.

    Syntax:-
        peekopt option
    """
    # print("args:{} flags:{}".format(args, flags))

    try:
        name = args[0]
        if not type(name) is str:
            raise ArgumentError("The option name needs to be a string.")
        if name not in context["options"]:
            raise ArgumentError("Invalid option {}".format(name))
    except IndexError as e:
        raise ArgumentError("Incorrect number of arguments specified") from e

    return context["options"][name][-1]


def cmdPopOpt(args, flags, context):
    """
    Pop script option from the options stack.

    Syntax:-
        popopt option
    """
    # print("args:{} flags:{}".format(args, flags))

    try:
        name = args[0]
        if not type(name) is str:
            raise ArgumentError("The option name needs to be a string.")
        if name not in context["options"]:
            raise ArgumentError("Invalid option {}".format(name))
    except IndexError as e:
        raise ArgumentError("Incorrect number of arguments specified") from e

    optHist = context["options"][name]

    if len(optHist) <= 1:
        raise IndexError("Cannot pop the default value off.")

    return optHist.pop()


def cmdOptions(args, flags, context):
    return context["options"]


def cmdLs(args, flags, context):
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
