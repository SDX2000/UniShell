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

from commands import *
from lib.logger import setDebugLevel, dbg
from lib.context import ExecutionContext
from lib.interpreter import UniShellInterpreter

version = "0.0.1"

gInitDir = None
gInterpreter = None
gContext = None

def init():
    global gInitDir
    global gContext
    global gInterpreter

    dbg("Init called")
    if not gInitDir:
        gInitDir = os.getcwd()
    else:
        os.chdir(gInitDir)

    gContext = ExecutionContext()

    gContext.setCmd("stat", cmdStat)
    gContext.setCmd("cd",   cmdChangeDirectory)
    gContext.setCmd("exit", cmdExit)
    gContext.setCmd("quit", cmdExit)
    gContext.setCmd("cls",  cmdClearScreen)
    gContext.setCmd("set",  cmdSet)
    gContext.setCmd("env",  cmdEnv)
    gContext.setCmd("echo", cmdEcho)
    gContext.setCmd("ls",   cmdListDir)
    gContext.setCmd("help", cmdHelp)

    gContext.setVar("INIT_DIR", gInitDir)

    gInterpreter = UniShellInterpreter(gContext)

def printBanner():
    print("UniShell Version {}".format(version))
    print("Copyright (C) Sandeep Datta, 2015")
    print("")



def getCtx():
    return gContext

def startRepl():
    printBanner()
    while True:
        try:
            cwd = os.getcwd()
            inp = input(cwd + "> ")
        except KeyboardInterrupt:
            print("")
            continue
        except EOFError:
            print("")
            break
        gInterpreter.execute(inp)
        
def main(args):
    init()

    doRepl = True
    if args['-c']:
        doRepl = False
        for cmd in args['COMMAND']:
            gInterpreter.execute(cmd)
    
    for arg in args['FILE']:
        doRepl = False
        try:
            scriptPath = path.abspath(arg)
            scriptDir  = path.dirname(scriptPath)
            scriptName = path.basename(arg)
            
            getCtx().setVar("SCRIPT_PATH", scriptPath)
            getCtx().setVar("SCRIPT_DIR", scriptDir)
            getCtx().setVar("SCRIPT_NAME", scriptName)
            
            with open(arg, "r") as f:
                for line in f:
                    gInterpreter.execute(line)
        except FileNotFoundError as e:
            print("ERROR: {}".format(e), file=sys.stderr)
        finally:
            getCtx().delVar("SCRIPT_PATH")
            getCtx().delVar("SCRIPT_DIR")
            getCtx().delVar("SCRIPT_NAME")
                
    if doRepl or args['--interactive']:
        startRepl()


if __name__ == '__main__':
    args = docopt(__doc__, version=version)
    if args['--trace']:
        setDebugLevel(1)
    dbg("Docopt args:{}".format(repr(args)))
    main(args)
