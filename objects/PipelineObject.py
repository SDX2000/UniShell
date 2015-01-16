import re

re1 = re.compile('([A-Z]+)')

class PipelineObject:
    def __init__(self):
        pass

    def __repr__(self):
        x = ""
        for attrName in sorted(dir(type(self))):
            attr = getattr(type(self), attrName)
            try:
                if attr.fget.visible:
                    name = re1.sub(r' \1', attrName).lower().lstrip()
                    x += ("{}{}: "+attr.fget.fmt+"\n").format(name[0].upper(),
                                                              name[1:],
                                                              getattr(self, attrName))
            except AttributeError:
                pass
        return x
