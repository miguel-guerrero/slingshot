from collections import OrderedDict
import inspect


def upLocals(levelsUp=1):
    """returns locals on a number of specific levels up"""
    f = inspect.currentframe()
    for i in range(levelsUp):
        f = f.f_back
    return f.f_locals.items()


class IoList:
    """keeps track of io definitions, created for example as

       io.x = In(Bits(1), name='x')
       io.y = Out(Bits(1), name='y')
    or
       io += [In(Bits(1), name='x'), Out(Bits(2), name='y')]
    or
        with io:
            x = In(Bits(1))
            y = Out(Bits(2))
    """
    def __init__(self, *lst):
        self._dic = OrderedDict()
        self._prev = None
        if lst is not None:
            for x in lst:
                self.assign(x)

    def assignSingle(self, _io):
        assert hasattr(_io, 'name'), f"{_io} must have a name in IoList"
        self._dic[_io.name] = _io

    def assign(self, ios):
        if ios is None:
            return
        if isinstance(ios, (list, tuple)):
            for _io in ios:
                self.assignSingle(_io)
            return
        self.assignSingle(ios)

    def asDict(self) -> dict:
        return self._dic

    def asList(self) -> list:
        return list(self._dic.values())

    def __iadd__(self, x):
        self.assign(x)
        return self

    def __getattr__(self, key):
        if key in self._dic:
            return self._dic[key]
        raise KeyError(f'IoList: key {key} not found in {self}')

    def __setattr__(self, key, val):
        if key != "_dic" and key != '_prev':
            self._dic[key] = val
        else:
            object.__setattr__(self, key, val)

    def __len__(self) -> int:
        return len(self._dic.keys())

    def __getitem__(self, idx):
        values = list(self._dic.values())
        return values[idx]

    def __enter__(self):
        # capture locals above this level
        self._prev = set(k for k, v in upLocals(2))
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # capture locals above this level
        newLoc = upLocals(2)
        newList = [v for k, v in newLoc if k not in self._prev]
        self.assign(sorted(newList, key=lambda x: x.name))
        self._prev = None

    def __repr__(self):
        return \
            "[" + ", ".join(f"{v!r}" for k, v in self.asDict().items()) + "]"
