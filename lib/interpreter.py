import re
import sys

from arpeggio import PTNodeVisitor, visit_parse_tree, NoMatch
from arpeggio.cleanpeg import ParserPEG

from .logger  import dbg, getDebugLevel
from lib import partition

grammar = """
    WS           = r'[ \t]+'
    EOL          = "\n"/";"
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
    prog         = (stmnt EOL)* stmnt? EOF
"""

#BUG getDebugLevel() is being called even before main has a chance to set it
gDebug = getDebugLevel() > 0
gParser = ParserPEG(grammar, "prog", skipws = False, debug = gDebug)


class Flag:
    def __init__(self, name, value=1):
        self.name = name
        self.value = value
    def __repr__(self):
        return "Flag(name={}, value={})".format(self.name, self.value)

#A prog is a list of commands or literals
class Prog:
    def __init__(self, elements):
        self.elements = elements

    def __call__(self, context):
        result = []
        for elem in self.elements:
            if callable(elem):
                result.append(elem(context))
            else:
                result.append(elem)
        dbg("Prog result:", result)
        return result

    def __repr_(self):
        return repr(self.elements)

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
            cmd = context.getCmd(self.cmdName)
            try:
                result = cmd(self.args, self.flags, context)
            except Exception as e:
                print("ERROR: ({}) {}".format(type(e).__name__, e), file=sys.stderr)
        except KeyError:
            print("ERROR: Unkown command: {}".format(self.cmdName), file=sys.stderr)
        return result

    def __repr__(self):
        return "Command({}, args={}, flags={})".format(self.cmdName, self.args, self.flags)

class String:
    #TODO: Incorporate this regex into the main grammar
    interpRegex = re.compile(r'\$(?P<var0>\w(\w|\d|_)*)|\${(?P<var1>.*?)}|\$\((?P<cmd0>.*?)\)')
    
    def __init__(self, string):
        if not type(string) is str:
            raise TypeError("Argument is not a string")
        self.string = string
    
    def __call__(self, context):
        def replacer(matchObj):
            name = matchObj.group('var0') or matchObj.group('var1')
            result = ""
            if name:
                try:
                    result = context.getVar(name)
                except KeyError:
                    pass
            else:
                cmd = matchObj.group('cmd0')
                if cmd:
                   prog = parse(cmd)
                   result = prog(context)[0]
                       
            dbg("replacer.result=", result)
            return result

        result = self.interpRegex.sub(replacer, self.string)

        dbg("STRING RETURNING:{}".format(result))
        return result

    def __repr__(self):
        return repr(self.string)
        

class UniShellVisitor(PTNodeVisitor):

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
        #TODO fix kludge
        if '.' in node.value:
            result = float(node.value)
        else:
            result = int(node.value)
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

        result = String(children[0])

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
        #A prog is a list of commands or literals
        result = Prog(children)
        dbg("PROG RETURNING:{}".format(repr(result)))
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
        cmdName = children[0]
        args = children[1:]
        result = Command(cmdName, args)

        dbg("CMD RETURNING:{}".format(repr(result)))
        return result

gVisitor = UniShellVisitor(debug = gDebug)

def parse(source):
    dbg("parse({}) called".format(repr(source)))
    parse_tree = gParser.parse(source)
    prog = visit_parse_tree(parse_tree, gVisitor)
    return prog
    
def evaluate(source, context):
    prog = parse(source)
    return prog(context)

def execute(source, context):
    try:
        result = evaluate(source, context)
        dbg("RESULT:", repr(result))
        if result:
            for r in result:
                if r:
                    print(str(r))

    except NoMatch as e:
        print("SYNTAX ERROR: ", e)
