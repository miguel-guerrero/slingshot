#------------------------------------------------------------------------------
# Copyright (c) 2018-Present, Miguel A. Guerrero
# All rights reserved.
#
# This is free software released under GNU Lesser GPL license version 3.0 (LGPL 3.0)
#
# See http://www.gnu.org/licenses/lgpl-3.0.txt for a full text
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE 
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED 
# OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Please send bugs and suggestions to: miguel.a.guerrero@gmail.com
#-------------------------------------------------------------------------------

from enum import Enum
import re
import copy
from collections import defaultdict
from itertools import takewhile

import gencore
from varname import makeCounter, Named
from helper import reprStr, listRepr, modkey, tupleize, Struct

try:
    #https://github.com/RussBaz/enforce
    from enforce import runtime_validation, config
    config({'mode':'covariant'})
except:
    import sys
    print('please run: pip3 install enforce', file=sys.stderr)
    runtime_validation = lambda x : x

serialNumber = makeCounter()

#------------------------------------------------------------------------------
# Utilities
#------------------------------------------------------------------------------
def simplify(e):
    if isinstance(e, Expr):
        return e.simplify()
    return e

def sortedAsList(s):
    return sorted(s, key=lambda x : modkey(x.name))


#if passed a tuple of statements creates a block with them,
#but if passed a tuple containing only a block just returns it
@runtime_validation
def flattenBlock(aTuple: tuple):
    if len(aTuple)==1 and isinstance(aTuple[0], Block):
        return aTuple[0]
    return Block(*aTuple)


# Short-cut to generate n copies of an object. e.g Input() ** 2
def Times(n, obj):
    return [obj] + [copy.copy(obj) for i in range(1, n)]


#------------------------------------------------------------------------------
# For hybrid g2p / chipo implementations
#------------------------------------------------------------------------------
class ApiGenerator(gencore.GeneratorBase):
    def __init__(self, module, targetDir, targetExt):
         super().__init__(targetDir, targetExt)
         self.module = module

    def runGeneration(self, name, passedParamDict):
        import vlog
        assert self.module.name == name
        s = vlog.dump(self.module.getAst())
        return s, self.module


def vlogToFile(exportMod, targetDir='build', targetExt='.v'):
    ag = ApiGenerator(exportMod, targetDir, targetExt)
    return ag.run(exportMod.getName(), exportMod.paramDict)


def generateG2p(modBaseName, passedParamDict, defaultParamDict, genFun):
    from g2p import processParams
    name, paramDict, params = processParams(
        modBaseName, passedParamDict, defaultParamDict)
    mod = genFun(name, params)
    mod.paramDict = paramDict
    return vlogToFile(mod) #returns mod


#------------------------------------------------------------------------------
# AstNode : Parent of all AST nodes
#------------------------------------------------------------------------------
class AstNode:
    def assigned(self):  return set()
    def used(self):      return set()
    def paramUsed(self): return set()
    def typesUsed(self): return set()
    def driven(self):    return set()
    def declared(self):  return set()

    #apply a set-returning method 'm' to non-None items in list and return
    #the union of all returned sets
    def apply(self, m, lst):
        lst = [getattr(x,m)() for x in lst if x is not None and x is not ...]
        if lst:
            return set.union(*lst)
        return set()


    def __repr__(self): raise NotImplementedError


#-----------------------------------------------------------
# AstNode -> Comment
#-----------------------------------------------------------
class Comment(AstNode):
    def __init__(self, *lines):
        self.lines = lines

    def __repr__(self):
        return f'Comment{self.lines!r}'


#------------------------------------------------------------------------------
# AstNode -> AstStatement : things that can show up under a module
#------------------------------------------------------------------------------
class AstStatement(AstNode):
    pass


#-----------------------------------------------------------
# AstNode -> AstStatement -> Clocked
#-----------------------------------------------------------
class Clocked(AstStatement):
    def __init__(self, clock, reset=None, autoReset=True):
        self.clock = clock
        self.reset = reset
        self.autoReset = autoReset
        self.body = Block()

    def __iadd__(self, x):
        self.body += x
        return self

    def __getitem__(self, stmts):
        return self.Body(*tupleize(stmts))

    def Body(self, *stmts):
        appendStms(self.body, stmts)
        return self

    def assigned(self):  return self.body.assigned()
    def paramUsed(self): return self.body.paramUsed()
    def typesUsed(self): return self.body.typesUsed()

    def used(self):
        return self.body.used().union([self.clock, self.reset])

    def Name(self, name):
        self.body.name = name
        return self

    def genResetLogic(self):
        lst = [SigAssign(var, var.default) for var in self.body.assigned()]
        if not lst:
            return self.body
        lst = sorted(lst, key=lambda x : x.lhs.name)
        return Block(If(self.reset.onExpr()).Then(*lst).Else(self.body))

    def addResetLogic(self):
        if self.autoReset and self.reset is not None:
            self.body = self.genResetLogic()
        return self

    def __repr__(self):
        return f'Clocked({self.clock}, reset={self.reset!r}, ' + \
               f'autoReset={self.autoReset}).Body({self.body!r})'


#-----------------------------------------------------------
# AstNode -> AstStatement -> Combo
#-----------------------------------------------------------
class Combo(AstStatement):
    def __init__(self, body=None):
        self.body = Block() if body is None else body

    def __iadd__(self, x):
        self.body += x
        return self

    def __getitem__(self, stmts):
        return self.Body(*tupleize(stmts))

    def Body(self, *stmts):
        appendStms(self.body, stmts)
        return self

    def assigned(self):  return self.body.assigned()
    def used(self):      return self.body.used()
    def paramUsed(self): return self.body.paramUsed()
    def typesUsed(self): return self.body.typesUsed()

    def Name(self, name):
        self.body.name = name
        return self

    def __repr__(self):
        return f'Combo(body={self.body!r})'


#-----------------------------------------------------------
# AstNode -> AstStatement -> Declare
#-----------------------------------------------------------
class Declare(AstStatement):
    def __init__(self, x):
        assert isinstance(x, (Signal, Variable))
        self.x = x

    @property
    def name(self):
        return self.x.name

    def declared(self):
        return set([self.x])

    def __repr__(self):
        return f"Declare({self.x!r})"


#-----------------------------------------------------------
# Instance related
#-----------------------------------------------------------
def _ioToTextDict(ioMapDict, IOs):
    name = lambda io : io.name if isinstance(io, Signal) else io
    d = {name(io): name(io) for io in IOs} # default name mapping
    for io, v in ioMapDict.items(): # override based on input
        if isinstance(io, Signal):
            assert io.name in d, 'signal in port map is not a port: ' + io.name
        if isinstance(io, str):
            assert io in d, 'signal in port map is not a port: ' + io
        d[name(io)] = name(v) if v is not None else ''
    return d

def _ioToVlogDict(ioMapDict, IOs):
    import vlog
    name = lambda io : io.name if isinstance(io, Signal) else io
    d = {name(io): name(io) for io in IOs} # default name mapping
    for io, v in ioMapDict.items(): # override based on input
        if isinstance(io, Signal):
            assert io.name in d, 'signal in port map is not a port: ' + io.name
        if isinstance(io, str):
            assert io in d, 'signal in port map is not a port: ' + io
        d[name(io)] = vlog.dump(v) if v is not None else ''
    return d

def _paramToTextDict(paramMapDict):
    name = lambda p : p.name if isinstance(p, Parameter) else p
    return {name(p) : name(v) for p, v in paramMapDict.items()}


#-----------------------------------------------------------
# AstNode -> AstStatement -> InstanceBase
#-----------------------------------------------------------
class InstanceBase(AstStatement):
    def __init__(self, insName):
        self.insName = insName

    def module(self):
        return None

    #must be overriden
    def used(self):              raise NotImplementedError(f"{self}")
    def modName(self):           raise NotImplementedError(f"{self}")
    def _textParamMapDict(self): raise NotImplementedError(f"{self}")
    def _textIoMapDict(self):    raise NotImplementedError(f"{self}")

    def _insName(self):
        if self.insName is not None:
            return self.insName
        return f"unamed_ins_{serialNumber()}"


#-----------------------------------------------------------
# AstNode -> AstStatement -> InstanceBase -> InstanceLegacy
#-----------------------------------------------------------
# for existing verilog modules
class InstanceLegacy(InstanceBase):
    def __init__(self, moduleName, textParamMapDict, textIoMapDict, insName=None):
        self.moduleName = moduleName
        self.textParamMapDict = textParamMapDict
        self.textIoMapDict = textIoMapDict
        super().__init__(insName)

    def used(self):      return set()
    def paramUsed(self): return set() #TODO
    def typesUsed(self): return set() #TODO

    def modName(self):
        return self.moduleName

    def _textParamMapDict(self):
        return self.textParamMapDict

    def _textIoMapDict(self):
        return self.textIoMapDict

    def __repr__(self):
        args = f", insName={self.insName!r}" if self.insName is not None else ""
        return f"InstanceLegacy({self.moduleName!r}, " + \
               f"textParamMapDict={self.textParamMapDict}, " + \
               f"textIoMapDict={self.textIoMapDict}{args})"


#-----------------------------------------------------------
# AstNode -> AstStatement -> InstanceBase -> InstanceG2p
#-----------------------------------------------------------
# for g2p module exports
class InstanceG2p(InstanceBase):
    def __init__(self, modExp, textParamMapDict, ioMap, insName=None):
        self.modExp = modExp
        self.textParamMapDict = textParamMapDict.dict if isinstance(textParamMapDict, ParamMap) \
                                else textParamMapDict
        self.ioMapDict = ioMap.dict if isinstance(ioMap, PortMap) else ioMap
        super().__init__(insName)

    def module(self):
        return self.modExp

    def paramUsed(self): return set() #TODO
    def typesUsed(self): return set() #TODO

    def used(self):
        inConn = {self.ioMapDict.get(i.name, i) for i in self.modExp.IOs
                  if isinstance(i, gencore.InputBase)}
        return set.union(*[x.used() for x in inConn])

    def driven(self):
        outConn = {self.ioMapDict.get(o.name, o) for o in self.modExp.IOs
                   if isinstance(o, gencore.OutputBase)}
        return set.union(*[x.lvalue() for x in outConn if x is not None])


    def modName(self):
        return self.modExp.name

    def _textParamMapDict(self):
        return self.textParamMapDict

    def _textIoMapDict(self):
        return _ioToVlogDict(self.ioMapDict, self.modExp.IOs)

    def __repr__(self):
        args = f", insName={self.insName!r}" if self.insName is not None else ""
        return f"InstanceG2p({self.modExp!r}, " + \
               f"textParamMapDict={self.textParamMapDict}, " + \
               f"ioMapDict={self.ioMapDict}{args})"

class PortMap:
    def __init__(self, policy=None, **kwargs):
        self.policy = policy
        self.dict = kwargs

class ParamMapPolicy:
    pass

class ParamMap:
    def __init__(self, policy=None, **kwargs):
        self.policy = policy
        self.dict = kwargs


#-----------------------------------------------------------
# AstNode -> AstStatement -> InstanceBase -> Instance
#-----------------------------------------------------------
# for native chipo modules
class Instance(InstanceBase):
    def __init__(self, mod, paramMap, ioMap, insName=None):
        assert isinstance(paramMap, (dict, ParamMap))
        assert isinstance(ioMap, (dict, PortMap))
        self.mod = mod
        self.paramMapDict = paramMap.dict if isinstance(paramMap, ParamMap) \
                            else paramMap
        self.ioMapDict = ioMap.dict if isinstance(ioMap, PortMap) else ioMap
        super().__init__(insName)

    def module(self):
        return self.mod

    def used(self):
        inConn = {self.ioMapDict.get(i.name, i) for i in self.mod.IOs
                  if isinstance(i, gencore.InputBase)}
        return set.union(*[x.used() for x in inConn])

    def driven(self):
        outConn = {self.ioMapDict.get(o.name, o) for o in self.mod.IOs
                   if isinstance(o, gencore.OutputBase)}
        return set.union(*[x.lvalue() for x in outConn if x is not None])

    def paramUsed(self):
        conn = [self.ioMapDict.get(io.name, io) for io in self.mod.IOs]
        return set.union(*[io.paramUsed() for io in conn
                if isinstance(io, gencore.IoBase)])

    def typesUsed(self):
        return set() #TODO

    def modName(self):
        return self.mod.name

    def _textParamMapDict(self):
        return _paramToTextDict(self.paramMapDict)

    def _textIoMapDict(self):
        return _ioToVlogDict(self.ioMapDict, self.mod.IOs)

    def __repr__(self):
        args = f", insName={self.insName!r}" if self.insName is not None else ""
        return f"Instance({self.mod!r}, paramMapDict={self.paramMapDict}, "+ \
               f"ioMapDict={self.ioMapDict}{args})"


#------------------------------------------------------------------------------
# AstNode -> AstProcStatement : things that can go under a procedural contruct
#------------------------------------------------------------------------------
class AstProcStatement(AstNode):
    def applyFunc(self, f):
        f(self)
        for s in self.all():
            s.applyFunc(f)


#-----------------------------------------------------------
# AstNode -> AstProcStatement -> Block
#-----------------------------------------------------------
class Block(AstProcStatement):
    def __init__(self, *stmts, name=None):
        self.stmts = list(stmts)
        self.name = name

    def __iadd__(self, x):
        self.stmts.append(x)
        return self

    def toList(self):
        return self.stmts

    def Name(self, name):
        self.name = name
        return self

    def assigned(self):  return self.apply('assigned',  self.stmts)
    def used(self):      return self.apply('used',      self.stmts)
    def paramUsed(self): return self.apply('paramUsed', self.stmts)
    def typesUsed(self): return self.apply('typesUsed', self.stmts)
    def driven(self):    return self.apply('driven',    self.stmts)
    def declared(self):  return self.apply('declared',  self.stmts)
    def all(self):       return self.stmts

    def __len__(self):
        return len(self.stmts)

    def __getitem__(self, slc):
        return self.stmts.__getitem__(slc)

    def __repr__(self):
        s = ", ".join(repr(stm) for stm in self.stmts)
        if self.name is not None:
            return f'Block({s}, name={self.name!r})'
        return f'Block({s})'

#-----------------------------------------------------------
# AstNode -> AstProcStatement -> If
#-----------------------------------------------------------
class If(AstProcStatement):

    class ElseClass:
        def __init__(self, parent):
            self.parent = parent

        def doElse(self, stmts):
            self.parent.falseBlock = flattenBlock(stmts)
            return self.parent

        def __getitem__(self, stmts):
            return self.doElse(tupleize(stmts))

        def __call__(self, *stmts):
            return self.doElse(stmts)

    class ElifClass:
        def __init__(self, parent):
            self.parent = parent

        def doElif(self, stmts):
            self.parent.elifBlock.append(flattenBlock(stmts))
            return self.parent

        def __getitem__(self, stmts):
            return self.doElif(tupleize(stmts))

        def __call__(self, cond):
            self.parent.elifCond.append(WrapExpr(cond))
            return self

    def __init__(self, cond=1):
        self.cond = WrapExpr(cond)
        self.trueBlock = Block()
        self.falseBlock = None
        self.elifBlock = []
        self.elifCond = []
        self.Else = self.ElseClass(parent=self)
        self.Elif = self.ElifClass(parent=self)

    def doThen(self, stmts):
        self.trueBlock = flattenBlock(stmts)
        return self

    def __getitem__(self, stmts):
        return self.doThen(tupleize(stmts))

    def Then(self, *trueBlock):
        return self.doThen(trueBlock)

    def assigned(self):  return self.apply('assigned', self.all())
    def used(self):      return self.apply('used', self.all())
    def paramUsed(self): return self.apply('paramUsed', self.all())
    def typesUsed(self): return self.apply('typesUsed', self.all())

    def all(self):
        return self.elifCond + self.elifBlock + \
               [self.cond, self.trueBlock, self.falseBlock]

    def __repr__(self):
        elifv = elsev = ''
        for i, b in enumerate(self.elifBlock):
            elifv = f'.Elif({self.elifCond[i]!r})[{b!r}]'
        if self.falseBlock is not None:
            elsev = f'.Else({self.falseBlock!r})'
        return f'If({self.cond!r}).Then({self.trueBlock!r})' + elifv + elsev


#-----------------------------------------------------------
# AstNode -> AstProcStatement -> While
#-----------------------------------------------------------
class While(AstProcStatement):
    def __init__(self, cond=1):
        self.cond = WrapExpr(cond)
        self.trueBlock = None

    @runtime_validation
    def doDo(self, stmts:tuple):
        self.trueBlock = flattenBlock(stmts)
        return self

    def __getitem__(self, stmts):
        return self.doDo(tupleize(stmts))

    def Do(self, *trueBlock):
        return self.doDo(trueBlock)

    def assigned(self):  return self.apply('assigned', self.all())
    def used(self):      return self.apply('used', self.all())
    def paramUsed(self): return self.apply('paramUsed', self.all())
    def typesUsed(self): return self.apply('typesUsed', self.all())

    def all(self):
        return [self.cond, self.trueBlock]

    def __repr__(self):
        return f'While({self.cond!r}).Do({self.trueBlock!r})'


#-----------------------------------------------------------
# AstNode -> AstProcStatement -> Switch
#-----------------------------------------------------------
class Switch(AstProcStatement):

    class CaseClass(AstProcStatement):
        def __init__(self, parent, *args):
            self.parent = parent
            self.conditionExpr = list(WrapExpr(i) for i in tupleize(*args))
            self.body = None

        @runtime_validation
        def doCase(self, stmts:tuple):
            self.body = flattenBlock(stmts)
            return self.parent

        def __getitem__(self, stmts):
            return self.doCase(tupleize(stmts))

        def Do(self, *stmts):
            return self.doCase(stmts)

        def assigned(self):  return self.apply('assigned', self.all())
        def used(self):      return self.apply('used', self.all())
        def paramUsed(self): return self.apply('paramUsed', self.all())
        def typesUsed(self): return self.apply('typesUsed', self.all())

        def all(self):
            return [self.body] + self.conditionExpr

        def __repr__(self):
            return f"Case({self.conditionExpr!r}).Do({self.body!r})"

    def __init__(self, cond=1):
        self.cond = WrapExpr(cond)
        self.cases = list()
        self.default = Block()

    def Case(self, *conds):
        self.cases.append(self.CaseClass(self, conds))
        return self.cases[-1]

    def Default(self, *stmts):
        self.default = flattenBlock(stmts)
        return self

    def assigned(self):  return self.apply('assigned', self.all())
    def used(self):      return self.apply('used', self.all())
    def paramUsed(self): return self.apply('paramUsed', self.all())
    def typesUsed(self): return self.apply('typesUsed', self.all())

    def all(self):
        return self.cases + [self.default]

    def __repr__(self):
        cases = "".join([f".{i!r}" for i in self.cases])
        return f"Switch({self.cond!r}){cases}.Default({self.default!r})"


#-----------------------------------------------------------
# AstNode -> AstProcStatement -> AssignBase
#-----------------------------------------------------------
# Handle signal and variable assignements
class AssignBase(AstProcStatement):
    def __init__(self, lhs, expr, kind='', oper='='):
        self.lhs = lhs
        self.expr = WrapExpr(expr)
        self.oper = oper
        self.kind = kind

    def assigned(self):
        return self.lhs.lvalue()

    def used(self):
        return self.expr.used()

    def paramUsed(self): return self.apply('paramUsed', self.all())
    def typesUsed(self): return self.apply('typesUsed', self.all())

    def all(self):
        return [self.lhs, self.expr]

    def __repr__(self):
        return f'{self.kind}Assign({self.lhs!r}, {self.expr!r})'


# AstNode -> AstProcStatement -> AssignBase -> VarAssign
class VarAssign(AssignBase):
    def __init__(self, lhs, expr):
        super().__init__(lhs, expr, 'Var', '=')


# AstNode -> AstProcStatement -> AssignBase -> SigAssign
class SigAssign(AssignBase):
    def __init__(self, lhs, expr):
        super().__init__(lhs, expr, 'Sig', '<=')


#-----------------------------------------------------------
# AstNode -> Module
#-----------------------------------------------------------
class Module(AstNode, gencore.ModuleBase, Named):
    def __init__(self, name=None, *, types=[], IOs=[], params=[], bd=[]):
        Named.__init__(self, name)
        gencore.ModuleBase.__init__(self, IOs)
        self.params = list(params)
        self.body = list(bd)
        self.types = list(types)

    def vlog(self, *args, **kwargs):
        import vlog
        return vlog.dump(self, *args, **kwargs)

    def getName(self):
        return self.name

    def getAst(self):
        return self

    def __iadd__(self, x):
        if isinstance(x, (tuple, list)):
            for xi in x:
                self.body.append(xi)
        elif isinstance(x, Block) and x.name is None:
            for xi in x.toList():
                self.body.append(xi)
        else:
            self.body.append(x)
        return self

    def Ios(self, *ios):
        self.IOs += ios
        return self

    def Params(self, *params):
        self.params += params
        return self

    def Types(self, *types):
        self.types += types
        return self

    def __getitem__(self, stmts):
        return self.Body(*tupleize(stmts))

    def Body(self, *stmts):
        for x in stmts:
            self += x  # invoke __iadd__
        return self

    def assigned(self, typ=None):
        typ = typ or (Signal, Variable)
        return {x for stm in self.body for x in stm.assigned()
                if isinstance(x, typ)}

    def used(self, typ=None):
        typ = typ or (Signal, Variable)
        return {x for stm in self.body for x in stm.used()
                if isinstance(x, typ)}

    def driven(self):
        return {x for stm in self.body for x in stm.driven()}

    def declared(self, typ=None):
        typ = typ or (Signal, Variable)
        return {x for stm in self.body for x in stm.declared()
                if isinstance(x, typ)}

    def paramUsed(self):
        return set.union({x for stm in self.body for x in stm.paramUsed()},
                         {x for io  in self.IOs  for x in io.paramUsed()})

    def typesUsed(self):
        return set.union({x for stm in self.body for x in stm.typesUsed()},
                         {x for io  in self.IOs  for x in io.typesUsed()})

    def getInstances(self):
        return [stm for stm in self.body if isinstance(stm, InstanceBase)]

    def _autoOutputs(self): # = {drivenSig} - {usedSig} - {declared}
        usedSig = {s for s in self.used(Signal) if not isinstance(s, Out)}
        declared = self.declared()
        drivenSig = self.assigned(Signal).union(self.driven())
        return (drivenSig.difference(usedSig)).difference(declared)

    def _autoInputs(self): # = {usedSig} - {assignedOrDriven} - {declared}
        usedSig = self.used(Signal)
        declared = self.declared()
        assignedOrDriven = self.assigned(Signal).union(self.driven())
        return (usedSig.difference(assignedOrDriven)).difference(declared)

    def autoSignals(self): # = ({usedSig} ^ {assignedOrDriven}) - {declared}
        usedSig = self.used(Signal)
        declared = self.declared()
        assignedOrDriven = self.assigned(Signal).union(self.driven())
        autoSignalSet = (usedSig.intersection(assignedOrDriven)).difference(declared)
        self.body = sortedAsList(Declare(s) for s in autoSignalSet) + self.body
        return self

    def autoIOs(self): #declared ones are kept in same order
        initIoSet = set(self.IOs)
        extraIns  = {InCopy(x)  for x in self._autoInputs()}
        extraOuts = {OutCopy(x) for x in self._autoOutputs()}
        self.IOs += sortedAsList(extraIns - initIoSet) + \
                    sortedAsList(extraOuts - initIoSet)
        return self

    def autoParams(self): #declared ones are kept in same order
        allParamSet = set(self.params).union(self.paramUsed())
        self.params += sortedAsList(allParamSet - set(self.params))
        return self

    def autoTypes(self): #declared ones are kept in same order
        allTypeSet = set(self.types).union(self.typesUsed())
        self.types += sortedAsList(allTypeSet - set(self.types))
        return self

    def autoInstanceName(self):
        instances = self.getInstances()
        seenIns = set(instances)
        unnamedIns = (i for i in instances if i.insName is None)
        nextIdx = defaultdict(lambda:0)
        for ins in unnamedIns:
            i = nextIdx[ins.modName()]
            while ins.modName() + f"_{i}" in seenIns:
                i += 1
            ins.insName = ins.modName() + f"_{i}"
            seenIns.add(ins.insName)
            nextIdx[ins.modName()] = i+1
        return self

    def autoReset(self):
        for stm in self.body:
            if isinstance(stm, Clocked):
                stm.addResetLogic()
        return self

    def autoGen(self):
        return self.autoReset().autoIOs() \
                   .autoSignals().autoParams() \
                   .autoTypes().autoInstanceName()

    def elab(self):
        s = self.vlog() #for now resolves all names FIXME
        return self.autoReset()

    def __repr__(self):
        typeStr = f"types={self.types!r}, " if self.types else ""
        return f'Module({self.name!r}, {typeStr}IOs={self.IOs!r}, ' + \
               f'params={self.params!r}, body={self.body!r})'


#------------------------------------------------------------------------
# Type related
#------------------------------------------------------------------------
class EnuCoding(Enum):
    autoIncr=0
    oneHot=1
    oneCold=2


#------------------------------------------------------------------------
# AstNode -> Type
#------------------------------------------------------------------------
class Type(AstNode, Named):
    def __init__(self, name):
        Named.__init__(self, name)
        self.signed = False

    def typesUsed(self):
        if isinstance(self, BitVec):
            return set()
        return set([self])


#------------------------------------------------------------------------
# AstNode -> Type -> BitVec
#------------------------------------------------------------------------
class BitVec(Type):
    def __init__(self, width=1, *, name=None, signed:bool=False):
        super().__init__(name)
        self.signed = signed
        self.width = width

    def Signed(self):
        self.signed = True
        return self

    def used(self):
        return set([self])

    def paramUsed(self):
        if isinstance(self.width, Expr):
            return self.width.paramUsed()
        return set()

    def __repr__(self):
        suffix = reprStr(["name", self.name, "self"],
                         ["signed", self.signed, False])
        return f"BitVec(width={self.width}{suffix})"

#------------------------------------------------------------------------
# AstNode -> Type -> Agreg
#------------------------------------------------------------------------
class Field:
    def __init__(self, typ:Type, *names):
        self.typ = typ
        self.names = names

    def __repr__(self):
        inner = listRepr(*self.names)
        return f"Field({self.typ}, {inner})"


class Agreg(Type):
    def __init__(self, *, name=None):
        super().__init__(name)
        self.body = []
        self.fieldDict = {}
        self.fieldList = []

    def __getitem__(self, stmts):
        return self.Body(*tupleize(stmts))

    def Body(self, *stmts):
        for stm in stmts:
            assert isinstance(stm, Field)
            for nm in stm.names:
                if nm in self.fieldDict:
                    raise KeyError(f"Repeated field name {name}.{nm}")
                if nm in self.__dir__():
                    raise KeyError(f"Field name is reserved {name}.{nm}")
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

    def offset(self, fieldName:str):
        assert fieldName in self.fieldDict
        priorFields = takewhile(lambda f : f.names[0] != fieldName, self.body)
        return Agreg.sumList(f.typ.width for f in priorFields)

    def fldWidth(self, fieldName:str):
        assert fieldName in self.fieldDict
        return self.fieldDict[fieldName].width

    def __repr__(self):
        inner = listRepr(*self.body)
        return f"{self.kind}(name={self.name!r}) [{inner}]"


class Rec(Agreg):
    kind='Rec'


def isMultParam(a):
    return isinstance(a, BinExpr) and a.op=='*' and type(a.args[0])==CInt and type(a.args[1])==Parameter


def isParamMult(a):
    return isinstance(a, BinExpr) and a.op=='*' and type(a.args[1])==CInt and type(a.args[0])==Parameter


def normalizeTerm(a):
    if type(a)==Parameter:
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
            if isMultParam(a) and isMultParam(b) and repr(a.args[1])==repr(b.args[1]):
                mx = max(a.args[0].args[0], b.args[0].args[0])
                if mx == 1:
                    return a.args[1]
                return BinExpr('*', mx, a.args[1])
    return IfCond(lst[0] > maxExpr(lst[1:]), lst[0], maxExpr(lst[1:]))


class Union(Agreg):
    kind='Union'

    def offset(self, fieldName:str):
        return 0

    @property
    def width(self):
        fldw = [f.typ.width for f in self.body]
        if all(isInt(x) for x in fldw):
            return max(intVal(w) for w in fldw)
        else:
            return maxExpr(fldw)


class Iface(Agreg):
    kind='Iface'


#------------------------------------------------------------------------
# AstNode -> Type -> Arr
#------------------------------------------------------------------------
class Arr(Type):
    def __init__(self, typ:Type, dims, *, name=None):
        super().__init__(name)
        self.typ = typ
        self._dims = tupleize(dims)

    def size(self, i):
        return self._dims[i]

    def dimensions(self):
        return len(self._dims)

    def __repr__(self):
        return f"Arr(typ={self.typ}, dims={self._dims}, name={self.name!r})"


#------------------------------------------------------------------------
# AstNode -> Type -> Enu
#------------------------------------------------------------------------
class Enu(Type):
    def __init__(self, *vals, style:EnuCoding = EnuCoding.autoIncr,
            name=None):
        self.valDict = {}
        super().__init__(name)
        self.style = style
        self.valNames = []
        assert vals
        for x in vals:
            itemName = type(x) is tuple and x[0] or x
            assert type(itemName) is str
            self.valNames.append(itemName)
        if style==EnuCoding.autoIncr:
            curr = 0
            for v in vals:
                if isinstance(v, tuple):
                    nm, val = v
                    if val < curr:
                        raise ValueError(f"Enu values must be increasing {val}")
                else:
                    nm, val = v, curr
                curr = val+1
                self.valDict[nm]=val
        else:
            raise NotImplementedError(f"{self}")

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
        raise KeyError(f"invalid enum constant {self.name}.{key}")

    @property
    def width(self):
        return self.max().bit_length()

    def __repr__(self):
        valStr = f"{self.valDict}"
        return f"Enu(vals={valStr}, style={self.style}, name={self.name!r})"


#------------------------------------------------------------------------------
#build a function that given an operator returns its priority
#------------------------------------------------------------------------------
def opPri():
    def fillUpPri(priDict):
        pri={}
        for ops, priority in priDict.items():
            for op in ops:
                pri[op] = priority
        return pri

    priMon = fillUpPri({
        ('.',):100, ('~', '&', '|', '^', '~^', '^~', '~&', '~|'):90,
        ('+', '-'):80 })

    priBin = fillUpPri({
        ('.'):99, ('*', '/'):20, ('+', '-'):19, ('<<', '>>'):18,
        ('>', '<', '>='): 17, ('==', '!='): 16,
        ('&',): 15, ('^',): 14, ('|',): 13, #not intuitive
        ('&&',): 12, ('||',): 11 })

    priTer = fillUpPri({ ('?',):0, ('{',):5, ('[',):95 })

    #the function returned, closure on the 3 arrays above
    def getPri(op, numOps):
        return priMon[op] if numOps==1 else \
               priBin[op] if numOps==2 else priTer[op]

    return getPri

getPri = opPri()

#------------------------------------------------------------------------------
# Generate a expresion wrapper out of some constants
#------------------------------------------------------------------------------
def WrapExpr(x):
    if x is None:
        return x
    if isinstance(x, Expr):
        return x
    if isinstance(x, Type):
        return x
    if isinstance(x, int):
        return CInt(x)
    if isinstance(x, str):
        return CEnu(x)
    if isinstance(x, list):
        return Concat(*x)
    raise TypeError(f"Don't know how to covert {x!r} to an expression")


#------------------------------------------------------------------------------
# AstNode -> Expr
#------------------------------------------------------------------------------
class Expr(AstNode):
    def __init__(self, op, *args, numOps=0):
        self.op = op
        self.pri = getPri(op, len(args) if numOps==0 else numOps)
        self.const = False
        self.args = [WrapExpr(arg) for arg in args]

    def __ilshift__(self, n):   raise NotImplementedError(f"{self}")

    def __add__(self, rhs):     return BinExpr('+', self, rhs)
    def __sub__(self, rhs):     return BinExpr('-', self, rhs)
    def __mul__(self, rhs):     return BinExpr('*', self, rhs)
    def __and__(self, rhs):     return BinExpr('&', self, rhs)
    def __or__(self, rhs):      return BinExpr('|', self, rhs)
    def __xor__(self, rhs):     return BinExpr('^', self, rhs)
    def __lshift__(self, rhs):  return BinExpr('<<', self, rhs)
    def __rshift__(self, rhs):  return BinExpr('>>', self, rhs)

    def __radd__(self, lhs):    return BinExpr('+', lhs, self)
    def __rsub__(self, lhs):    return BinExpr('-', lhs, self)
    def __rmul__(self, lhs):    return BinExpr('*', lhs, self)
    def __rand__(self, lhs):    return BinExpr('&', lhs, self)
    def __ror__(self, lhs):     return BinExpr('|', lhs, self)
    def __rxor__(self, lhs):    return BinExpr('^', lhs, self)
    def __rlshift(self, lhs):   return BinExpr('<<', lhs, self)
    def __rrshift__(self, lhs): return BinExpr('>>', lhs, self)

    def __lt__(self, rhs):      return BinExpr('<', self, rhs)
    def __gt__(self, rhs):      return BinExpr('>', self, rhs)
    def __ge__(self, rhs):      return BinExpr('>=', self, rhs)
    def __eq__(self, rhs):      return BinExpr('==', self, rhs)
    def __ne__(self, rhs):      return BinExpr('!=', self, rhs)

    def __neg__(self):          return UnaryExpr('-', self)
    def __invert__(self):       return UnaryExpr('~', self)

    def __getitem__(self, slc): return BitExtract(self, slc)

    def simplify(self):
        return self

    def Eval(self):
        raise TypeError(f"{self!r} cannot be Eval'ed")


    def applyFunc(self, f):
        f(self)
        for s in self.all():
            s.applyFunc(f)

    def all(self):
        return self.args

    def lvalue(self):
        raise TypeError(f"{self!r} is not an lvalue")

    def used(self):      return self.apply('used', self.all())
    def paramUsed(self): return self.apply('paramUsed', self.all())
    def typesUsed(self): return self.apply('typesUsed', self.all())

    def argsStr(self):
        return listRepr(*self.args)

    def __repr__(self):
        return f"{self.op}({self.argsStr()})"

    def __hash__(self):
        return self.__repr__().__hash__()


#------------------------------------------------------------------------
# AstNode -> Expr -> UnaryExpr
#------------------------------------------------------------------------
class UnaryExpr(Expr):
    def __init__(self, op, rhs):
        super().__init__(op, rhs)

    def Eval(self):
        r = self.args[0].Eval()
        return eval(f"{self.op} {r}")

    def applyFunc(self, f):
        f(self)

    #https://stackoverflow.com/questions/53518981/
    #inheritance-hash-sets-to-none-in-a-subclass
    __hash__ = Expr.__hash__


class CInt(UnaryExpr):
    def __init__(self, val, width=None, signed=False):
        self.op = '.'
        self.pri = getPri(self.op, numOps=1)
        self.const = False
        self.args = [val]
        self.width = width
        self.signed = signed
        self.base = 'b' if width==1 else 'd'

    def used(self):      return set()
    def paramUsed(self): return set()
    def typesUsed(self): return set()

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
        suf = '.Hex()' if self.base=='h' else \
              '.Bin()' if self.base=='b' else ''
        if self.signed:
            return f'CInt({self.args[0]!r}, width={self.width}, ' + \
                   f'signed={self.signed}){suf}'
        if self.width is not None:
            return f'CInt({self.args[0]!r}, width={self.width}){suf}'
        return f'CInt({self.args[0]!r}){suf}'


class CEnu(UnaryExpr):
    def __init__(self, val, width=None, signed=False):
        self.op = '.'
        self.pri = getPri(self.op, numOps=1)
        self.const = False
        self.args = [val]
        self.width = width
        self.signed = signed
        self.base = 'b' if width==1 else 'd'

    def used(self):      return set()
    def paramUsed(self): return set()
    def typesUsed(self): return set()

    def Eval(self):
        return self.args[0]

    def __repr__(self):
        if self.signed:
            return f'CEnu({self.args[0]!r}, width={self.width}, ' + \
                   f'signed={self.signed})'
        if self.width is not None:
            return f'CEnu({self.args[0]!r}, width={self.width}){suf}'
        return f'CEnu({self.args[0]!r})'


class Parameter(UnaryExpr, Named):
    def __init__(self, val, name=None):
        super().__init__('.', val)
        Named.__init__(self, name)
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
        return f"Parameter({self.argsStr()}, name={self.name!r})"


#------------------------------------------------------------------------
# AstNode -> Expr -> UnaryExpr -> Assignable
#------------------------------------------------------------------------
class Assignable(UnaryExpr, Named):
    kind = 'Assignable'

    @runtime_validation
    def __init__(self, typ=None, name=None, default=0):
        Named.__init__(self, name)
        if isinstance(typ, Assignable): #from other signal/var
            typ = typ._type()
        elif isinstance(typ, (Expr, int)):
            typ = BitVec(typ)
        elif typ is None:
            typ = BitVec(1)
        else:
            assert isinstance(typ, Type)
        UnaryExpr.__init__(self, '.', typ)
        self.default = default

    def _type(self):
        return self.args[0]

    def Signed(self):
        if isinstance(self._type(), BitVec):
            self._type().Signed()
            return self
        raise TypeError(f"Cannot set signed on non-BitVec {self}")

    def width(self):
        if isinstance(self._type(), BitVec):
            return self._type().width
        raise NotImplementedError(f"no width for {self}")

    def __getattr__(self, key):
        if key.startswith("_"):
            return self.__getattribute__(key)
        typ = self._type()
        assert isinstance(typ, Agreg), f"{self.name} is not aggregate type"
        if key in typ.fieldDict:
            return DotExpr(self, key)
        raise KeyError(f"invalid Rec/Union/Iface field {self.name}.{key} for {self}")

    #def __getitem__(self, lst):
    #    typ = self._type()
    #    assert isinstance(typ, Arr), f"{self.name} is not indexable type"
    #    raise NotImplementedError

    def used(self):
        return set([self])

    def lvalue(self):
        return set([self])

    def __pow__(self, n):
        return Times(n, self)

    def __repr__(self):
        suffix = reprStr(["default", self.default, 0])
        return f"{self.kind}(typ={self._type()!r}, name={self.name!r}{suffix})"


#------------------------------------------------------------------------
# AstNode -> Expr -> UnaryExpr -> Assignable -> Signal
#------------------------------------------------------------------------
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
        suffix = reprStr(["posedge", self.posedge, True])
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
        suffix = reprStr(["asyn", self.asyn, True],
                         ["lowTrue", self.lowTrue, True])
        return f"Reset(name={self.name!r}{suffix})"


#------------------------------------------------------------------------
# AstNode -> Expr -> UnaryExpr -> Assignable -> Variable
#------------------------------------------------------------------------
class Variable(Assignable):
    kind = 'Variable'

    def eq(self, rhs):
        return VarAssign(self, rhs)

    def __ne__(self, rhs): # x != x + 1
        if isinstance(self, Variable):
            return VarAssign(self, rhs)
        return Expr('!=', self, rhs)

    def __matmul__(self, n): # x @ x + 1
        return VarAssign(self, n)

    # TODO, add support for var.a = var.x + 1


#------------------------------------------------------------------------
# AstNode -> Expr -> BinExpr
#------------------------------------------------------------------------
@runtime_validation
def isInt(obj) -> bool:
    return isinstance(obj, (CInt, int))


def intVal(obj):
    if isinstance(obj, CInt):
        return obj.args[0]
    if isinstance(obj, int):
        return obj


class BinExpr(Expr):
    def __init__(self, op, lhs, rhs):
        super().__init__(op, lhs, rhs)

    def Eval(self):
        l = self.args[0].Eval()
        r = self.args[1].Eval()
        return eval(f"{l} {self.op} {r}")

    def simplify(self):
        from simplify import simplifyBinExpr
        return simplifyBinExpr(self)

    def __repr__(self):
        return f"({self.args[0]!r} {self.op} {self.args[1]!r})"


class DotExpr(BinExpr):
    def __init__(self, parent, key, root=None):
        self.op = '.'
        self.pri = getPri(self.op, numOps=2)
        self.const = False
        root = root or parent
        self.typ = parent.args[0].fieldDict[key]
        self.args = [self.typ, parent, key]
        self.root = root

    def used(self):      return set([self.root])
    def paramUsed(self): return set()
    def typesUsed(self): return set()

    def offset(self, key):
        lsb = 0
        curr = self
        while isinstance(curr, DotExpr):
            parent = curr.args[1]
            parentTyp = parent.args[0]
            lsb += parentTyp.offset(key)
            curr = parent
            if isinstance(curr, DotExpr):
                key = curr.args[2]
        return lsb

    def __getattr__(self, key):
        parent = self.args[0]
        typ = self.typ
        assert isinstance(typ, Agreg), f"{typ.name}={typ!r} is not aggregate type"
        if key in typ.fieldDict:
            return DotExpr(self, key, self.root)
        raise KeyError(f"invalid Rec/Union/Iface field {self.name}.{key} for {self}")

    def __getitem__(self, slc): 
        typ = self.args[0]
        assert isinstance(typ, BitVec), f"{self.name} is not indexable type"
        return BitExtract(self, slc)

    def lvalue(self):
        return set([self.args[0]])

    def Eval(self):
        return self.args[0]

    def __hash__(self):
        return self.name.__hash__()

    def __repr__(self):
        suffix = reprStr(["root", self.root, None])
        return f'DotExpr(parent={self.args[1]!r}, key={self.args[2]!r}{suffix})'


#------------------------------------------------------------------------
# AstNode -> Expr -> MultiExpr
#------------------------------------------------------------------------
class MultiExpr(Expr):
    def __init__(self, op, *args, numOps=0):
        super().__init__(op, *args, numOps=numOps)


class BitExtract(MultiExpr):
    def __init__(self, val, msb, lsb=None):
        if isinstance(msb, slice): # BitExtract(x, 3, 2) or x[3:2]
            assert msb.step==None, f"invalid bit selection {msb.step}"
            assert lsb==None
            msb, lsb = msb.start, msb.stop
        super().__init__('[', val, msb, lsb)

    def __le__(self, rhs):
        return SigAssign(self, rhs)

    def lvalue(self):
        return set([self.args[0]])

    __hash__ = Expr.__hash__

    def __repr__(self):
        return f"BitExtract({self.argsStr()})"



class Concat(MultiExpr):
    def __init__(self, *args):
        super().__init__('{', *args, numOps=3)
        self.pri = getPri(self.op, numOps=3)

    def __le__(self, rhs):
        return SigAssign(self, rhs)

    def lvalue(self):
        return set.union(*[x.lvalue() for x in self.all()])

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
    def __init__(self, rhs): super().__init__('|', rhs)


class AndReduce(ExprReduce):
    def __init__(self, rhs): super().__init__('&', rhs)


class XorReduce(ExprReduce):
    def __init__(self, rhs): super().__init__('^', rhs)


#------------------------------------------------------------------------------
# More convenience functions
#------------------------------------------------------------------------------
def OutCopy(x):
    return Out(typ=x.args[0], name=x.name, default=x.default)


def InCopy(x):
    return In(typ=x.args[0], name=x.name, default=x.default)


def Assign(sig, val):
    return Combo() [ sig <= val ]


def Input(n=1, **kwargs):
    if isinstance(n, (Expr, int)):
        return In(BitVec(n), **kwargs)
    return In(n, **kwargs)


def Output(n=1, **kwargs):
    if isinstance(n, (Expr, int)):
        return Out(BitVec(n), **kwargs)
    return Out(n, **kwargs)


def appendStms(body, stmts):
    for stm in stmts:
        body += stm

