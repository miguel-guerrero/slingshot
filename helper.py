import re
from collections import namedtuple

verboseErrors=True

DebugInfo = namedtuple('Debuginfo', ['filename', 'lineno', 'function'])

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

#------------------------------------------------------------------------------
# for error reporting
#------------------------------------------------------------------------------
def red(s):   return f"\033[91m{s}\033[00m"
def green(s): return f"\033[92m{s}\033[00m"
def blue(s):  return f"\033[96m{s}\033[00m"

def error(msg, n):
    dbgStr = ''
    if hasattr(n, '_dbg'):
        dbg = n.__getattribute__('_dbg')
        if dbg is not None:
            dbgStr = f"{dbg.filename}:{dbg.lineno} "
            if dbg.function != '<module>':
                dbgStr += f"{dbg.function} "
            if verboseErrors:
                import sys
                if sys.stderr.isatty():
                    r, g, b = red, green, blue
                else:
                    r = g = b = lambda x : x
                with open(dbg.filename) as f:
                    lines = f.readlines()
                from_ = max(1, dbg.lineno-5)
                to_   = min(len(lines), dbg.lineno+5)
                print(f'{dbg.filename}:{dbg.lineno}:1 error: {r(msg)}', file=sys.stderr)
                if from_ > 1:
                    print(f'...', file=sys.stderr)
                for i in range(from_, to_+1):
                    marker = ' '
                    text = lines[i-1]
                    if i == dbg.lineno:
                        marker = '*' 
                        text = b(text)
                    else:
                        text = g(text)
                    print("%s %5d %s" %(marker, i, text), file=sys.stderr, end='')
                if to_ < len(lines):
                    print(f'...', file=sys.stderr)
    msg += f" INTERNAL: {n}" 
    return f"{dbgStr}{msg}"
