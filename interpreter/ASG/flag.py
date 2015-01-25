__author__ = 'sandeepd'


class Flag:
    def __init__(self, name, value=1):
        self.name = name
        self.value = value

    def __repr__(self):
        return "Flag(name={}, value={})".format(self.name, self.value)