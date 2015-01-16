import sys

from .Command import *
from objects import FileInfo

class Exit(Command):
    def execute(self, args):
        try:
            sys.exit(int(args[0]))
        except IndexError:
            sys.exit(0)
