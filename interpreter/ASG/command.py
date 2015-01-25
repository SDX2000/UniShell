import sys
import traceback
from . import Flag
from lib import partition
from lib.logger import dbg


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