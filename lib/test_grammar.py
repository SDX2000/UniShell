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

from pprint import pprint

from docopt import docopt
from arpeggio import PTNodeVisitor, visit_parse_tree
from arpeggio.cleanpeg import ParserPEG

debug = False

# grammar = """
#    escape        = r'\\\\.'
#    string        = '"' (escape / r'[^"]')* '"'
#    program          = string
# """

grammar = """
    WS            = r'[ \t]+'
    EOL           = "\n"/";"
    identifier         = r'[a-zA-Z_](\w|_)*'
    comment       = "#" r'.*'
    
    bare_str      = r'[a-zA-Z_.:*?/@~{}](\w|[.:*?/@~{}])*'

    escape        = r'\\\\.'
    quoted_str    = '"' (escape/ WS / expr)* '"'

    literal       = quoted_str / bare_str / number
    
    flag          = ("-" identifier / "--" identifier)
    cmd           = identifier (WS (flag / expr))*

    expr_cmd      = cmd / expr
    eval_var      = ("$" identifier / r'\$\{.*?\}')
    eval_expr_cmd = "$(" WS? expr_cmd WS? ")"

    expr          = eval_var / eval_expr_cmd / literal


    statement         = WS? expr_cmd? WS? comment? WS?
    program          = (statement EOL)* statement? EOF
"""


class UniShellVisitor(PTNodeVisitor):
    def visit_escape(self, node, children):
        return children

    def visit_program(self, node, children):
        return children

    def visit_string(self, node, children):
        print("STRING NODE VALUE:", node.value)
        return children


def parse(source):
    gParser = ParserPEG(grammar, "program", skipws=False, debug=debug)
    gVisitor = UniShellVisitor(debug=False)

    # print("parse({}) called".format(repr(source)))

    parse_tree = gParser.parse(source)
    program = visit_parse_tree(parse_tree, gVisitor)
    return program


if __name__ == '__main__':
    args = docopt(__doc__, version="0.0.1")
    # print("Docopt args:{}".format(repr(args)))

    if args['-t']:
        debug = True

    if args['-c']:
        pprint(parse(args['COMMAND']))
    else:
        with open(args['FILE'], "r") as f:
            text = f.read()
            print("------input------")
            print(text)
            print("-----------------")
            pprint(parse(text))

