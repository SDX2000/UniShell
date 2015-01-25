#!/usr/bin/env python3
"""UniShell

Usage:
  unishell [(-t | --trace)] [(-i | --interactive) [--no-banner]] [-s | --syntax] [(-c COMMAND) ...] [FILE ...]
  unishell (-h | --help)
  unishell --version

Options:
  -c                 Execute COMMAND
  -s --syntax        Check syntax but do not run anything
  -i --interactive   Start interactive shell
  -t --trace         Print debug trace messages.
  --no-banner        Suppress unishell banner
  -h --help          Show this screen.
  --version          Show version.
  FILE               UniShell Script file (usually *.ush)
"""

# noinspection PyUnresolvedReferences
import readline
from os import path
from inspect import getmembers

from docopt import docopt
from arpeggio import NoMatch

from commands import *
from formatters import printDict, printList
from lib.logger import setDebugLevel, dbg
from interpreter import parse, evaluate
from lib.prologue import prologue

gBanner = """\
 _    _       _  _____ _          _ _
| |  | |     (_)/ ____| |        | | |
| |  | |_ __  _  (___ | |__   ___| | |
| |  | |  _ \| |\___ \|  _ \ / _ \ | |
| |__| | | | | |____) | | | |  __/ | |
 \____/|_| |_|_|_____/|_| |_|\___|_|_|
"""

version = "0.0.1"

gInitDir = None
gContext = None
gOptions = None
gCheckSyntax = False


def getCommands():
    import commands
    members = getmembers(commands)
    c = filter(lambda x: x[0].startswith("cmd"), members)
    c = map(lambda x: (x[0][3:].lower(), x[1]), c)
    return dict(list(c))


def init():
    global gInitDir
    global gContext
    global gCheckSyntax

    dbg("Init called")

    gCheckSyntax = False

    if not gInitDir:
        gInitDir = os.getcwd()
    else:
        os.chdir(gInitDir)

    commands = getCommands()

    gContext = {
        "vars": commands,
        "exported_vars": {

        },
        "options": {
            "prompt": [lambda a, f, ctx: os.getcwd() + "> "]
            , "echo": [False]
            , "autoprint": [True]
        }
    }

    gContext["vars"]["INIT_DIR"] = gInitDir


def printBanner():
    print(gBanner)
    print("Version {}".format(version))
    print("Copyright (C) Sandeep Datta, 2015")
    print("")


def getCtx():
    return gContext


def getVars():
    return gContext["vars"]


def getOption(name):
    return gContext["options"][name][-1]


def execute(source, context):
    try:
        dbg("----------PARSING---------")
        program = parse(source)

        if not gCheckSyntax:
            dbg("----------RUNNING---------")
            result = program(context)

            dbg("RESULT:", repr(result))
            autoPrint = getOption("autoprint")

            if result and autoPrint:
                for r in result:
                    if issubclass(type(r), list):
                        printList(r)
                    elif issubclass(type(r), dict):
                        printDict(r)
                    elif r is not None:
                        print(str(r))
    except NoMatch as e:
        print("SYNTAX ERROR: ", e)
    else:
        if gCheckSyntax:
            print("Syntax OK.")


def startRepl(noBanner):
    if not noBanner:
        printBanner()
    while True:
        try:
            prompt = getOption("prompt")
            if callable(prompt):
                prompt = prompt(None, None, getCtx())
            line = input(str(prompt))
        except KeyboardInterrupt:
            print("")
            continue
        except EOFError:
            print("")
            break

        execute(line, getCtx())


def evalPrologue():
    dbg("Evaluating prologue")
    try:
        evaluate(prologue, getCtx())
    except NoMatch as e:
        print("SYNTAX ERROR IN PROLOGUE! ", e)


def main(args):
    init()
    global gCheckSyntax

    if args['--syntax']:
        gCheckSyntax = True

    evalPrologue()

    doRepl = True
    if args['-c']:
        doRepl = False
        for cmd in args['COMMAND']:
            execute(cmd, getCtx())

    for arg in args['FILE']:
        doRepl = False
        try:
            scriptPath = path.abspath(arg)
            scriptDir = path.dirname(scriptPath)
            scriptName = path.basename(arg)

            getVars()["SCRIPT_PATH"] = scriptPath
            getVars()["SCRIPT_DIR"] = scriptDir
            getVars()["SCRIPT_NAME"] = scriptName

            with open(arg, "r") as f:
                source = f.read()
                execute(source, getCtx())
        except FileNotFoundError as e:
            print("ERROR: {}".format(e), file=sys.stderr)
        finally:
            del getVars()["SCRIPT_PATH"]
            del getVars()["SCRIPT_DIR"]
            del getVars()["SCRIPT_NAME"]

    if doRepl or args['--interactive']:
        startRepl(args['--no-banner'])


if __name__ == '__main__':
    cmdLineArgs = docopt(__doc__, version=version)
    if cmdLineArgs['--trace']:
        setDebugLevel(1)
    dbg("Docopt args:{}".format(repr(cmdLineArgs)))
    main(cmdLineArgs)

