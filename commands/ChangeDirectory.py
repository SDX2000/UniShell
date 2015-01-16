import os

from .Command import *
from objects import FileInfo

class ChangeDirectory(Command):
    def execute(self, args):
        try:
            os.chdir(args[0])
        except IndexError:
            return os.getcwd()
