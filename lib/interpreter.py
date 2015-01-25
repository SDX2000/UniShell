import re
import sys
import codecs
import traceback

from arpeggio import PTNodeVisitor, visit_parse_tree
from arpeggio.cleanpeg import ParserPEG

from lib.logger import dbg, getDebugLevel
from lib import partition

grammar = """
    WS               = r'[ \t]+'
    EOL              = "\n"/";"
    integer          = r'[+-]?\d+'
    float            = r'[+-]?\d+\.\d+((e|E)[+-]?\d+)?'
    number           = float / integer
    identifier       = r'[a-zA-Z_](\w|_)*'
    quoted_str       = r'"[^"]*"'
    bare_str         = r'[a-zA-Z_.:*?/@~{}](\w|[.:*?/@~{}])*'
    string           = quoted_str / bare_str
    literal          = string / number
    expr_cmd         = cmd / expr
    expr             = eval_var / eval_expr_cmd / literal
    flag             = ("-" identifier / "--" identifier)
    comment          = "#" r'.*'
    cmd              = identifier (WS (flag / expr))*
    eval_bare_var    = "$" identifier
    eval_quoted_var  = "${" identifier "}"
    eval_var         = eval_bare_var / eval_quoted_var
    eval_expr_cmd    = "$(" WS? expr_cmd WS? ")"
    eval             = eval_var / eval_expr_cmd
    statement        = WS? expr_cmd? WS? comment? WS?
    program          = (statement EOL)* statement? EOF
"""

# BUG getDebugLevel() is being called even before main has a chance to set it
# gDebug = getDebugLevel() > 0
gDebug = False
gProgramParser = ParserPEG(grammar, "program", skipws=False, debug=gDebug)
gEvalParser = ParserPEG(grammar, "eval", skipws=False, debug=gDebug)


class Flag:
    def __init__(self, name, value=1):
        self.name = name
        self.value = value

    def __repr__(self):
        return "Flag(name={}, value={})".format(self.name, self.value)


class Program:
    def __init__(self, expressions):
        self.expressions = expressions

    def __call__(self, context):
        result = []
        for expr in self.expressions:
            if callable(expr):
                result.append(expr(context))
            else:
                result.append(expr)  # A literal
        dbg("Program result:", result)
        return result

    def __repr__(self):
        return repr("Program({})".format(repr(self.expressions)))


class Command:
    def __init__(self, cmdName, allArgs):
        if not cmdName or type(cmdName) is not str:
            raise Exception("Bad command name:{}".format(repr(cmdName)))

        self.cmdName = cmdName

        if allArgs:
            self.args, self.flags = partition(lambda x: isinstance(x, Flag), allArgs)
        else:
            self.args = self.flags = []

        dbg("args:{} flags:{}".format(self.args, self.flags))

    def __call__(self, context):
        result = ""

        try:
            cmd = context["vars"][self.cmdName]
            try:
                self.args = list(map(lambda x: x(context) if callable(x) else x, self.args))
                result = cmd(self.args, self.flags, context)
            except Exception as e:
                print("ERROR: ({}) {}".format(type(e).__name__, e), file=sys.stderr)
                dbg(traceback.format_exc(), file=sys.stderr)
        except KeyError:
            print("ERROR: Unknown command: {}".format(self.cmdName), file=sys.stderr)
        dbg("{} result:{}".format(repr(self), result))
        return result

    def __repr__(self):
        return "Command({}, args={}, flags={})".format(self.cmdName, self.args, self.flags)


class String:
    splitterRegex = re.compile(r'(\$[a-zA-Z_](?:\w|\d|_)*|\$\{[a-zA-Z_](?:\w|\d|_)*\}|\$\(.*?\))')

    def __init__(self, string):
        if not type(string) is str:
            raise TypeError("Argument is not a string")
        self.string = string
        dbg("String init:", string)

        parts = self.splitterRegex.split(self.string)

        def unescape(s):
            return codecs.decode(s, 'unicode_escape')

        self.parts = list(map(lambda x: parseEvalExpr(x) if x.startswith('$') else unescape(x), parts))

        dbg("String parts:", repr(self.parts))

    def __call__(self, context):
        result = ""

        for part in self.parts:
            if callable(part):
                result += str(part(context))
            else:
                result += str(part)

        dbg("String({}) returning:{}".format(repr(self.string), repr(result)))

        return result

    def __repr__(self):
        return "String({})".format(repr(self.parts))


class VarLookup:
    def __init__(self, varName):
        if not type(varName) is str:
            raise TypeError("Argument is not a string")
        self.varName = varName

    def __call__(self, context):
        result = context["vars"][self.varName]
        dbg("VarLookup({}) returning:{}".format(repr(self.varName), repr(result)))
        return result

    def __repr__(self):
        return "VarLookup({})".format(repr(self.varName))


class UniShellVisitor(PTNodeVisitor):
    def visit_WS(self, node, children):
        return None

    def visit_EOL(self, node, children):
        return None

    def visit_statement(self, node, children):
        dbg("STATEMENT NODE VALUE:", repr(node.value))
        dbg("STATEMENT CHILDREN:", children)
        result = children[0] if children else None
        dbg("STATEMENT RETURNING:{}".format(repr(result)))
        return result

    def visit_integer(self, node, children):
        dbg("INTEGER NODE VALUE:", repr(node.value))
        dbg("INTEGER CHILDREN:", children)

        result = int(node.value)
        dbg("INTEGER RETURNING:{}".format(repr(result)))
        return result

    def visit_float(self, node, children):
        dbg("FLOAT NODE VALUE:", repr(node.value))
        dbg("FLOAT CHILDREN:", children)

        result = float(node.value)
        dbg("FLOAT RETURNING:{}".format(repr(result)))
        return result

    def visit_number(self, node, children):
        dbg("NUMBER NODE VALUE:", repr(node.value))
        dbg("NUMBER CHILDREN:", children)
        result = children[0]
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

    def eval_bare_var(self, node, children):
        dbg("EVAL_BARE_VAR NODE VALUE:", repr(node.value))
        dbg("EVAL_BARE_VAR CHILDREN:", children)
        result = children[0]
        dbg("EVAL_BARE_VAR RETURNING:{}".format(repr(result)))
        return result

    def visit_eval_quoted_var(self, node, children):
        dbg("EVAL_QUOTED_VAR NODE VALUE:", repr(node.value))
        dbg("EVAL_QUOTED_VAR CHILDREN:", children)
        result = children[0]
        dbg("EVAL_QUOTED_VAR RETURNING:{}".format(repr(result)))
        return result

    def visit_eval_var(self, node, children):
        dbg("EVAL_VAR NODE VALUE:", repr(node.value))
        dbg("EVAL_VAR CHILDREN:", children)
        result = VarLookup(children[0])
        dbg("EVAL_VAR RETURNING:{}".format(repr(result)))
        return result

    def visit_eval(self, node, children):
        dbg("EVAL NODE VALUE:", repr(node.value))
        dbg("EVAL CHILDREN:", children)
        result = children[0]
        dbg("EVAL RETURNING:{}".format(repr(result)))
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

    def visit_identifier(self, node, children):
        dbg("IDENTIFIER NODE VALUE:", repr(node.value))
        dbg("IDENTIFIER CHILDREN:", children)
        result = node.value
        dbg("IDENTIFIER RETURNING:{}".format(repr(result)))
        return result

    def visit_string(self, node, children):
        dbg("STRING NODE VALUE:", repr(node.value))
        dbg("STRING CHILDREN:", children)

        result = String(children[0])

        dbg("STRING RETURNING:{}".format(result))
        return result

    def visit_expr(self, node, children):
        dbg("EXPR NODE VALUE:", repr(node.value))
        dbg("EXPR CHILDREN:", repr(children))
        result = children[0]
        dbg("EXPR RETURNING:{}".format(repr(result)))
        return result

    def visit_program(self, node, children):
        dbg("PROGRAM NODE VALUE:", repr(node.value))
        dbg("PROGRAM CHILDREN:", repr(children))
        # A program is a list of commands or literals
        result = Program(children)
        dbg("PROGRAM RETURNING:{}".format(repr(result)))
        return result

    def visit_cmd_interp(self, node, children):
        dbg("CMD_INTERP NODE VALUE:", repr(node.value))
        dbg("CMD_INTERP CHILDREN:", repr(children))

        result = children[0]
        # result.echo = False

        dbg("CMD_INTERP RETURNING:{}".format(repr(result)))
        return result

    def visit_cmd(self, node, children):
        dbg("CMD NODE VALUE:", repr(node.value))
        dbg("CMD CHILDREN:", repr(children))

        # TODO: return a (stdin, stderr) tuple instead? Throw a BadExit
        # exception on a bad exit code.
        # args = children[1] if len(children) > 1 else []
        cmdName = children[0]
        args = children[1:]
        result = Command(cmdName, args)

        dbg("CMD RETURNING:{}".format(repr(result)))
        return result


gVisitor = UniShellVisitor(debug=gDebug)


def parse(source):
    dbg("parse({}) called".format(repr(source)))
    parse_tree = gProgramParser.parse(source)
    program = visit_parse_tree(parse_tree, gVisitor)
    return program


def parseEvalExpr(source):
    dbg("parseEvalExpr({}) called".format(repr(source)))
    parse_tree = gEvalParser.parse(source)
    program = visit_parse_tree(parse_tree, gVisitor)
    return program


def evaluate(source, context):
    dbg("----------PARSING---------")
    program = parse(source)
    dbg("----------RUNNING---------")
    return program(context)


