from abc import ABCMeta, abstractmethod

class InvalidArgumentError(ValueError):
    def __init__(self, argName, argValue):
        self.argName = argName
        self.argValue = argValue

    def __repr__(self):
        return "Invalid argument {}={}.".format(argName, argValue)

class Command(metaclass=ABCMeta):
    @abstractmethod
    def execute(self, args):
        pass
