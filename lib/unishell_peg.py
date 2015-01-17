from arpeggio.cleanpeg import ParserPEG

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
        prog        = stmnt+ EOF
"""

parser = ParserPEG(grammar, "prog", skipws = False, debug=False)

def parse(prog):
    parse_tree = parser.parse(prog)
    return parse_tree
