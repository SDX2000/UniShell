import re

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

class Flag:
    def __init__(self, name, value=1):
        self.name = name
        self.value = value
    def __repr__(self):
        return "Flag(name={}, value={})".format(self.name, self.value)

class UniShellVisitor(PTNodeVisitor):

    interpRegex = re.compile(r'\$(?P<var0>\w(\w|\d|_)*)|\${(?P<var1>.*?)}|\$\((?P<cmd0>.*?)\)')

    def __init__(self, interpreter, context, defaults=True, debug=False):
        super().__init__(defaults, debug)
        self.context = context
        self.interpreter = interpreter

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
            cctx = self.context
            name = matchObj.group('var0') or matchObj.group('var1')
            result = ""
            if name:
                try:
                    result = cctx.getVar(name)
                except KeyError:
                    pass
            else:
                cmd = matchObj.group('cmd0')
                if cmd:
                   result = self.interpreter.evaluate(cmd)
                   result = ''.join([str(r) for r in result])
                       
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
        result = children
        dbg("PROG RETURNING:{}".format(repr(result)))
        return result

    def execCmd(self, cmdName, allArgs):
        args = flags = []
        
        if allArgs:
            args, flags = partition(lambda x: isinstance(x, Flag), allArgs)

        dbg("args:{} flags:{}".format(args, flags))

        result = ""

        try:
            cmd = self.context.getCmd(cmdName)
            try:
                result = cmd(args, flags, self.context)
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



class UniShellInterpreter:
    def __init__(self, context):
        debug = getDebugLevel() > 0
        self.parser = ParserPEG(grammar, "prog", skipws = False, debug = debug)
        self.visitor = UniShellVisitor(self, context, debug = debug)

    def evaluate(self, prog):
        dbg("++++evaluate('{}') called".format(prog))
        parse_tree = self.parser.parse(prog)
        result = visit_parse_tree(parse_tree, self.visitor)
        return result

    def execute(self, prog):
        try:
            result = self.evaluate(prog)
            dbg("RESULT:", repr(result))
            if result:
                if issubclass(type(result), list):
                    for r in result:
                        if r:
                            print(str(r))
                else:
                    if result:
                        print(str(result))
        except NoMatch as e:
            print("SYNTAX ERROR: ", e)
