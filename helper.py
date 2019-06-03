import re

#------------------------------------------------------------------------------
# Helper function to print arguments to a constructor omiting defaults
#------------------------------------------------------------------------------
def reprStr(*nameValDefVal):
    s = []
    for name, val, defVal in reversed(nameValDefVal):
        if val != defVal or s:
            s.insert(0, f", {name}={val!r}")
    return "".join(s)


def listRepr(*args):
    return ", ".join([f"{x!r}" for x in args])


#pad suffix number if present for nicer sort
def modkey(n): 
    m = re.search(r'^(.+?)(\d+)$', n)
    if m:
        n = m.group(1) + f"{int(m.group(2)):05}"
    return n


#convert to tuple if passed a single element
def tupleize(x):
    if not isinstance(x, tuple):
        x = (x,)
    return x


#a structure that returns None for not-defined fields
#and can be used as a dict too
class Struct:
    def __init__(self, **kwargs):
        self.argDict = kwargs

    def setDict(self, argDict):
        self.argDict = argDict

    def getDict(self):
        return self.argDict

    def __getattr__(self, key):
        if key in self.argDict.keys():
            return self.argDict[key]
        raise KeyError(f'key {key} not found in {self}')

    def __setattr__(self, key, val):
        if key != "argDict":
            self.argDict[key] = val
        else:
            object.__setattr__(self, key, val)

    __getitem__ = __getattr__
    __setitem__ = __setattr__

    def __repr__(self):
        return "Struct(" + ", ".join(f"{k}={v!r}" 
                for k, v in self.argDict.items()) + ")"
