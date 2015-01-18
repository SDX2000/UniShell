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
import sys
import os

moduleBaseDir = os.path.dirname(__file__)
sys.path.extend([os.path.join(moduleBaseDir, "lib")])

import os
import re
import string
import readline
import collections

from os import path
from pprint import pprint
from docopt import docopt
from arpeggio import PTNodeVisitor, visit_parse_tree, NoMatch
from arpeggio.cleanpeg import ParserPEG

from commands import *

debug = False
version = "0.0.1"
parser = None
visitor = None

gContext = None
gInitDir = None

class Variable:
    def __init__(self, name, value, exported=False):
        self.name = name
        self.value = value
        self.exported = exported

    def __repr__(self):
        return "Variable(name='{}', value={}, exported={})".format(self.name, repr(self.value), self.exported)


class Context:
    def __init__(self):
        self.variables = {}
        self.commands = {}

    def getCmdNames(self):
        return sorted(self.commands.keys())

    def getCmd(self, name):
        return self.commands[name]

    def setCmd(self, name, command):
        self.commands[name] = command

    def delCmd(self, name):
        try:
            del self.commands[name]
        except KeyError:
            pass

    def getVarNames(self):
        return sorted(self.variables.keys())
    
    def getVar(self, name):
        return self.variables[name]

    def setVar(self, name, value, exported=False):
        self.variables[name] = Variable(name, value, exported)

    def delVar(self, name):
        try:
            del self.variables[name]
        except KeyError:
            pass

def init():
    global parser
    global visitor
    global gContext
    global gInitDir

    dbg("Init called")
    if not gInitDir:
        gInitDir = os.getcwd()
    else:
        os.chdir(gInitDir)
    
    parser = ParserPEG(grammar, "prog", skipws = False, debug=debug)
    visitor = UniShellVisitor(debug=debug)

    gContext = Context()

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

    

def printBanner():
    print("UniShell Version {}".format(version))
    print("Copyright (C) Sandeep Datta, 2015")
    print("")

def dbg(*str, **kwargs):
    if debug:
        print(*str, **kwargs)

def getCtx():
    return gContext

grammar = """
    WS           = r'[ \t]+'
    EOL          = "\n"
    number       = r'\d+\.\d+|\d+'
    ident        = r'[a-zA-Z_](\w|_)*'
    quoted_str   = r'"[^"]*"'
    bare_str     = r'[a-zA-Z_.:*?/@~${}](\w|[.:*?/@~${}])*'
    string       = quoted_str / bare_str
    literal      = string / number
    expr_cmd     = cmd / expr
    expr         = cmd_interp / literal
    flag         = ("-" ident / "--" ident)
    comment      = "#" r'.*'
    cmd          = ident (WS (flag / expr))*
    cmd_interp   = "$(" WS? cmd WS? ")"
    stmnt        = WS? expr_cmd? WS? comment? WS?
    prog         = (stmnt EOL)+ / (stmnt EOF) / EOF
"""


def partition(pred, _list):
    return ([x for x in _list if not pred(x)], [x for x in _list if pred(x)])

class Flag:
    def __init__(self, name, value=1):
        self.name = name
        self.value = value
    def __repr__(self):
        return "Flag(name='{}', value={})".format(self.name, self.value)

class UniShellVisitor(PTNodeVisitor):

    interpRegex = re.compile(r'\$(?P<var0>\w(\w|\d|_)*)|\${(?P<var1>.*?)}|\$\((?P<cmd0>.*?)\)')

    def visit_WS(self, node, children):
        return None

    def visit_EOL(self, node, children):
        return None

    def visit_stmnt(self, node, children):
        dbg("STMNT NODE VALUE:", repr(node.value))
        dbg("STMNT CHILDREN:", children)
        result = children[0] if children else None
        dbg("STMNT RETURNING:{}".format(repr(result)))
        return result

    def visit_number(self, node, children):
        dbg("NUMBER NODE VALUE:", repr(node.value))
        dbg("NUMBER CHILDREN:", children)
        result = node.value
        dbg("NUMBER RETURNING:{}".format(repr(result)))
        return result

    def visit_comment(self, node, children):
        return None

    def visit_flag(self, node, children):
        dbg("FLAG NODE VALUE:", repr(node.value))
        dbg("FLAG CHILDREN:", children)
        result = Flag(children[0])
        dbg("FLAG RETURNING:{}".format(repr(result)))
        return result

    def visit_quoted_str(self, node, children):
        dbg("QUOTED STRING NODE VALUE:", repr(node.value))
        dbg("QUOTED STRING CHILDREN:", children)
        result = None
        if node.value:
            result = node.value[1:]
            result = result[:-1]
        dbg("QUOTED STRING RETURNING:{}".format(repr(result)))
        return result

    def visit_bare_str(self, node, children):
        dbg("BARE STRING NODE VALUE:", repr(node.value))
        dbg("BARE STRING CHILDREN:", children)
        result = node.value
        dbg("BARE STRING RETURNING:{}".format(repr(result)))
        return result

    def visit_ident(self, node, children):
        dbg("IDENT NODE VALUE:", repr(node.value))
        dbg("IDENT CHILDREN:", children)
        result = node.value
        dbg("IDENT RETURNING:{}".format(repr(result)))
        return result

    
    def visit_string(self, node, children):
        dbg("STRING NODE VALUE:", repr(node.value))
        dbg("STRING CHILDREN:", children)

        def replacer(matchObj):
            cctx = getCtx()
            name = matchObj.group('var0') or matchObj.group('var1')
            result = ""
            if name:
                try:
                    result = cctx.getVar(name).value
                except KeyError:
                    pass
            else:
                cmd = matchObj.group('cmd0')
                if cmd:
                   result = evaluate(cmd)
            dbg("replacer.result=", result)
            return result

        string = children[0]
        result = self.interpRegex.sub(replacer, string)

        dbg("STRING RETURNING:{}".format(result))
        return result

    def visit_expr(self, node, children):
        dbg("EXPR NODE VALUE:", repr(node.value))
        dbg("EXPR CHILDREN:", repr(children))
        result = children[0]
        dbg("EXPR RETURNING:{}".format(repr(result)))
        return result
    
    def visit_prog(self, node, children):
        dbg("PROG NODE VALUE:", repr(node.value))
        dbg("PROG CHILDREN:", repr(children))
        result = children[0] if children else None
        dbg("PROG RETURNING:{}".format(repr(result)))
        return result

    def execCmd(self, cmdName, allArgs):
        args = flags = []
        
        if allArgs:
            args, flags = partition(lambda x: isinstance(x, Flag), allArgs)

        dbg("args:{} flags:{}".format(args, flags))

        result = ""

        try:
            cmd = getCtx().getCmd(cmdName)
            try:
                result = cmd(args, flags, gContext)
            except Exception as e:
                print("ERROR: ({}) {}".format(type(e).__name__, e), file=sys.stderr)
        except KeyError:
            print("ERROR: Unkown command: {}".format(cmdName), file=sys.stderr)
        return result

    def visit_cmd_interp(self, node, children):
        dbg("CMD_INTERP NODE VALUE:", repr(node.value))
        dbg("CMD_INTERP CHILDREN:", repr(children))

        result = children[0]
        #result.echo = False

        dbg("CMD_INTERP RETURNING:{}".format(repr(result)))
        return result
    
    def visit_cmd(self, node, children):
        dbg("CMD NODE VALUE:", repr(node.value))
        dbg("CMD CHILDREN:", repr(children))

        #TODO: return a (stdin, stderr) tuple instead? Throw a BadExit
        #exception on a bad exit code.
        #args = children[1] if len(children) > 1 else []
        args = children[1:]
        result = self.execCmd(children[0], args)

        dbg("CMD RETURNING:{}".format(repr(result)))
        return result


def evaluate(prog):
    dbg("++++evaluate('{}') called".format(prog))
    parse_tree = parser.parse(prog)
    result = visit_parse_tree(parse_tree, visitor)
    return result


def execute(prog):
    try:
        result = evaluate(prog)
        dbg("RESULT:", repr(result))
        if result:
            if type(result) is list:
                for r in result:
                    if r:
                        print(str(r))
            else:
                if result:
                    print(str(result))
    except NoMatch as e:
        print("SYNTAX ERROR: ", e)
        

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
        execute(inp)
        
def main(args):
    init()

    doRepl = True
    if args['-c']:
        doRepl = False
        for cmd in args['COMMAND']:
            execute(cmd)
    
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
                    execute(line)
        except FileNotFoundError as e:
            print("ERROR: {}".format(e), file=sys.stderr)
        finally:
            getCtx().delVar("SCRIPT_DIR")
                
    if doRepl or args['--interactive']:
        startRepl()


if __name__ == '__main__':
    args = docopt(__doc__, version=version)
    if args['--trace']:
        debug = True
    dbg("Docopt args:{}".format(repr(args)))
    main(args)
