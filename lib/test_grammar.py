#!/usr/bin/env python3
"""test_grammar

Usage:
  test_grammar ((-c COMMAND) | FILE) [-t]


Options:
  -c                 Execute COMMAND
  FILE               UniShell Script file (usually *.ush)
  -h --help          Show this screen.
  --version          Show version.
"""

from docopt import docopt

import sys
import traceback

from arpeggio import PTNodeVisitor, visit_parse_tree, NoMatch
from arpeggio.cleanpeg import ParserPEG

from pprint import pprint

gDebug = False

##grammar = """
##    escape        = r'\\\\.'
##    string        = '"' (escape / r'[^"]')* '"'
##    prog          = string
##"""

grammar = """
    WS            = r'[ \t]+'
    EOL           = "\n"/";"
    ident         = r'[a-zA-Z_](\w|_)*'
    comment       = "#" r'.*'
    
    bare_str      = r'[a-zA-Z_.:*?/@~{}](\w|[.:*?/@~{}])*'

    escape        = r'\\\\.'
    quoted_str    = '"' (escape/ WS / expr)* '"'

    literal       = quoted_str / bare_str / number
    
    flag          = ("-" ident / "--" ident)
    cmd           = ident (WS (flag / expr))*

    expr_cmd      = cmd / expr
    eval_var      = ("$" ident / r'\$\{.*?\}')
    eval_expr_cmd = "$(" WS? expr_cmd WS? ")"

    expr          = eval_var / eval_expr_cmd / literal


    stmnt         = WS? expr_cmd? WS? comment? WS?
    prog          = (stmnt EOL)* stmnt? EOF
"""


class UniShellVisitor(PTNodeVisitor):
    def visit_escape(self, node, children):
        return children

    def visit_prog(self, node, children):
        return children

    def visit_string(self, node, children):
        print("STRING NODE VALUE:", node.value)
        return children


def parse(source):
    gParser = ParserPEG(grammar, "prog", skipws=False, debug=gDebug)
    gVisitor = UniShellVisitor(debug=False)

    # print("parse({}) called".format(repr(source)))

    parse_tree = gParser.parse(source)
    prog = visit_parse_tree(parse_tree, gVisitor)
    return prog


if __name__ == '__main__':
    args = docopt(__doc__, version="0.0.1")
    # print("Docopt args:{}".format(repr(args)))

    if args['-t']:
        gDebug = True

    if args['-c']:
        pprint(parse(args['COMMAND']))
    else:
        with open(args['FILE'], "r") as f:
            text = f.read()
            print("------input------")
            print(text)
            print("-----------------")
            pprint(parse(text))

