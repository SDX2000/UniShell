import sys

from .Command import *
from objects import FileInfo

class ClearScreen(Command):
    def execute(self, args):
        print("\x1Bc", end="")

