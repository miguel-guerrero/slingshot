import re
import os
from collections import namedtuple, OrderedDict
from inspect import stack

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
    m = re.search(r'^(.+?)(\d+)(.*)$', n)
    if m:
        n = m.group(1) + f"{int(m.group(2)):05}" + m.group(3)
    return n


#convert to tuple if passed a single element
def tupleize(x):
    if not isinstance(x, tuple):
        x = (x,)
    return x


def setUnion(*lst):
    if lst:
        return set.union(*lst)
    return set()


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

import inspect

def upLocals(ups=1):
    f = inspect.currentframe()
    for i in range(ups):
        f = f.f_back
    return f.f_locals.items()

class IoList:
    def __init__(self, *lst):
        self._dic = OrderedDict()
        self._prev = None
        if lst is not None:
            for x in lst:
                self.assign(x)

    def assign(self, l):
        if l is None:
            return
        if isinstance(l, (list, tuple)):
            for _x in l:
                assert hasattr(_x, 'name')
                self._dic[_x.name] = _x
        else:
            assert hasattr(l, 'name'), f"{l}"
            self._dic[l.name] = l

    def asDict(self):
        return self._dic

    def asList(self):
        return list(self._dic.values())

    def __iadd__(self, x):
        self.assign(x)
        return self

    def __getattr__(self, key):
        if key in self._dic:
            return self._dic[key]
        raise KeyError(f'key {key} not found in {self}')

    def __setattr__(self, key, val):
        if key != "_dic" and key != '_prev':
            self._dic[key] = val
        else:
            object.__setattr__(self, key, val)

    def __len__(self):
        return len(self._dic.keys())

    def __getitem__(self, idx):
        lst = list(self._dic.values())
        return lst[idx]

    def __enter__(self): 
        self._prev = set(k for k,v in upLocals(2))
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback): 
        newList = []
        newLoc = upLocals(2)
        for k,v in newLoc:
            if k not in self._prev:
                newList.append(v)
        self.assign(sorted(newList, key=lambda x : x.name))
        self._prev = None

    def __repr__(self):
        return "[" + ", ".join(f"{v!r}" for k, v in self.asDict().items()) + "]"

#------------------------------------------------------------------------------
#a structure that returns None for not-defined fields
#and can be used as a dict too
#------------------------------------------------------------------------------
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

def getFileLines(filename, lineno, isatty=False, showElip=False, ctxLines=3):
    if isatty:
        g, b = green, blue
    else:
        g = b = lambda x : x
    with open(filename) as f:
        lines = f.readlines()
    from_ = max(1, lineno-5)
    to_   = min(len(lines), lineno+5)
    out = ""
    if showElip and from_ > 1:
        out += f'...\n'
    for i in range(from_, to_+1):
        marker = '  '
        text = lines[i-1]
        if i == lineno:
            marker = '->' 
            text = b(text)
        else:
            text = g(text)
        out += "%s %5d %s" %(marker, i, text)
    if showElip and to_ < len(lines):
        out += '...'
    return out


def showErrorLocation(msg, filename, lineno):
    import sys
    isatty = sys.stderr.isatty()
    r = red if isatty else lambda x : x
    print(f'{filename}:{lineno}:1 error: {r(msg)}',        file=sys.stderr)
    print(getFileLines(filename, lineno, isatty, True, 5), file=sys.stderr)


def getDbgInfo():
    excludeList = ['__init__', '__call__', 'Input', 'Output']
    exclModList = ['chipo.py', 'helper.py', 'hlc.py', 'decorators.py', 'vlog.py', 'functools.py']
    for i in stack():
        filebase = os.path.basename(i.filename)
        if i.function not in excludeList and filebase not in exclModList:
            return DebugInfo(i.filename, i.lineno, i.function)


def error(msg, n):
    dbgStr = ''
    #some nodes have . overriden= 
    dbg = n.__getattribute__('_dbg') if hasattr(n, '_dbg') else getDbgInfo()
    if dbg is not None:
        dbgStr = f"{dbg.filename}:{dbg.lineno} "
        if dbg.function != '<module>':
            dbgStr += f"{dbg.function} "
        if verboseErrors:
            showErrorLocation(msg, dbg.filename, dbg.lineno)
    msg += f" INTERNAL: {n}" 
    return f"{dbgStr}{msg}"

