# ------------------------------------------------------------------------------
# Copyright (c) 2018-Present, Miguel A. Guerrero
# All rights reserved.
#
# This is free software released under GNU Lesser GPL license version 3.0
# (LGPL 3.0)
#
# See http://www.gnu.org/licenses/lgpl-3.0.txt for a full text
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Please send bugs and suggestions to: miguel.a.guerrero@gmail.com
# -------------------------------------------------------------------------------
from enum import Enum
import copy
from collections import defaultdict
from itertools import takewhile
from functools import reduce

import gencore
import varname
import helper
import iolist

trackDebugInfo = True
serialNumber = varname.makeCounter()


# ------------------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------------------
def simplify(e):
    if isinstance(e, Expr):
        return e.simplify()
    return e


def sortedAsList(s):
    return sorted(s, key=lambda x: helper.modkey(x.name))


# if passed a tuple of statements creates a block with them,
# but if passed a tuple containing only a block just returns it
def flattenBlock(aTuple: tuple):
    if len(aTuple) == 1 and isinstance(aTuple[0], Block):
        return aTuple[0]
    return Block(*aTuple)


# Short-cut to generate n copies of an object. e.g Input() ** 2
def Times(n: int, obj):
    return [obj] + [copy.copy(obj) for i in range(1, n)]


# ------------------------------------------------------------------------------
# For hybrid g2p / chipo implementations
# ------------------------------------------------------------------------------
class ApiGenerator(gencore.GeneratorBase):
    def __init__(self, module, targetDir, targetExt):
        super().__init__(targetDir, targetExt)
        self.module = module

    def runGeneration(self, name, passedParamDict):
        import vlog
        assert self.module.name == name
        for modName, modStr in vlog.dump(self.module.getAst()):
            pass
        return modStr, self.module


def vlogToFile(exportMod, targetDir='build', targetExt='.v'):
    ag = ApiGenerator(exportMod, targetDir, targetExt)
    return ag.run(exportMod.getName(), exportMod.paramDict)


def generateG2p(modBaseName, passedParamDict, defaultParamDict, genFun):
    from g2p import processParams
    name, paramDict, params = processParams(
        modBaseName, passedParamDict, defaultParamDict)
    mod = genFun(name, params)
    mod.paramDict = paramDict
    return vlogToFile(mod)  # returns mod


# ------------------------------------------------------------------------------
# Track debug info in all objects created
# ------------------------------------------------------------------------------
class Meta(type):
    def __new__(cls, name, bases, dct):
        x = super().__new__(cls, name, bases, dct)
        cls._dbgi = None
        return x

    def __call__(self, *args, **kwargs):
        self._dbgi = helper.getDbgInfo() if trackDebugInfo else None
        return type.__call__(self, *args, **kwargs)


# ------------------------------------------------------------------------------
# AstNode : Parent of all AST nodes
# ------------------------------------------------------------------------------
class AstNode(metaclass=Meta):

    def assigned(self) -> set:
        return set()

    def used(self) -> set:
        return set()

    def paramUsed(self) -> set:
        return set()

    def typesUsed(self) -> set:
        return set()

    def driven(self) -> set:
        return set()

    def declared(self) -> set:
        return set()

    def asList(self) -> list:
        return []

    def __init__(self):
        self._dbg = self._dbgi

    # apply a set-returning method 'm' to non-None items in list and return
    # the union of all returned sets
    def apply(self, m, lst: list) -> set:
        return helper.setUnion(*[getattr(x, m)() for x in lst
                                 if x is not None and x is not ...])

    def __repr__(self):
        raise NotImplementedError


# -----------------------------------------------------------
# AstNode -> Comm
# Node to keep textual comments that get preserved on AST
# -----------------------------------------------------------
class Comm(AstNode):
    def __init__(self, *lines):
        super().__init__()
        self.lines = lines

    def __repr__(self):
        return f'Comm{self.lines!r}'


# ------------------------------------------------------------------------------
# AstNode -> AstStatement : things that can show up under a module will derive
# from this AST node
# ------------------------------------------------------------------------------
class AstStatement(AstNode):
    def __init__(self):
        super().__init__()


# -----------------------------------------------------------
# AstNode -> AstStatement -> Clocked
# -----------------------------------------------------------
class Clocked(AstStatement):
    def __init__(self, clock=None, reset=None, autoReset=True, name=None):
        super().__init__()
        self.clock = clock
        self.reset = reset
        self.autoReset = autoReset
        self.body = Block(name=name)
        self.hasWfe = False   # Wfe = wait for event

    def __iadd__(self, x):
        self.body += x
        return self

    def __getitem__(self, stmts):
        return self.Body(*helper.tupleize(stmts))

    def Body(self, *stmts):
        appendStms(self.body, stmts)
        return self

    def asList(self) -> list:
        return self.body.asList()

    def assigned(self) -> set:
        return self.body.assigned()

    def paramUsed(self) -> set:
        return self.body.paramUsed()

    def typesUsed(self) -> set:
        return self.body.typesUsed()

    def used(self) -> set:
        return self.body.used().union([self.clock, self.reset])

    # assign a name
    def Name(self, name):
        self.body.name = name
        return self

    def needsReset(self) -> set:
        assigned = self.body.assigned()
        withDefault = set(x for x in assigned if x.default is not None)
        return withDefault

    def genResetLogic(self):
        assigned = self.body.assigned()
        withDefault = set(x for x in assigned if x.default is not None)
        if not withDefault:
            return self.body
        if len(withDefault) < len(assigned):
            missing = sorted(x.name for x in assigned - withDefault)
            raise ValueError(
                helper.error(
                    "The following items need a default (in Clocked " +
                    f"block with reset): {missing}", self))
        withDefault = sorted([SigAssign(x, x.default) for x in withDefault],
                             key=lambda x: x.lhs.name)
        name, self.body.name = self.body.name, None
        return Block(If(self.reset.onExpr()).
                     Then(*withDefault).
                     Else(self.body), name=name)

    def addResetLogic(self):
        if self.autoReset and self.reset:
            self.body = self.genResetLogic()
        return self

    def __repr__(self):
        suffix = helper.reprStr(["autoReset", self.autoReset, True],
                                ["name", self.body.name, ""])
        return f'Clocked({self.clock}, reset={self.reset!r}' + \
               f'{suffix}).Body({self.body!r})'


# -----------------------------------------------------------
# AstNode -> AstStatement -> Combo
# -----------------------------------------------------------
class Combo(AstStatement):
    def __init__(self, *body, name=None):
        super().__init__()
        if body:
            self.body = flattenBlock(body)
        else:
            self.body = Block()
        if name:
            self.body.name = name

    def __iadd__(self, x):
        self.body += x
        return self

    def __getitem__(self, stmts):
        return self.Body(*helper.tupleize(stmts))

    def Body(self, *stmts):
        self.body += stmts
        return self

    def asList(self) -> list:
        return self.body.asList()

    def assigned(self) -> set:
        return self.body.assigned()

    def paramUsed(self) -> set:
        return self.body.paramUsed()

    def typesUsed(self) -> set:
        return self.body.typesUsed()

    def used(self) -> set:
        return self.body.used()

    # assign a name
    def Name(self, name):
        self.body.name = name
        return self

    def __repr__(self):
        return f'Combo(body={self.body!r})'


# -----------------------------------------------------------
# AstNode -> AstStatement -> Declare
# -----------------------------------------------------------
class Declare(AstStatement):
    def __init__(self, x):
        super().__init__()
        if not isinstance(x, (Signal, Var)):
            raise TypeError(helper.error("Only Signa/Var can be Declare'd", x))
        self.x = x

    @property
    def name(self) -> str:
        return self.x.name

    def declared(self) -> set:
        return set([self.x])

    def __repr__(self):
        return f"Declare({self.x!r})"


# -----------------------------------------------------------
# Instance related
# -----------------------------------------------------------
def _paramToTextDict(paramMapDict):
    def name(p):
        return p.name if isinstance(p, Param) else p

    return {name(p): name(v) for p, v in paramMapDict.items()}


# -----------------------------------------------------------
# AstNode -> AstStatement -> InstanceBase
# -----------------------------------------------------------
class InstanceBase(AstStatement):
    def __init__(self, insName):
        super().__init__()
        self.insName = insName

    def module(self):
        return None

    # must be overriden
    def used(self) -> set:
        raise NotImplementedError(helper.error("", self))

    def modName(self) -> set:
        raise NotImplementedError(helper.error("", self))

    def _textParamMapDict(self):
        raise NotImplementedError(helper.error("", self))

    def _insName(self) -> str:
        if self.insName is not None:
            return self.insName
        return f"unamed_ins_{serialNumber()}"


# -----------------------------------------------------------
# AstNode -> AstStatement -> InstanceBase -> InstanceLegacy
# -----------------------------------------------------------
# for existing verilog modules
class InstanceLegacy(InstanceBase):
    def __init__(self, moduleName, textParamMapDict, textIoMapDict,
                 insName=None):
        self.moduleName = moduleName
        self.textParamMapDict = textParamMapDict
        self.textIoMapDict = textIoMapDict
        super().__init__(insName)

    def used(self) -> set:
        return set()

    def paramUsed(self) -> set:
        return set()  # TODO

    def typesUsed(self) -> set:
        return set()  # TODO

    def modName(self) -> str:
        return self.moduleName

    def _textParamMapDict(self):
        return self.textParamMapDict

    def __repr__(self):
        args = f", insName={self.insName!r}" \
               if self.insName is not None else ""

        return f"InstanceLegacy({self.moduleName!r}, " + \
               f"textParamMapDict={self.textParamMapDict}, " + \
               f"textIoMapDict={self.textIoMapDict}{args})"


# -----------------------------------------------------------
# AstNode -> AstStatement -> InstanceBase -> InstanceG2p
# -----------------------------------------------------------
# for g2p module exports
class InstanceG2p(InstanceBase):
    def __init__(self, modExp, textParamMapDict, ioMap, insName=None):
        self.modExp = modExp
        self.textParamMapDict = textParamMapDict.dict \
            if isinstance(textParamMapDict, ParamMap) else textParamMapDict
        self.ioMapDict = ioMap.dict if isinstance(ioMap, PortMap) else ioMap
        super().__init__(insName)

    def module(self):
        return self.modExp

    def paramUsed(self) -> set:
        return set()  # TODO

    def typesUsed(self) -> set:
        return set()  # TODO

    def used(self) -> set:
        inConn = {self.ioMapDict.get(i.name, i) for i in self.modExp.IOs
                  if isinstance(i, gencore.InputBase)}
        return helper.setUnion(*[x.used() for x in inConn])

    def driven(self) -> set:
        outConn = {self.ioMapDict.get(o.name, o) for o in self.modExp.IOs
                   if isinstance(o, gencore.OutputBase)}
        return helper.setUnion(*[x.lvalue() for x in outConn if x is not None])

    def modName(self) -> str:
        return self.modExp.name

    def _textParamMapDict(self):
        return self.textParamMapDict

    def __repr__(self):
        args = f", insName={self.insName!r}" \
               if self.insName is not None else ""

        return f"InstanceG2p({self.modExp!r}, " + \
               f"textParamMapDict={self.textParamMapDict}, " + \
               f"ioMapDict={self.ioMapDict}{args})"


class PortMap:
    def __init__(self, policy=None, **kwargs):
        super().__init__()
        self.policy = policy
        self.dict = kwargs


class ParamMapPolicy:
    pass


class ParamMap:
    def __init__(self, policy=None, **kwargs):
        super().__init__()
        self.policy = policy
        self.dict = kwargs


# -----------------------------------------------------------
# AstNode -> AstStatement -> InstanceBase -> Instance
# -----------------------------------------------------------
# for native chipo modules
class Instance(InstanceBase):
    def __init__(self, mod, paramMap, ioMap, insName=None):
        assert isinstance(paramMap, (dict, ParamMap))
        assert isinstance(ioMap, (dict, PortMap))
        self.mod = mod
        self.paramMapDict = paramMap.dict \
            if isinstance(paramMap, ParamMap) else paramMap
        self.ioMapDict = ioMap.dict if isinstance(ioMap, PortMap) else ioMap
        super().__init__(insName)

    def module(self):
        return self.mod

    def used(self) -> set:
        inConn = {self.ioMapDict.get(i.name, i) for i in self.mod.IOs
                  if isinstance(i, gencore.InputBase)}
        return helper.setUnion(*[x.used() for x in inConn])

    def driven(self) -> set:
        outConn = {self.ioMapDict.get(o.name, o) for o in self.mod.IOs
                   if isinstance(o, gencore.OutputBase)}
        return helper.setUnion(*[x.lvalue() for x in outConn if x is not None])

    def paramUsed(self) -> set:
        conn = [self.ioMapDict.get(io.name, io) for io in self.mod.IOs]
        return helper.setUnion(*[io.paramUsed() for io in conn
                                 if isinstance(io, gencore.IoBase)])

    def typesUsed(self) -> set:
        return set()  # TODO

    def modName(self) -> str:
        return self.mod.name

    def _textParamMapDict(self):
        return _paramToTextDict(self.paramMapDict)

    def __repr__(self):
        args = f", insName={self.insName!r}" \
               if self.insName is not None else ""

        return f"Instance({self.mod!r}, paramMapDict={self.paramMapDict}" \
               f", ioMapDict={self.ioMapDict}{args})"


# ------------------------------------------------------------------------------
# AstNode -> AstProcStatement : things that can go under a procedural contruct
# ------------------------------------------------------------------------------
class AstProcStatement(AstNode):
    def __init__(self):
        super().__init__()

    def applyFunc(self, f) -> None:
        f(self)
        for s in self.all():
            s.applyFunc(f)

    def any(self, f) -> bool:
        if f(self) or any(f(s) for s in self.asList()):
            return True
        return any(s.any(f) for s in self.asList()
                   if hasattr(s, 'any'))

    def all(self, f) -> bool:
        return not self.any(lambda x: not f(x))


# -----------------------------------------------------------
# AstNode -> AstProcStatement -> Block
# -----------------------------------------------------------
class Block(AstProcStatement):
    def __init__(self, *stmts, name=None):
        super().__init__()
        self.stmts = []
        self.name = name
        if len(stmts) == 1 and isinstance(stmts[0], tuple):
            stmts = stmts[0]  # peel off outer tuple
        self += stmts         # invoke __iadd__

    @staticmethod
    def check(x):
        if not isinstance(x, AstProcStatement) and \
           not isinstance(x, Comm) and \
           not isinstance(x, tuple) and \
           not isinstance(x, Declare) and x is not ...:
            raise TypeError(helper.error(
                f'Expecting procedural statement in a Block, got a {type(x)}',
                x
            ))
        return x

    def __iadd__(self, x):
        if isinstance(x, tuple):
            for xi in x:
                self += Block.check(xi)
        elif isinstance(x, Block) and x.name is None:
            for xi in x.asList():  # flatten a nameless block
                self += Block.check(xi)
        elif x is not None:
            self.stmts.append(Block.check(x))
        return self

    def doDo(self, stmts: tuple):
        self.stmts += stmts
        return self

    # def __getitem__(self, stmts):
    #     return self.doDo(helper.tupleize(stmts))

    def __getitem__(self, slc):
        return self.stmts.__getitem__(slc)

    def asList(self):
        return self.stmts

    def Name(self, name):
        self.name = name
        return self

    def assigned(self) -> set:
        return self.apply('assigned',  self.stmts)

    def used(self) -> set:
        return self.apply('used',      self.stmts)

    def paramUsed(self) -> set:
        return self.apply('paramUsed', self.stmts)

    def typesUsed(self) -> set:
        return self.apply('typesUsed', self.stmts)

    def driven(self) -> set:
        return self.apply('driven',    self.stmts)

    def declared(self) -> set:
        return self.apply('declared',  self.stmts)

    def all(self):
        return self.stmts

    def __len__(self):
        return len(self.stmts)

    def __repr__(self):
        s = ", ".join(repr(stm) for stm in self.stmts)
        if self.name is not None:
            return f'Block({s}, name={self.name!r})'
        return f'Block({s})'


# -----------------------------------------------------------
# AstNode -> AstProcStatement -> If
# -----------------------------------------------------------
class If(AstProcStatement):

    class ElseClass:
        def __init__(self, parent):
            super().__init__()
            self.parent = parent

        def doElse(self, stmts):
            self.parent.falseBlock = flattenBlock(stmts)
            return self.parent

        def __getitem__(self, stmts):
            return self.doElse(helper.tupleize(stmts))

        def __call__(self, *stmts):
            return self.doElse(stmts)

    class ElifClass:
        def __init__(self, parent):
            super().__init__()
            self.parent = parent

        def doElif(self, stmts):
            self.parent.elifBlock.append(flattenBlock(stmts))
            return self.parent

        def __getitem__(self, stmts):
            return self.doElif(helper.tupleize(stmts))

        def __call__(self, cond):
            self.parent.elifCond.append(WrapExpr(cond))
            return self

    def __init__(self, cond=1):
        super().__init__()
        self.cond = WrapExpr(cond)
        self.trueBlock = Block()
        self.falseBlock = Block()
        self.elifBlock = []
        self.elifCond = []
        self.Else = self.ElseClass(parent=self)
        self.Elif = self.ElifClass(parent=self)

    def doThen(self, stmts):
        self.trueBlock = flattenBlock(stmts)
        return self

    def __getitem__(self, stmts):
        return self.doThen(helper.tupleize(stmts))

    def Then(self, *trueBlock):
        return self.doThen(trueBlock)

    def assigned(self) -> set:
        return self.apply('assigned', self.all())

    def used(self) -> set:
        return self.apply('used', self.all())

    def paramUsed(self) -> set:
        return self.apply('paramUsed', self.all())

    def typesUsed(self) -> set:
        return self.apply('typesUsed', self.all())

    def all(self) -> list:
        return self.elifCond + self.elifBlock + \
               [self.cond, self.trueBlock, self.falseBlock]

    def asList(self) -> list:
        return [x for x in self.elifBlock] + \
            self.trueBlock.asList() + self.falseBlock.asList()

    def __repr__(self):
        elifv = elsev = ''
        for i, b in enumerate(self.elifBlock):
            elifv = f'.Elif({self.elifCond[i]!r})[{b!r}]'
        if self.falseBlock.asList():
            elsev = f'.Else({self.falseBlock!r})'
        return f'If({self.cond!r}).Then({self.trueBlock!r})' + elifv + elsev


# -----------------------------------------------------------
# AstNode -> AstProcStatement -> While
# -----------------------------------------------------------
class While(AstProcStatement):
    def __init__(self, cond=1):
        super().__init__()
        self.cond = WrapExpr(cond)
        self.trueBlock = Block()

    def doDo(self, stmts: tuple):
        self.trueBlock = flattenBlock(stmts)
        return self

    def __getitem__(self, stmts):
        return self.doDo(helper.tupleize(stmts))

    def Do(self, *trueBlock):
        return self.doDo(trueBlock)

    def asList(self) -> list:
        return self.trueBlock.asList()

    def assigned(self) -> set:
        return self.apply('assigned', self.all())

    def used(self) -> set:
        return self.apply('used', self.all())

    def paramUsed(self) -> set:
        return self.apply('paramUsed', self.all())

    def typesUsed(self) -> set:
        return self.apply('typesUsed', self.all())

    def all(self) -> list:
        return [self.cond, self.trueBlock]

    def __repr__(self):
        return f'While({self.cond!r}).Do({self.trueBlock!r})'


# -----------------------------------------------------------
# AstNode -> AstProcStatement -> Do/While
# -----------------------------------------------------------
class Do(AstProcStatement):

    class WhileClass:
        def __init__(self, parent):
            super().__init__()
            self.parent = parent

        def __call__(self, cond):
            self.parent.cond = WrapExpr(cond)
            return self.parent

    def __init__(self):
        super().__init__()
        self.body = Block()
        self.cond = WrapExpr(1)
        self.While = self.WhileClass(parent=self)

    def doLoop(self, stmts):
        self.body = flattenBlock(stmts)
        return self

    def __getitem__(self, stmts):
        return self.doLoop(helper.tupleize(stmts))

    def Loop(self, *body):
        return self.doLoop(body)

    def assigned(self) -> set:
        return self.apply('assigned', self.all())

    def used(self) -> set:
        return self.apply('used', self.all())

    def paramUsed(self) -> set:
        return self.apply('paramUsed', self.all())

    def typesUsed(self) -> set:
        return self.apply('typesUsed', self.all())

    def all(self) -> list:
        return [self.cond, self.body]

    def asList(self) -> list:
        return self.body.asList()

    def __repr__(self):
        return f'Do().Loop({self.body!r}).While({self.cond!r})'


# -----------------------------------------------------------
# AstNode -> AstProcStatement -> Switch
# -----------------------------------------------------------
class Switch(AstProcStatement):

    class CaseClass(AstProcStatement):
        def __init__(self, parent, *args):
            super().__init__()
            self.parent = parent
            self.conditionExpr = list(WrapExpr(i)
                                      for i in helper.tupleize(*args))
            self.body = Block()

        def doCase(self, stmts: tuple):
            self.body = flattenBlock(stmts)
            return self.parent

        def __getitem__(self, stmts):
            return self.doCase(helper.tupleize(stmts))

        def Do(self, *stmts):
            return self.doCase(stmts)

        def assigned(self):
            return self.apply('assigned', self.all())

        def used(self):
            return self.apply('used', self.all())

        def paramUsed(self):
            return self.apply('paramUsed', self.all())

        def typesUsed(self):
            return self.apply('typesUsed', self.all())

        def all(self):
            return [self.body] + self.conditionExpr

        def __repr__(self):
            return f"Case({self.conditionExpr!r}).Do({self.body!r})"

    def __init__(self, cond=1):
        super().__init__()
        self.cond = WrapExpr(cond)
        self.cases = list()
        self.default = Block()

    def Case(self, *conds):
        self.cases.append(self.CaseClass(self, conds))
        return self.cases[-1]

    def Default(self, *stmts):
        self.default = flattenBlock(stmts)
        return self

    def assigned(self) -> set:
        return self.apply('assigned', self.all())

    def used(self) -> set:
        return self.apply('used', self.all())

    def paramUsed(self) -> set:
        return self.apply('paramUsed', self.all())

    def typesUsed(self) -> set:
        return self.apply('typesUsed', self.all())

    def all(self) -> list:
        return [self.cond] + self.cases + [self.default]

    def asList(self) -> list:
        lst = [self.default]
        for b in self.cases:
            lst += b.asList()
        return lst

    def __repr__(self):
        cases = "".join([f".{i!r}" for i in self.cases])
        return f"Switch({self.cond!r}){cases}.Default({self.default!r})"


# -----------------------------------------------------------
# AstNode -> AstProcStatement -> AssignBase
# -----------------------------------------------------------
# Handle signal and Var assignements
class AssignBase(AstProcStatement):
    def __init__(self, lhs, expr, kind='', oper='='):
        super().__init__()
        self.lhs = lhs
        self.expr = WrapExpr(expr)
        self.oper = oper
        self.kind = kind

    def assigned(self) -> set:
        return self.lhs.lvalue()

    def used(self) -> set:
        return self.expr.used()

    def paramUsed(self) -> set:
        return self.apply('paramUsed', self.all())

    def typesUsed(self) -> set:
        return self.apply('typesUsed', self.all())

    def all(self):
        return [self.lhs, self.expr]

    def __repr__(self):
        return f'{self.kind}Assign({self.lhs!r}, {self.expr!r})'


# AstNode -> AstProcStatement -> AssignBase -> VarAssign
class VarAssign(AssignBase):
    def __init__(self, lhs, expr):
        super().__init__(lhs, expr, 'Var', '=')


# AstNode -> AstProcStatement -> AssignBase -> SigAssign
class SigAssign(AssignBase, AstStatement):
    def __init__(self, lhs, expr):
        AssignBase.__init__(self, lhs, expr, 'Sig', '<=')


# -----------------------------------------------------------
# AstNode -> Module
# -----------------------------------------------------------
class Module(AstNode, gencore.ModuleBase, varname.Named):
    def __init__(self, *IOs, name=None, types=[], params=[]):
        varname.Named.__init__(self, name)
        gencore.ModuleBase.__init__(self, IOs)
        super().__init__()
        self.params = list(params)
        self.body = []
        self.types = list(types)

    def __call__(self, paramMap=None, **kwargs):
        if paramMap is None:
            paramMap = ParamMap()
        return Instance(self, paramMap, PortMap(**kwargs),
                        insName=self.name+str(serialNumber()))

    def vlog(self, indLvl=0, recursive=False):
        import vlog
        res = ''
        for _, modStr in vlog.dump(self, indLvl=indLvl,
                                   recursive=recursive):
            res += modStr + '\n'
        return res

    def vlogIter(self, indLvl=0):
        import vlog
        for modName, modStr in vlog.dump(self, indLvl=indLvl, recursive=True):
            yield modName, modStr

    def vlogToFiles(self, pattern="{}.v", filelist='file_list.f'):
        fileLst = []
        with open(filelist, "wt") as f:
            for modName, modStr in self.vlogIter():
                fname = pattern.format(modName)
                if modStr:  # None is returned for external modules
                    with open(fname, "wt") as fv:
                        fv.write(modStr)
                f.write(fname+'\n')
                fileLst.append(fname)
            return fileLst

    def getName(self):
        return self.name

    def getAst(self):
        return self

    @staticmethod
    def check(x):
        if (not isinstance(x, AstStatement) and
           not hasattr(x, 'expand') and not isinstance(x, Comm)):
            raise TypeError(helper.error(
                'Expecting an statement in a Module', x))
        return x

    def __iadd__(self, x):
        if isinstance(x, tuple):
            for xi in x:
                self.body.append(Module.check(xi))
        elif isinstance(x, Block) and x.name is None:
            for xi in x.asList():
                self.body.append(Module.check(xi))
        else:
            self.body.append(Module.check(x))
        return self

    def Ios(self, *ios):
        self.IOs += ios
        return self

    def __setattr__(self, key, val):
        if key == 'IOs':
            if not isinstance(val, iolist.IoList):
                object.__setattr__(self, key, iolist.IoList(val))
                return
        object.__setattr__(self, key, val)

    def Params(self, *params):
        self.params += params
        return self

    def Types(self, *types):
        self.types += types
        return self

    def __getitem__(self, stmts):
        return self.Body(*helper.tupleize(stmts))

    def Body(self, *stmts):
        for x in stmts:
            self += x  # invoke __iadd__
        return self

    def assigned(self, typ=None):
        typ = typ or (Signal, Var)
        return {x for stm in self.body for x in stm.assigned()
                if isinstance(x, typ)}

    def used(self, typ=None):
        typ = typ or (Signal, Var)
        return {x for stm in self.body for x in stm.used()
                if isinstance(x, typ)}

    def driven(self):
        return {x for stm in self.body for x in stm.driven()}

    def declared(self, typ=None):
        typ = typ or (Signal, Var)
        return {x for stm in self.body for x in stm.declared()
                if isinstance(x, typ)}

    def paramUsed(self):
        return helper.setUnion(
                {x for stm in self.body for x in stm.paramUsed()},
                {x for io in self.IOs for x in io.paramUsed()})

    def typesUsed(self):
        return helper.setUnion(
                {x for stm in self.body for x in stm.typesUsed()},
                {x for io in self.IOs for x in io.typesUsed()})

    def getInstances(self):
        return [stm for stm in self.body if isinstance(stm, InstanceBase)]

    def _autoOutputs(self):  # = {drivenSig} - {usedSig} - {declared}
        usedSig = {s for s in self.used(Signal) if not isinstance(s, Out)}
        declared = self.declared()
        drivenSig = self.assigned(Signal).union(self.driven())
        return (drivenSig.difference(usedSig)).difference(declared)

    def _autoInputs(self):  # = {usedSig} - {assignedOrDriven} - {declared}
        usedSig = self.used(Signal)
        declared = self.declared()
        assignedOrDriven = self.assigned(Signal).union(self.driven())
        return (usedSig.difference(assignedOrDriven)).difference(declared)

    def autoSignals(self):  # = ({usedSig} ^ {assignedOrDriven}) - {declared}
        usedSig = self.used(Signal)
        declared = self.declared()
        assignedOrDriven = self.assigned(Signal).union(self.driven())
        autoSignalSet = (usedSig.intersection(assignedOrDriven)).difference(
                        declared)
        self.body = sortedAsList(Declare(s) for s in autoSignalSet) + self.body
        return self

    def autoIOs(self):  # declared ones are kept in same order
        ios = self.IOs.asList() if isinstance(self.IOs, iolist.IoList) \
              else self.IOs
        initIoSet = set(ios)
        extraIns = {inCopy(x) for x in self._autoInputs()}
        extraOuts = {outCopy(x) for x in self._autoOutputs()}
        ios += sortedAsList(extraIns - initIoSet) + \
            sortedAsList(extraOuts - initIoSet)
        self.IOs = iolist.IoList(*ios)
        return self

    def autoParams(self):  # declared ones are kept in same order
        allParamSet = set(self.params).union(self.paramUsed())
        self.params += sortedAsList(allParamSet - set(self.params))
        return self

    def autoTypes(self):  # declared ones are kept in same order
        allTypeSet = set(self.types).union(self.typesUsed())
        self.types += sortedAsList(allTypeSet - set(self.types))
        return self

    def autoInstanceName(self):
        instances = self.getInstances()
        seenIns = set(instances)
        unnamedIns = (i for i in instances if i.insName is None)
        nextIdx = defaultdict(lambda: 0)
        for ins in unnamedIns:
            i = nextIdx[ins.modName()]
            while ins.modName() + f"_{i}" in seenIns:
                i += 1
            ins.insName = ins.modName() + f"_{i}"
            seenIns.add(ins.insName)
            nextIdx[ins.modName()] = i+1
        return self

    def findIOByType(self, typ):
        return [io for io in self.IOs if isinstance(io, typ)]

    def autoConnClockReset(self):
        cntClockedWithoutClk = 0
        moduleClock = self.findIOByType(Clock)
        moduleClock = moduleClock[0] if len(moduleClock) == 1 else None

        cntClockedWithoutRst = 0
        moduleReset = self.findIOByType(Reset)
        moduleReset = moduleReset[0] if len(moduleReset) == 1 else None

        for stm in self.body:

            # if the statement is expected to have a clock
            if hasattr(stm, 'clock'):
                # but none was given
                if stm.clock is None:
                    # get this module clock (only one expected implicit clock)
                    cntClockedWithoutClk += 1
                    if moduleClock is not None:
                        stm.clock = moduleClock
                    else:
                        raise ValueError(helper.error(
                            'Could not derived a clock from top for', stm))

            if hasattr(stm, 'reset'):
                # if the statement is expected to have a reset but doesn't
                if stm.reset is None and (not hasattr(stm, 'autoReset') or
                                          stm.autoReset):
                    cntClockedWithoutRst += 1
                    if moduleReset is not None:
                        stm.reset = moduleReset
                    else:
                        raise ValueError(helper.error(
                            'Could not derive a reset from top for', stm))
        return self

    def autoExpand(self):  # TODO make sure body can accept tuples
        newBody = []
        for stm in self.body:
            if hasattr(stm, 'expand') and (
                    not hasattr(stm, 'autoExpand') or stm.autoExpand):
                exp = stm.expand()
                if isinstance(exp, tuple):
                    newBody += list(exp)
                else:
                    newBody.append(exp)
            else:
                newBody.append(stm)
        self.body = newBody
        return self

    def autoReset(self):
        for stm in self.body:
            if isinstance(stm, Clocked):
                stm.addResetLogic()
        return self

    def autoGen(self):
        return self.autoConnClockReset() \
                   .autoExpand() \
                   .autoReset() \
                   .autoIOs() \
                   .autoSignals() \
                   .autoParams() \
                   .autoTypes() \
                   .autoInstanceName()

    def elab(self):
        _ = repr(self)  # resolves all names TODO
        return self.autoReset()

    def __repr__(self):
        typeStr = f"types={self.types!r}, " if self.types else ""
        return f'Module({self.name!r}, {typeStr}IOs={self.IOs!r}, ' + \
               f'params={self.params!r}, body={self.body!r})'


# ------------------------------------------------------------------------
# Type related
# ------------------------------------------------------------------------
class EnuCoding(Enum):
    autoIncr = 0
    oneHot = 1
    oneCold = 2


# ------------------------------------------------------------------------
# AstNode -> Type
# ------------------------------------------------------------------------
class Type(AstNode, varname.Named):
    def __init__(self, name):
        AstNode.__init__(self)
        varname.Named.__init__(self, name)
        self.signed = False

    def typesUsed(self) -> set:
        if isinstance(self, BitVec):
            return set()
        return set([self])

    def paramUsed(self) -> set:
        return helper.setUnion(*[x.paramUsed() for x in self.all()])

    def all(self) -> list:
        return []


# ------------------------------------------------------------------------
# AstNode -> Type -> Array
# ------------------------------------------------------------------------
class Array(Type):
    def __init__(self, itemType, *dims, name=None):
        super().__init__(name)
        self.itemType = itemType
        self.dims = dims
        self.width = reduce(lambda x, y: x*y, dims)*itemType.width

    def _itemtype(self): return self.itemType

    def _offset(self, idx):
        assert len(idx) == len(self.dims)
        dims = list(reversed(self.dims))  # store lower ranking on index 0
        offs = 0
        sizeLowerDims = 1
        for pos, i in enumerate(reversed(idx)):
            offs += i * sizeLowerDims
            sizeLowerDims *= dims[pos]
        return offs*self.itemType.width

    def all(self):
        return [self.itemType] + list(i for i in self.dims if not isInt(i))

    def size(self, i):
        return self.dims[i]

    def ndims(self):
        return len(self.dims)

    def __repr__(self):
        suffix = helper.reprStr(["name", self.name, ""])
        return f"Array({self.itemType}, {self.dims}{suffix})"


# ------------------------------------------------------------------------
# AstNode -> Type -> BitVec
# ------------------------------------------------------------------------
class BitVec(Type):
    def __init__(self, width=1, *, name=None, signed: bool = False):
        super().__init__(name)
        self.signed = signed
        self.width = width

    def Signed(self):
        self.signed = True
        return self

    def used(self) -> set:
        return set([self])

    def paramUsed(self) -> set:
        if isinstance(self.width, Expr):
            return self.width.paramUsed()
        return set()

    def __repr__(self):
        suffix = helper.reprStr(["name", self.name, ""],
                                ["signed", self.signed, False])
        return f"BitVec({self.width}{suffix})"


# ------------------------------------------------------------------------
# AstNode -> Type -> Agreg
# ------------------------------------------------------------------------
class Field:
    def __init__(self, typ: Type, *names):
        super().__init__()
        self.typ = typ
        self.names = names

    def __repr__(self):
        inner = helper.listRepr(*self.names)
        return f"Field({self.typ}, {inner})"


class Agreg(Type):
    def __init__(self, *, name=None):
        super().__init__(name)
        self.body = []
        self.fieldDict = {}
        self.fieldList = []

    def __getitem__(self, stmts):
        return self.Body(*helper.tupleize(stmts))

    def Body(self, *stmts):
        for stm in stmts:
            if not isinstance(stm, Field):
                raise TypeError(
                        helper.error(f"Agreg members must be Field's", stm))
            for nm in stm.names:
                if nm in self.fieldDict:
                    raise KeyError(
                            helper.error(f"Repeated field name .{nm}", self))
                if nm in self.__dir__():
                    raise KeyError(helper.error(
                        f"Field name .{nm} is reserved", self))
                self.body.append(Field(stm.typ, nm))
                self.fieldDict[nm] = stm.typ
                self.fieldList.append(nm)
        return self

    @staticmethod
    def sumList(lst):
        return simplify(sum(lst))

    @property
    def width(self):
        return Agreg.sumList(f.typ.width for f in self.body)

    def _offset(self, fieldName: str):
        assert fieldName in self.fieldDict
        priorFields = takewhile(lambda f: f.names[0] != fieldName, self.body)
        return Agreg.sumList(f.typ.width for f in priorFields)

    def fldWidth(self, fieldName: str):
        assert fieldName in self.fieldDict
        return self.fieldDict[fieldName].width

    def __repr__(self):
        inner = helper.listRepr(*self.body)
        return f"{self.kind}(name={self.name!r}) [{inner}]"


class Rec(Agreg):
    kind = 'Rec'


def isMultParam(e):
    return (isinstance(e, BinExpr) and
            e.op == '*' and
            type(e.args[0]) == CInt and
            type(e.args[1]) == Param)


def isParamMult(e):
    return (isinstance(e, BinExpr) and
            e.op == '*' and
            type(e.args[1]) == CInt and
            type(e.args[0]) == Param)


def normalizeTerm(a):
    if type(a) == Param:
        a = BinExpr('*', CInt(1), a)
    if isParamMult(a):
        e = BinExpr('*', a.args[1], a.args[0])
        assert isMultParam(e)
        return e
    return a


def maxExpr(lst):
    lst = list(set(lst))
    if len(lst) == 1:
        return lst[0]
    if len(lst) == 2:
        a, b = lst
        a = normalizeTerm(a)
        b = normalizeTerm(b)
        if isinstance(a, BinExpr) and isinstance(b, BinExpr):
            if (isMultParam(a) and isMultParam(b) and
               repr(a.args[1]) == repr(b.args[1])):
                mx = max(a.args[0].args[0], b.args[0].args[0])
                if mx == 1:
                    return a.args[1]
                return BinExpr('*', mx, a.args[1])
    return IfCond(lst[0] > maxExpr(lst[1:]), lst[0], maxExpr(lst[1:]))


class Union(Agreg):
    kind = 'Union'

    def _offset(self, fieldName: str):
        return 0

    @property
    def width(self):
        fldw = [f.typ.width for f in self.body]
        if all(isInt(x) for x in fldw):
            return max(intVal(w) for w in fldw)
        else:
            return maxExpr(fldw)


class Iface(Agreg):
    kind = 'Iface'


# ------------------------------------------------------------------------
# AstNode -> Type -> Enu
# ------------------------------------------------------------------------
class Enu(Type):
    def __init__(self, *vals, style: EnuCoding = EnuCoding.autoIncr,
                 name=None):
        self.valDict = {}
        super().__init__(name)
        self.style = style
        self.valNames = []
        assert vals
        for x in vals:
            if type(x) is not str and type(x) is not tuple:
                raise TypeError(helper.error(
                    f"Enu values must be strings or (name, value) " +
                    f"tuples, found {x}", self))
            itemName = type(x) is tuple and x[0] or x
            if type(itemName) is not str:
                raise TypeError(helper.error(
                    f"Enu names must be strings, found {itemName}", self))
            self.valNames.append(itemName)
        if style == EnuCoding.autoIncr:
            curr = 0
            for v in vals:
                if isinstance(v, tuple):
                    nm, val = v
                    if val < curr:
                        self.valDict[nm] = val
                        raise ValueError(helper.error(
                            f"Enu values must be increasing but {nm}" +
                            f" got {val}", self))
                else:
                    nm, val = v, curr
                curr = val+1
                self.valDict[nm] = val
        else:
            raise NotImplementedError(helper.error(
                f"EnuCoding style {style} not implemented yet", self))

    def dict(self):
        return self.valDict

    def val(self, symName):
        return self.valDict[symName]

    def first(self):
        return self.valNames[0]

    def last(self):
        return self.valNames[-1]

    def min(self):
        return min(self.valDict.values())

    def max(self):
        return max(self.valDict.values())

    def __getattr__(self, key):
        if key in self.valDict:
            return key
        raise KeyError(helper.error(
            f"Attempted invalid enum value {self.name}.{key}. See definition",
            self))

    @property
    def width(self):
        return self.max().bit_length()

    def __repr__(self):
        valStr = f"{self.valDict}"
        return f"Enu(vals={valStr}, style={self.style}, name={self.name!r})"


# ------------------------------------------------------------------------------
# build a function that given an operator returns its priority
# ------------------------------------------------------------------------------
def opPri():
    def fillUpPri(priDict):
        pri = {}
        for ops, priority in priDict.items():
            for op in ops:
                pri[op] = priority
        return pri

    priMon = fillUpPri({
        ('.',): 100,
        ('~', '&', '|', '^', '~^', '^~', '~&', '~|'): 90,
        ('+', '-'): 80
    })

    priBin = fillUpPri({
        ('.'): 99,
        ('[',): 95,
        ('*', '/'): 20,
        ('+', '-'): 19,
        ('<<', '>>'): 18,
        ('>', '<', '>='): 17,
        ('==', '!='): 16,
        ('&',): 15,
        ('^',): 14,
        ('|',): 13,  # not intuitive
        ('&&',): 12,
        ('||',): 11
    })

    priTer = fillUpPri({
        ('?',): 0,
        ('{',): 5,
        ('[',): 95
    })

    # the function returned, closure on the 3 arrays above
    def getPri(op, numOps):
        return priMon[op] if numOps == 1 else \
               priBin[op] if numOps == 2 else priTer[op]

    return getPri


getPri = opPri()


# ------------------------------------------------------------------------------
# Generate a expresion wrapper out of some constants
# ------------------------------------------------------------------------------
def WrapExpr(x):
    if x is None or isinstance(x, (Expr, Type)):
        return x
    if isinstance(x, int):
        return CInt(x)
    if isinstance(x, str):
        return CEnu(x)
    if isinstance(x, list):
        return Concat(*x)
    if isinstance(x, tuple):
        return x  # for Array
    raise TypeError(helper.error(
        f"Don't know how to covert to an expression", x))


# ------------------------------------------------------------------------------
# AstNode -> Expr
# ------------------------------------------------------------------------------
class Expr(AstNode):
    def __init__(self, op, *args, numOps=0):
        super().__init__()
        self.op = op
        self.pri = getPri(op, len(args) if numOps == 0 else numOps)
        self.const = False
        self.args = [WrapExpr(arg) for arg in args]

    def __ilshift__(self, n):
        raise NotImplementedError(helper.error("", self))

    def __add__(self, rhs):
        return BinExpr('+', self, rhs)

    def __sub__(self, rhs):
        return BinExpr('-', self, rhs)

    def __mul__(self, rhs):
        return BinExpr('*', self, rhs)

    def __and__(self, rhs):
        return BinExpr('&', self, rhs)

    def __or__(self, rhs):
        return BinExpr('|', self, rhs)

    def __xor__(self, rhs):
        return BinExpr('^', self, rhs)

    def __lshift__(self, rhs):
        return BinExpr('<<', self, rhs)

    def __rshift__(self, rhs):
        return BinExpr('>>', self, rhs)

    def __radd__(self, lhs):
        return BinExpr('+', lhs, self)

    def __rsub__(self, lhs):
        return BinExpr('-', lhs, self)

    def __rmul__(self, lhs):
        return BinExpr('*', lhs, self)

    def __rand__(self, lhs):
        return BinExpr('&', lhs, self)

    def __ror__(self, lhs):
        return BinExpr('|', lhs, self)

    def __rxor__(self, lhs):
        return BinExpr('^', lhs, self)

    def __rlshift(self, lhs):
        return BinExpr('<<', lhs, self)

    def __rrshift__(self, lhs):
        return BinExpr('>>', lhs, self)

    def __lt__(self, rhs):
        return BinExpr('<', self, rhs)

    def __gt__(self, rhs):
        return BinExpr('>', self, rhs)

    # def __ge__(self, rhs):
    #     return BinExpr('>=', self, rhs)  # FIXME

    def __eq__(self, rhs):
        return BinExpr('==', self, rhs)

    def __ne__(self, rhs):
        return BinExpr('!=', self, rhs)

    def __neg__(self):
        return UnaryExpr('-', self)

    def __invert__(self):
        return UnaryExpr('~', self)

    def __getitem__(self, slc):
        typ = self._type()
        if isinstance(typ, BitVec):
            return BitExtract(self, slc)
        elif isinstance(typ, Array):
            return ItemExtract(self, slc)
        else:
            raise TypeError(helper.error(
                f"{self.name} is not indexable type", self))

    def simplify(self):
        return self

    def Eval(self):
        raise TypeError(helper.error(f"Cannot be Eval", self))

    def applyFunc(self, f) -> None:
        f(self)
        for s in self.all():
            s.applyFunc(f)

    def all(self) -> list:
        return self.args

    def lvalue(self):
        raise TypeError(helper.error(f"Not an lvalue", self))

    def used(self) -> set:
        return self.apply('used', self.all())

    def paramUsed(self) -> set:
        return self.apply('paramUsed', self.all())

    def typesUsed(self) -> set:
        return self.apply('typesUsed', self.all())

    def argsStr(self):
        return helper.listRepr(*self.args)

    def __repr__(self):
        return f"{self.op}({self.argsStr()})"

    def __hash__(self):
        return self.__repr__().__hash__()


# ------------------------------------------------------------------------
# AstNode -> Expr -> UnaryExpr
# ------------------------------------------------------------------------
class UnaryExpr(Expr):
    def __init__(self, op, rhs):
        super().__init__(op, rhs)

    def Eval(self):
        r = self.args[0].Eval()
        return eval(f"{self.op} {r}")

    def applyFunc(self, f):
        f(self)

    # https://stackoverflow.com/questions/53518981/
    # inheritance-hash-sets-to-none-in-a-subclass
    __hash__ = Expr.__hash__


class CInt(UnaryExpr):
    def __init__(self, val, width=None, signed=False):
        # super().__init__('.', val)
        self.op = '.'
        self.pri = getPri(self.op, numOps=1)
        self.const = False
        self.args = [val]
        self.width = width
        self.signed = signed
        self.base = 'b' if width == 1 else 'd'

    def used(self) -> set:
        return set()

    def paramUsed(self) -> set:
        return set()

    def typesUsed(self) -> set:
        return set()

    def Eval(self):
        return self.args[0]

    def Dec(self):
        self.base = 'd'
        return self

    def Hex(self):
        self.base = 'h'
        return self

    def Bin(self):
        self.base = 'b'
        return self

    def Signed(self):
        self.signed = True
        return self

    def __repr__(self):
        suf = '.Hex()' if self.base == 'h' else \
              '.Bin()' if self.base == 'b' else ''
        if self.signed:
            return f'CInt({self.args[0]!r}, width={self.width}, ' + \
                   f'signed={self.signed}){suf}'
        if self.width is not None:
            return f'CInt({self.args[0]!r}, width={self.width}){suf}'
        return f'CInt({self.args[0]!r}){suf}'


class CEnu(UnaryExpr):
    def __init__(self, val, width=None, signed=False):
        # super().__init__()
        self.op = '.'
        self.pri = getPri(self.op, numOps=1)
        self.const = False
        self.args = [val]
        self.width = width
        self.signed = signed
        self.base = 'b' if width == 1 else 'd'

    def used(self) -> set:
        return set()

    def paramUsed(self) -> set:
        return set()

    def typesUsed(self) -> set:
        return set()

    def Eval(self):
        return self.args[0]

    def __repr__(self):
        if self.signed:
            return f'CEnu({self.args[0]!r}, width={self.width}, ' + \
                   f'signed={self.signed})'
        if self.width is not None:
            return f'CEnu({self.args[0]!r}, width={self.width})'
        return f'CEnu({self.args[0]!r})'


class Param(UnaryExpr, varname.Named):
    def __init__(self, val, name=None):
        super().__init__('.', val)
        varname.Named.__init__(self, name)
        self.const = True

    def Eval(self):
        return self.args[0].Eval()

    def used(self):
        return set()

    def paramUsed(self):
        return set([self])

    def __hash__(self):
        return self.name.__hash__()

    def __repr__(self):
        return f"Param({self.argsStr()}, name={self.name!r})"


# ------------------------------------------------------------------------
# AstNode -> Expr -> UnaryExpr -> Assignable
# ------------------------------------------------------------------------
class Assignable(UnaryExpr, varname.Named):
    kind = 'Assignable'

    def __init__(self, typ=None, name=None, default=0):
        varname.Named.__init__(self, name)
        if isinstance(typ, Assignable):  # from other signal/var
            typ = typ._type()
        elif isinstance(typ, (Expr, int)):
            typ = BitVec(typ)  # typ is a width here
        elif typ is None:
            typ = BitVec(1)
        else:
            if not isinstance(typ, Type):
                raise TypeError(helper.error(
                    'Expecting first argument to be a Signal/Var, an ' +
                    'expression (width), None for width=1 or a user defined ' +
                    f'type however found {typ}', self))
        UnaryExpr.__init__(self, '.', typ)
        self.default = default

    def _type(self):
        return self.args[0]

    @property
    def width(self):
        return self._type().width

    def Signed(self):
        if isinstance(self._type(), BitVec):
            self._type().Signed()
            return self
        raise TypeError(helper.error(
            "Cannot set signed on non-BitVec type", self))

    def __getattr__(self, key):
        if key.startswith("_"):
            return self.__getattribute__(key)
        typ = self._type()
        if not isinstance(typ, Agreg):
            raise TypeError(helper.error(
                f"{self.name} of type {typ} is not aggregate type and " +
                f". expression was attempted on it", self))
        if key in typ.fieldDict:
            return DotExpr(self, key)
        raise KeyError(helper.error(
            f"invalid Rec/Union/Iface field {self.name}.{key}", self))

    def used(self) -> set:
        return set([self])

    def lvalue(self) -> set:
        return set([self])

    def __pow__(self, n):
        return Times(n, self)

    def __repr__(self):
        suffix = helper.reprStr(["default", self.default, 0])
        return f"{self.kind}(typ={self._type()!r}, name={self.name!r}{suffix})"


# ------------------------------------------------------------------------
# AstNode -> Expr -> UnaryExpr -> Assignable -> Signal
# ------------------------------------------------------------------------
class Signal(Assignable):
    kind = 'Signal'

    def __le__(self, rhs):
        return SigAssign(self, rhs)

    def update(self, rhs):
        return SigAssign(self, rhs)

    def __hash__(self):
        return self.name.__hash__()


class Port(Signal):
    kind = 'Port'


class Out(Port, gencore.OutputBase):
    kind = 'Out'
    isReg = False


class In(Port, gencore.InputBase):
    kind = 'In'


class Clock(In):
    def __init__(self, *, name=None, posedge=True):
        super().__init__(BitVec(1), name=name)
        self.posedge = posedge

    def __repr__(self):
        suffix = helper.reprStr(["posedge", self.posedge, True])
        return f"Clock(name={self.name!r}{suffix})"


class Reset(In):
    def __init__(self, *, name=None, asyn=True, lowTrue=True):
        super().__init__(BitVec(1), name=name)
        self.asyn = asyn
        self.lowTrue = lowTrue

    def onExpr(self):
        return ~self if self.lowTrue else self

    def offExpr(self):
        return self if self.lowTrue else ~self

    def __repr__(self):
        suffix = helper.reprStr(["asyn", self.asyn, True],
                                ["lowTrue", self.lowTrue, True])
        return f"Reset(name={self.name!r}{suffix})"


# ------------------------------------------------------------------------
# AstNode -> Expr -> UnaryExpr -> Assignable -> Var
# ------------------------------------------------------------------------
class Var(Assignable):
    kind = 'Var'

    def eq(self, rhs):
        return VarAssign(self, rhs)

    def __ne__(self, rhs):  # x != x + 1
        if isinstance(self, Var):
            return VarAssign(self, rhs)
        return Expr('!=', self, rhs)

    def __matmul__(self, n):  # x @ x + 1
        return VarAssign(self, n)

    # TODO, add support for var.a = var.x + 1


# ------------------------------------------------------------------------
# AstNode -> Expr -> BinExpr
# ------------------------------------------------------------------------
def isInt(obj) -> bool:
    return isinstance(obj, (CInt, int))


def intVal(obj):
    if isinstance(obj, (tuple, list)):
        return tuple(intVal(k) for k in obj)
    if isinstance(obj, CInt):
        return obj.args[0]
    if isinstance(obj, int):
        return obj
    assert False, f"Not clear how to get intVal of {obj}"


class BinExpr(Expr):
    def __init__(self, op, lhs, rhs):
        super().__init__(op, lhs, rhs)

    def Eval(self):
        left = self.args[0].Eval()
        right = self.args[1].Eval()
        return eval(f"{left} {self.op} {right}")

    def simplify(self):
        from simplify import simplifyBinExpr
        return simplifyBinExpr(self)

    def __repr__(self):
        return f"({self.args[0]!r} {self.op} {self.args[1]!r})"


class DotExpr(BinExpr):
    def __init__(self, parent, key, root=None):
        super().__init__('.', None, None)
        self.op = '.'
        self.pri = getPri(self.op, numOps=2)
        self.const = False
        root = root or parent
        assert isinstance(parent._type(), Agreg)
        fldtyp = parent._type().fieldDict[key]
        self.args = [fldtyp, parent, key]
        self.root = root

    def used(self):
        return set([self.root])

    def paramUsed(self):
        return set()

    def typesUsed(self):
        return set()

    def _type(self):
        return self.args[0]  # type of the selected key

    def _parent(self):
        return self.args[1]  # whole parent expression

    def _key(self):
        return self.args[2]  # selected key

    def __le__(self, rhs):
        return SigAssign(self, rhs)

    @property
    def width(self):
        return self._type().width

    def __getattr__(self, key):
        _ = self.args[0]  # parent
        typ = self._type()
        if not isinstance(typ, Agreg):
            raise TypeError(helper.error(
                f"{typ.name} is not aggregate type and . expression attempted",
                self))
        if key in typ.fieldDict:
            return DotExpr(self, key, self.root)
        raise KeyError(helper.error(
                f"invalid Rec/Union/Iface field {self.name}.{key}", self))

    def lvalue(self):
        return self._parent().lvalue()

    def Eval(self):
        return self.args[0]

    def __hash__(self):
        return self.name.__hash__()

    def __repr__(self):
        suffix = helper.reprStr(["root", self.root, None])
        return \
            f'DotExpr(parent={self.args[1]!r}, key={self.args[2]!r}{suffix})'


# ------------------------------------------------------------------------
# AstNode -> Expr -> MultiExpr
# ------------------------------------------------------------------------
class MultiExpr(Expr):
    def __init__(self, op, *args, numOps=0):
        super().__init__(op, *args, numOps=numOps)


class BitExtract(MultiExpr):
    def __init__(self, parent, msb, lsb=None):
        if isinstance(msb, slice):  # e.g. x[3:2]
            if msb.step is not None:
                raise ValueError(helper.error(
                    f"invalid bit selection {msb.step}", self))
            assert lsb is None
            msb, lsb = msb.start, msb.stop
        super().__init__('[', parent, msb, lsb)  # BitExtract(x,3,2) also vld

    def _parent(self):
        return self.args[0]

    def _msb(self):
        return self.args[1]

    def _lsb(self):
        return self.args[2] or self._msb()

    @property
    def width(self):
        return self._msb() + 1 - self._lsb()

    def __le__(self, rhs):
        return SigAssign(self, rhs)

    def lvalue(self):
        return set([self.args[0]])

    __hash__ = Expr.__hash__

    def __repr__(self):
        return f"BitExtract({self.argsStr()})"


class ItemExtract(MultiExpr):
    def __init__(self, parent, idx):
        assert isinstance(parent._type(), Array)
        idx = helper.tupleize(idx)
        super().__init__('[', parent, *idx)  # E.g. BitExtract(x,(1,2,3))

    def _parent(self):
        return self.args[0]

    def _idx(self):
        return self.args[1:]

    def _type(self):
        return self._parent()._type()._itemtype()

    def _itemtype(self):
        return self._parent()._type()._itemtype()

    @property
    def width(self):
        return self._itemtype().width

    def __le__(self, rhs):
        return SigAssign(self, rhs)

    def lvalue(self):
        return self._parent().lvalue()

    __hash__ = Expr.__hash__

    # def all(self):
    #    return self.args + [self._parent()]

    def __repr__(self):
        return f"ItemExtract({self.argsStr()})"


class Concat(MultiExpr):
    def __init__(self, *args):
        super().__init__('{', *args, numOps=3)
        self.pri = getPri(self.op, numOps=3)

    def __le__(self, rhs):
        return SigAssign(self, rhs)

    def lvalue(self):
        return helper.setUnion(*[x.lvalue() for x in self.all()])

    def __repr__(self):
        return f"Concat({self.argsStr()})"


class IfCond(MultiExpr):
    def __init__(self, cond, ift, iff):
        super().__init__('?', cond, ift, iff)

    def __repr__(self):
        return f"IfCond({self.argsStr()})"


class ExprReduce(MultiExpr):
    def __init__(self, op, rhs):
        assert op in ('&', '|', '^', '~^', '^~', '~&', '~|')
        super().__init__(op, rhs)

    def __repr__(self):
        return f"ExprReduce({self.op!r}, {self.argsStr()})"


class OrReduce(ExprReduce):
    def __init__(self, rhs):
        super().__init__('|', rhs)


class AndReduce(ExprReduce):
    def __init__(self, rhs):
        super().__init__('&', rhs)


class XorReduce(ExprReduce):
    def __init__(self, rhs):
        super().__init__('^', rhs)


# ------------------------------------------------------------------------------
# More convenience functions
# ------------------------------------------------------------------------------
def outCopy(x):
    return Out(typ=x.args[0], name=x.name, default=x.default)


def inCopy(x):
    return In(typ=x.args[0], name=x.name, default=x.default)


def appendStms(body, stmts):
    for stm in stmts:
        body += stm


# For backwards compatibility
Input = In
Output = Out
Parameter = Param
Comment = Comm
Variable = Var
