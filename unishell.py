#!/usr/bin/env python3

import sys
sys.path.extend(["lib"])

import os
import string
import readline
from pprint import pprint
from arpeggio import PTNodeVisitor, visit_parse_tree, NoMatch


import unishell_peg
from commands import *



def printBanner():
    print("UniShell Version 0.0.1")
    print("Copyright (C) Sandeep Datta, 2015")
    print("")

gCommandTable = {
    "stat"      : cmdStat
    , "cd"      : cmdChangeDirectory
    , "exit"    : cmdExit
    , "quit"    : cmdExit
    , "cls"     : cmdClearScreen
}

gVariables = {}

class UniShellVisitor(PTNodeVisitor):

    def visit_WS(self, node, children):
        return None

    def visit_EOL(self, node, children):
        return None

    def visit_stmnt(self, node, children):
        retVal = children[0] if children else None
        return retVal

    def visit_prog(self, node, children):
        return children

    def visit_bare_command(self, node, children):
        cmdName = children[0]
        args = children[1:]

        try:
            cmd = gCommandTable[cmdName]
        except KeyError:
            print("ERROR: Unkown command: {}".format(cmdLinePart[0]), file=sys.stderr)
            return

        try:
            retVal = cmd(args)
            if retVal:
                print(retVal)
        except Exception as e:
            print("ERROR: ({}) {}".format(type(e).__name__, e), file=sys.stderr)
        

visitor = UniShellVisitor(debug=False)

def processProg(prog):
    try:
        parse_tree = unishell_peg.parse(prog)
        result = visit_parse_tree(parse_tree, visitor)
        return result
    except NoMatch as e:
        print("SYNTAX ERROR: ", e)

  
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
 - string interpolation "$x, ${x}H, $(time)". The $ sign is only required
   within strings for interpolation.
 - lists, a = [a b c], a.len(), a[0], a[1:]
 - dictionaries d = {x:1 y:2}; d = (dict [a b c d])
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
 - echo
"""
def main(args):
    if len(args) > 1:
        with open(args[1], "r") as f:
            for line in f:
                processProg(line)
    else:
        printBanner()
        while True:
            try:
                cwd = os.getcwd()
                inp = input(cwd + "> ")
            except EOFError:
                print("")
                break
            processProg(inp)


if __name__ == '__main__':
    main(sys.argv)
