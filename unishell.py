#!/usr/bin/env python3

import sys
sys.path.extend(["lib"])

import os
import string
import readline
from commands import *
from pprint import pprint


def printBanner():
    print("UniShell Version 0.0.1")
    print("Copyright (C) Sandeep Datta, 2015")
    print("")


cmds = {"stat" : cmdStat
        , "cd" : cmdChangeDirectory
        , "exit" : cmdExit
        , "quit" : cmdExit
        , "cls" : cmdClearScreen
}

"""
TODO:
 - handle KeyboardInterrupt
 - Be case insensitive

Implement console features:-
 - Autocomplete
 - History

Implement language features:-
 - user defined prompts
 - strings, quoted strings, escapes, slicing, string operations
 - string interpolation "$x, $(time)". The $ sign is only required within strings for interpolation.
 - lists, a = [a b c], a.len()
 - conditionals if/else/elif, pattern matching with match
 - regular expression literals /abc/ig, =~
 - loops
 - numbers, (num x), (str n)
 - wildcards *,**,?
 - functions
 - variables, scopes, persistence (use json/sqlite?), x = 10, print x
 - command substitution (pwd)
 - exceptions (try, catch, finally)
 - pipes
 - redirection
 - external commands, set search paths
 
Implement commands :-
 - ls
 - copy
 - rsync
 - exec $code
 - alias
"""
def main(args):
    if len(args) > 1:
        with open(args[1], "r") as f:
            for line in f:
                processInput(line)
    else:
        printBanner()
        while True:
            try:
                cwd = os.getcwd()
                inp = input(cwd + "> ")
            except EOFError:
                print("")
                break

            if not processInput(inp):
                break

def processInput(cmdLine):
    if not cmdLine:
        return True
    
    cmdLine = cmdLine.strip()

    #Skip comments
    if cmdLine.startswith("#"):
        return True

    cmdLinePart = cmdLine.split()

    if not cmdLinePart:
        return True

    try:
        cmd = cmds[cmdLinePart[0]]
    except KeyError:
        print("ERROR: Unkown command: {}".format(cmdLinePart[0]), file=sys.stderr)
        return True

    try:
        retVal = cmd(cmdLinePart[1:])
        if retVal:
            print(retVal)
    except Exception as e:
        print("ERROR: ({}) {}".format(type(e).__name__, e), file=sys.stderr)

    return True


if __name__ == '__main__':
    main(sys.argv)
