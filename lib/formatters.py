import re

_re1 = re.compile(r"\$(\w[_a-zA-Z0-9\.]*)")

def formatObject(fmt, obj):
    def replacer(matchObj):
        val = getattr(obj, matchObj.group(1))
        return str(val)
    return _re1.sub(replacer, fmt)

def getObjectFields(obj, fields):
    return [(field, str(getattr(obj, field))) for field in fields]

def visible(fmt="{}"):
    def realformat(obj):
        obj.visible = True
        obj.fmt = fmt
        return property(obj)
    return realformat
