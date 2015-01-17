#!/usr/bin/env python3

import sys
sys.path.extend(["lib"])

import os
import string
import readline
import collections
from pprint import pprint
from arpeggio import PTNodeVisitor, visit_parse_tree, NoMatch
from arpeggio.cleanpeg import ParserPEG

from commands import *

debug = False

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


grammar = """
    WS           = r'[ \t]+'
    EOL          = "\n"
    number       = r'\d+\.\d+|\d+'
    ident        = r'\w(\w|\d|_)*'
    quoted_str   = r'"[^"]*"'
    bare_str     = r'(\w|[.:*?/@~])*'
    string       = quoted_str / bare_str
    expr         = string / number
    bare_command = ident (WS expr)*
    command      = "(" WS? bare_command WS? ")"
    stmnt        = WS? (bare_command / command)? WS?
    prog         = (stmnt EOL)+ / (stmnt EOF)
"""

parser = ParserPEG(grammar, "prog", skipws = False, debug=debug)


class UniShellVisitor(PTNodeVisitor):

    def visit_WS(self, node, children):
        return None

    def visit_EOL(self, node, children):
        return None

    def visit_stmnt(self, node, children):
        retVal = children[0] if children else None
        return retVal

    def visit_quoted_str(self, node, children):
        #print("STR NODE VALUE:", )
        #print("STR CHILDREN:", children)
        if node.value:
            retVal = node.value[1:]
            retVal = retVal[:-1]
            #print("__str:", retVal)
            return retVal

    def visit_prog(self, node, children):
        return children

    def visit_bare_command(self, node, children):
        cmdName = children[0]
        args = children[1:]

        #print("Cmdname:{} args:{}".format(cmdName, args))

        try:
            cmd = gCommandTable[cmdName]
        except KeyError:
            print("ERROR: Unkown command: {}".format(cmdName), file=sys.stderr)
            return None

        try:
            retVal = cmd(args)
            return retVal
        except Exception as e:
            print("ERROR: ({}) {}".format(type(e).__name__, e), file=sys.stderr)
        

visitor = UniShellVisitor(debug=debug)

def processProg(prog):
    #print("++++++++++processProg('{}') called".format(prog))
    try:
        parse_tree = parser.parse(prog)
        result = visit_parse_tree(parse_tree, visitor)
        if result:
            if isinstance(result, collections.Iterable):
                for elem in result:
                    print(elem)
            else:
                print(result)
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
        if args[1] == "-c":
            retVal = processProg(' '.join(args[2:]))
        else:
            with open(args[1], "r") as f:
                for line in f:
                    retVal = processProg(line)
    else:
        printBanner()
        while True:
            try:
                cwd = os.getcwd()
                inp = input(cwd + "> ")
            except EOFError:
                print("")
                break
            retVal = processProg(inp)


if __name__ == '__main__':
    main(sys.argv)
