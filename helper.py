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

def bitsFor(n: int):
    assert n >= 0
    bits, limit = 1, 2
    while limit <= n:
        limit <<= 1
        bits += 1
    return bits
