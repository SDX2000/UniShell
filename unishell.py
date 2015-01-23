#!/usr/bin/env python3
"""UniShell

Usage:
  unishell [(-t | --trace)] [(-i | --interactive)] [(-c COMMAND) ...] [FILE ...]
  unishell (-h | --help)
  unishell --version

Options:
  -c                 Execute COMMAND
  FILE               UniShell Script file (usually *.ush)
  -i --interactive   Start interactive shell
  -t --trace         Print debug trace messages.
  -h --help          Show this screen.
  --version          Show version.
"""

import os
import re
import sys
import string
import readline
import collections

from os import path
from pprint import pprint
from docopt import docopt
from arpeggio import NoMatch

from commands import *
from lib.logger import setDebugLevel, dbg
from lib.interpreter import parse, evaluate

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
gExported = None
gOptions = None


def init():
    global gInitDir
    global gContext

    dbg("Init called")
    if not gInitDir:
        gInitDir = os.getcwd()
    else:
        os.chdir(gInitDir)

    # TODO: Make gContext local
    gContext = {
        "vars": {
            "stat": cmdStat
            , "cd": cmdChangeDirectory
            , "exit": cmdExit
            , "quit": cmdExit
            , "cls": cmdClearScreen
            , "set": cmdSet
            , "env": cmdEnv
            , "echo": cmdEcho
            , "ls": cmdListDir
            , "help": cmdHelp
            , "INIT_DIR": gInitDir
        },
        "exported_vars": {

        }
    }


def printBanner():
    print(gBanner)
    print("Version {}".format(version))
    print("Copyright (C) Sandeep Datta, 2015")
    print("")


def getCtx():
    return gContext


def getVars():
    return gContext["vars"]


def execute(source, context):
    result = evaluate(source, context)
    dbg("RESULT:", repr(result))
    if result:
        for r in result:
            if r:
                print(str(r))


def startRepl():
    printBanner()
    while True:
        try:
            cwd = os.getcwd()
            line = input(cwd + "> ")
        except KeyboardInterrupt:
            print("")
            continue
        except EOFError:
            print("")
            break
        try:
            execute(line, getCtx())
        except NoMatch as e:
            print("SYNTAX ERROR: ", e)


def main(args):
    init()

    doRepl = True
    if args['-c']:
        doRepl = False
        for cmd in args['COMMAND']:
            try:
                execute(cmd, getCtx())
            except NoMatch as e:
                print("SYNTAX ERROR: ", e)

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
                try:
                    evaluate(source, getCtx())
                except NoMatch as e:
                    print("SYNTAX ERROR: ", e)
        except FileNotFoundError as e:
            print("ERROR: {}".format(e), file=sys.stderr)
        finally:
            del getVars()["SCRIPT_PATH"]
            del getVars()["SCRIPT_DIR"]
            del getVars()["SCRIPT_NAME"]

    if doRepl or args['--interactive']:
        startRepl()


if __name__ == '__main__':
    args = docopt(__doc__, version=version)
    if args['--trace']:
        setDebugLevel(1)
    dbg("Docopt args:{}".format(repr(args)))
    main(args)

