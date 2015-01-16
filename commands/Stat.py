from .Command import *
from objects import FileInfo

class Stat(Command):
    def execute(self, args):
        if not args:
            raise InvalidArgumentError("filePath", args)
        filePath = args[0]
        return FileInfo(filePath)
