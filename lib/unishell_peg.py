from arpeggio.cleanpeg import ParserPEG
from arpeggio import PTNodeVisitor, visit_parse_tree
from pprint import pprint

#text=str

# An expression we want to evaluate
input_expr = """
 (add 1 2)
sub "a" "b"
"""


# Grammar is defined using textual specification based on PEG language.
grammar = """
        WS           = r'[ \t]+'
        EOL          = "\n"
        number       = r'\d+\.\d+|\d+'
        ident        = r'\w(\w|\d|_)*'
        _str         = r'"[^"]*"'
        expr         = _str / number
        bare_command = ident (WS expr)*
        command      = "(" WS? bare_command WS? ")"
        stmnt        = WS? (bare_command / command)? WS? EOL?
        start        = stmnt+ EOF
"""

class UniShellVisitor(PTNodeVisitor):
    def visit_WS(self, node, children):
        return None

    def visit_EOL(self, node, children):
        return None

    def visit_stmnt(self, node, children):
        retVal = children[0] if children else None
        return retVal

    def visit_start(self, node, children):
        return children

    def visit_bare_command(self, node, children):
        cmd = children[0]
        args = children[1:]
        return ('cmd', cmd, args)

parser = ParserPEG(grammar, "start", skipws = False, debug=False)

parse_tree = parser.parse(input_expr)
print("*************PARSE TREE************")
pprint(parse_tree)
print("***********************************")

result = visit_parse_tree(parse_tree, UniShellVisitor(debug=False))
print("RESULT:", result)
