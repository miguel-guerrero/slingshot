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
import gencore
import re
import varname
import copy
from collections import defaultdict

INDENT='    '
serialNumber = varname.makeCounter()

#------------------------------------------------------------------------------
# Utilities
#------------------------------------------------------------------------------
def setIndent(x):
    global INDENT
    INDENT = x

def ind(s:str, n:int) -> str:
    return (INDENT*n) + s

def indList(lst:list, n:int) -> list:
    return [ind(item, n) for item in lst]

def indListAsStr(lst:list, n:int, sep=',\n') -> str:
    return sep.join(indList(lst, n))

#pad suffix number if present for nicer sort
def modkey(n): 
    m = re.search(r'^(.+?)(\d+)$', n)
    if m:
        n = m.group(1) + f"{int(m.group(2)):05}"
    return n

def sortedAsList(s):
    return sorted(s, key=lambda x : modkey(x.name))

def tupleize(x):
    if not isinstance(x, tuple):
        x = (x,)
    return x

class GenericExc(BaseException):
    def __init__(self, s):
        self.s = s

#------------------------------------------------------------------------------
# For hybrid g2p / chipo implementations
#------------------------------------------------------------------------------
class ApiGenerator(gencore.GeneratorBase):
    def __init__(self, module, targetDir, targetExt):
         super().__init__(targetDir, targetExt)
         self.module = module

    def runGeneration(self, name, passedParamDict):
        assert self.module.name == name 
        s = self.module.getAst().vlog()
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
# Parent of all AST nodes
#------------------------------------------------------------------------------
class AstNode:
    def assigned(self):  return set()
    def used(self):      return set()
    def paramUsed(self): return set()
    def driven(self):    return set()
    def declared(self):  return set()

    #apply a set-returning method 'm' to non-None items in list and return
    #the union of all returned sets
    def apply(self, m, lst): 
        return set.union(*[getattr(x,m)() for x in lst if x is not None])

#------------------------------------------------------------------------------
# Statement related
#------------------------------------------------------------------------------
class Comment(AstNode):
    def __init__(self, *lines):
        self.lines = lines

    def vlog(self, indLvl):
        vlst = [f"// {cmnt}" for cmnt in self.lines]
        return indListAsStr(vlst, indLvl, sep='\n')

    def __repr__(self):
        return f'Comment{self.lines!r}'

class AstStatement(AstNode):
    def assigned(self):  raise NotImplementedError
    def used(self):      raise NotImplementedError
    def paramUsed(self): raise NotImplementedError

class Block(AstStatement):
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
    def driven(self):    return self.apply('driven',    self.stmts)
    def declared(self):  return self.apply('declared',  self.stmts)

    def vlog(self, indLvl):
        if len(self.stmts) == 1 and self.name is None:
            return "\n" + self.stmts[0].vlog(indLvl+1)
        v = [stm.vlog(indLvl+1) for stm in self.stmts]
        name = "" if self.name is None else " : " + self.name
        return f"begin{name}\n" + \
            indListAsStr(v, 0, sep='\n') + "\n" + ind("end", indLvl)

    def __repr__(self):
        s = ", ".join(repr(stm) for stm in self.stmts)
        if self.name is not None:
            return f'Block({s}, name={self.name!r})'
        return f'Block({s})'

#if passed a list of statements, creates a block
#but if passed a block just returns it, no block wrapper around
def flattenBlock(aTuple):
    assert isinstance(aTuple, tuple)
    if len(aTuple)==1 and isinstance(aTuple[0], Block):
        return aTuple[0]
    return Block(*aTuple)

class If(AstStatement):

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
        self.trueBlock = None
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

    def all(self):
        return self.elifCond + self.elifBlock + \
               [self.cond, self.trueBlock, self.falseBlock]

    def vlog(self, indLvl):
        assert len(self.elifBlock)==len(self.elifCond), "Forgot cond on Elif ?"
        v = ind('if (' + self.cond.vlog(0) + ')', indLvl) + ' ' + \
            self.trueBlock.vlog(indLvl)
        for i, b in enumerate(self.elifBlock):
            v += '\n' + ind('else if (' + self.elifCond[i].vlog(0) + ')', 
                indLvl) + ' ' + b.vlog(indLvl)
        if self.falseBlock is not None:
            v += "\n" + ind("else ", indLvl) + self.falseBlock.vlog(indLvl)
        return v

    def __repr__(self):
        elifv = elsev = ''
        for i, b in enumerate(self.elifBlock):
            elifv = f'.Elif({self.elifCond[i]!r})[{b!r}]'
        if self.falseBlock is not None:
            elsev = f'.Else({self.falseBlock!r})'
        return f'If({self.cond!r}).Then({self.trueBlock!r})' + elifv + elsev

class While(AstStatement):
    def __init__(self, cond=1):
        self.cond = WrapExpr(cond)
        self.trueBlock = None

    def doDo(self, stmts):
        self.trueBlock = flattenBlock(stmts)
        return self

    def __getitem__(self, stmts):
        return self.doDo(tupleize(stmts))

    def Do(self, *trueBlock):
        return self.doDo(trueBlock)

    def assigned(self):  return self.apply('assigned', self.all())
    def used(self):      return self.apply('used', self.all())
    def paramUsed(self): return self.apply('paramUsed', self.all())

    def all(self):
        return [self.cond, self.trueBlock]

    def vlog(self, indLvl):
        return ind('while (' + self.cond.vlog(0) + ')', indLvl) + ' ' + \
               self.trueBlock.vlog(indLvl)

    def __repr__(self):
        return f'While({self.cond!r}).Do({self.trueBlock!r})'

class Switch(AstStatement):

    class CaseClass(AstStatement):
        def __init__(self, parent, *args):
            self.parent = parent
            self.conditionExpr = list(WrapExpr(i) for i in tupleize(*args))
            self.body = None

        def doCase(self, stmts):
            self.body = flattenBlock(stmts)
            return self.parent

        def __getitem__(self, *stmts):
            return self.doCase(tupleize(stmts))
    
        def Do(self, *stmts):
            return self.doCase(stmts)

        def assigned(self):  return self.apply('assigned', self.all())
        def used(self):      return self.apply('used', self.all())
        def paramUsed(self): return self.apply('paramUsed', self.all())

        def all(self):
            return [self.body] + self.conditionExpr 

        def __repr__(self):
            return f"Case({self.conditionExpr!r}).Do({self.body!r})"

        def vlog(self, indLvl):
            cases = ", ".join([i.vlog(0) for i in self.conditionExpr])
            return ind(f'{cases} : ', indLvl) + self.body.vlog(indLvl)

    def __init__(self, cond=1):
        self.cond = WrapExpr(cond)
        self.cases = list()

    def Case(self, *conds):
        self.cases.append(self.CaseClass(self, conds))
        return self.cases[-1]

    def Default(self, *stmts):
        self.default = list(stmts)
        return self

    def assigned(self):  return self.apply('assigned', self.all())
    def used(self):      return self.apply('used', self.all())
    def paramUsed(self): return self.apply('paramUsed', self.all())

    def all(self):
        return self.cases 

    def vlog(self, indLvl):
        cases = indListAsStr([i.vlog(indLvl+1) for i in self.cases], 0, sep='\n')
        return ind('case (' + self.cond.vlog(0) + ')', indLvl) + '\n' + \
               cases + '\n' + ind('endcase', indLvl)

    def __repr__(self):
        cases = "".join([f".{i!r}" for i in self.cases])
        return f"Switch({self.cond!r}){cases}.Default({self.default!r})"

class AssignBase(AstStatement):
    def __init__(self, lhs, expr, kind='', vlogOper='='):
        self.lhs = lhs
        self.expr = WrapExpr(expr)
        self.vlogOper = vlogOper
        self.kind = kind

    def assigned(self):
        return self.lhs.lvalue()

    def used(self):
        return self.expr.used()

    def paramUsed(self):
        return self.expr.paramUsed().union(self.lhs.paramUsed())

    def vlog(self, indLvl):
        return ind(self.lhs.vlog(0) + " " + self.vlogOper + " " + \
               self.expr.vlog(indLvl), indLvl) + ';'

    def __repr__(self):
        return f'{self.kind}Assign({self.lhs!r}, {self.expr!r})'

class VarAssign(AssignBase):
    def __init__(self, lhs, expr):
        super().__init__(lhs, expr, 'Var', '=')


class SigAssign(AssignBase):
    def __init__(self, lhs, expr):
        super().__init__(lhs, expr, 'Sig', '<=')

#------------------------------------------------------------------------------
# Expression related
#------------------------------------------------------------------------------

#build a function that given an operator returns its priority
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
        ('*', '/'):20, ('+', '-'):19, ('<<', '>>'):18, ('>', '<', '>='): 17,
        ('==', '!='): 16, 
        ('&',): 15, ('^',): 14, ('|',): 13, #not intuitive
        ('&&',): 12, ('||',): 11 })

    priTer = fillUpPri({ ('?',):0, ('{',):5, ('[',):95 })

    #the function returned, closure on the 3 arrays above
    def getPri(op, numOps):
        return priMon[op] if numOps==1 else \
               priBin[op] if numOps==2 else priTer[op]

    return getPri

getPri = opPri()

class CInt(AstNode):
    def __init__(self, val, width=None, signed=False):
        self.val = val
        self.width = width
        self.signed = signed
        self.base = 'b' if width==1 else 'd'

    def Eval(self):
        return self.val

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

    def vlog(self, indLvl):
        prefix = '-' if self.signed and self.val < 0 else ''
        sz = "'" if self.width is None else f"{self.width}'"
        sgn = 's' if self.signed else ''
        fmt = 'x' if self.base == 'h' else self.base
        num = f'{abs(self.val):{fmt}}'
        if sz + sgn + self.base == "'d": # omit 'd prefix if alone
            return prefix + num
        return prefix + sz + sgn + self.base + num

    def __repr__(self):
        suf = '.Hex()' if self.base=='h' else \
              '.Bin()' if self.base=='b' else ''
        if self.signed:
            return f'CInt({self.val!r}, width={self.width}, ' + \
                   f'signed={self.signed}){suf}'
        if self.width is not None:
            return f'CInt({self.val!r}, width={self.width}){suf}'
        return f'CInt({self.val!r}){suf}'

def WrapExpr(x):
    if isinstance(x, (Expr, BitVec, UnaryExpr, CInt)):
        return x
    if isinstance(x, int):
        return CInt(x)
    if isinstance(x, list):
        return Concat(*x)
    raise GenericExc(f"Don't know how to covert {x!r} to an expression")

class Expr(AstNode):
    def __init__(self, op, lhs, rhs):
        self.op = op
        self.lhs = WrapExpr(lhs)
        self.rhs = WrapExpr(rhs)
        self.pri = getPri(op, numOps=2)

    def Eval(self):
        l = self.lhs.Eval() if self.lhs is not None else ""
        r = self.rhs.Eval()
        return eval(f"{l} {self.op} {r}")

    def __ilshift__(self, n):   raise NotImplementedError

    def __add__(self, rhs):     return Expr('+', self, rhs)
    def __sub__(self, rhs):     return Expr('-', self, rhs)
    def __mul__(self, rhs):     return Expr('*', self, rhs)
    def __and__(self, rhs):     return Expr('&', self, rhs)
    def __or__(self, rhs):      return Expr('|', self, rhs)
    def __xor__(self, rhs):     return Expr('^', self, rhs)
    def __lshift__(self, rhs):  return Expr('<<', self, rhs)
    def __rshift__(self, rhs):  return Expr('>>', self, rhs)

    def __radd__(self, lhs):    return Expr('+', lhs, self)
    def __rsub__(self, lhs):    return Expr('-', lhs, self)
    def __rmul__(self, lhs):    return Expr('*', lhs, self)
    def __rand__(self, lhs):    return Expr('&', lhs, self)
    def __ror__(self, lhs):     return Expr('|', lhs, self)
    def __rxor__(self, lhs):    return Expr('^', lhs, self)
    def __rlshift(self, lhs):   return Expr('<<', lhs, self)
    def __rrshift__(self, lhs): return Expr('>>', lhs, self)

    def __lt__(self, rhs):      return Expr('<', self, rhs)
    def __gt__(self, rhs):      return Expr('>', self, rhs)
    def __ge__(self, rhs):      return Expr('>=', self, rhs)
    def __eq__(self, rhs):      return Expr('==', self, rhs)
    def __ne__(self, rhs):      return Expr('!=', self, rhs)

    def __neg__(self):          return UnaryExpr('-', self)
    def __invert__(self):       return UnaryExpr('~', self)

    def __getitem__(self, slc): return BitExtract(self, slc)

    def __le__(self, rhs):
        return SigAssign(self, rhs)

    def lvalue(self):
        assert False, f'{self.name} is not an lvalue'

    def used(self):      return self.apply('used', self.all())
    def paramUsed(self): return self.apply('paramUsed', self.all())
        
    def all(self):
        return (self.lhs, self.rhs)

    # convert expr to vlog and parenthesize if expr operator is lower pri than 
    # self.op/pri
    def paren(self, expr):
        v = expr.vlog(0)
        if isinstance(expr, Expr) and expr.pri < self.pri:
            return '('+v+')'
        return v

    def vlog(self, indLvl):
        return self.paren(self.lhs) + " " + self.op + " " + self.paren(self.rhs)

    def __repr__(self):
        return f"({self.lhs!r} {self.op} {self.rhs!r})"

class UnaryExpr(Expr):
    def __init__(self, op, rhs):
        self.op = op
        self.lhs = None
        self.rhs = WrapExpr(rhs)
        self.pri = getPri(op, numOps=1)

    def vlog(self, indLvl):
        return self.op + self.paren(self.rhs) 

    def __repr__(self):
        return f"{self.op}({self.rhs!r})"

class NoEvalExpr(Expr):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Concat(NoEvalExpr):
    def __init__(self, *opt):
        self.op = '{'
        self.lhs = self.rhs = None
        self.all_ = [WrapExpr(x) for x in opt]
        self.pri = getPri(self.op, numOps=3)

    def all(self):
        return self.all_

    def lvalue(self):
        return set.union(*[x.lvalue() for x in self.all_])

    def vlog(self, indLvl):
        return '{\n'+ indListAsStr([self.paren(x) for x in self.all_], indLvl+1) +'}'

    def __repr__(self):
        return f"Concat({self.all_!r})"

class IfCond(NoEvalExpr):
    def __init__(self, cond, ift, iff):
        self.op = '?'
        self.cond = WrapExpr(cond)
        self.ift = ift
        self.iff = iff
        self.pri = getPri(self.op, numOps=3)

    def all(self):
        return (self.cond, self.ift, self.iff)

    def vlog(self, indLvl):
        return self.paren(self.cond) + ' ? ' + self.ift.vlog(0) + \
                                       ' : ' + self.iff.vlog(0) 
    def __repr__(self):
        return f"IfCond({self.cond!r}, {self.ift!r}, {self.iff!r})"

class BitExtract(NoEvalExpr):
    def __init__(self, val, msb, lsb=None):
        if isinstance(msb, slice): # BitExtract(x, 3, 2) or x[3:2]
            assert msb.step==None, f"invalid bit selection {msb.step}"
            assert lsb==None
            msb, lsb = msb.start, msb.stop
        self.op = '['
        self.lhs = WrapExpr(val)
        self.rhs = WrapExpr(msb)
        self.rhs2 = None if lsb is None else WrapExpr(lsb)
        self.pri = getPri(self.op, numOps=3)

    def lvalue(self):
        return set([self.lhs])

    def all(self):
        return (self.lhs, self.rhs, self.rhs2)

    def __hash__(self):
        return self.__repr__().__hash__()

    def vlog(self, indLvl):
        lsbv = '' if self.rhs2 is None else ':' + self.rhs2.vlog(0)
        return self.paren(self.lhs) + '['+ self.rhs.vlog(0) + lsbv +']'

    def __repr__(self):
        rest = '' if self.rhs2 is None else f", {self.rhs2!r})"
        return f"BitExtract({self.lhs!r}, {self.rhs!r}{rest})"

class ExprReduce(NoEvalExpr):
    def __init__(self, op, rhs):
        assert op in ('&', '|', '^', '~^', '^~', '~&', '~|')
        self.op = op
        self.rhs = WrapExpr(rhs)
        self.pri = getPri(op, numOps=1)

    def all(self):
        return (self.rhs,)

    def vlog(self, indLvl):
        return self.op + self.paren(self.rhs) 

    def __repr__(self):
        return f"ExprReduce({self.op!r}, {self.rhs!r})"

class OrReduce(ExprReduce):
    def __init__(self, rhs): super().__init__('|', rhs)

class AndReduce(ExprReduce):
    def __init__(self, rhs): super().__init__('&', rhs)

class XorReduce(ExprReduce):
    def __init__(self, rhs): super().__init__('^', rhs)

class Parameter(Expr, varname.Named):
    def __init__(self, default, name=None):
        varname.Named.__init__(self, name)
        self.default = WrapExpr(default)
        self.pri = getPri('.', numOps=1)

    def Eval(self):
        return self.default.Eval()

    def used(self):
        return set()

    def paramUsed(self):
        return set([self])

    def __hash__(self):
        return self.name.__hash__()

    def vlog(self, indLvl, ctx=''):
        v = f'{self.name}'
        if ctx == 'io':
            v = f"parameter {v} = {self.default.vlog(0)}"
        return v

    def __repr__(self):
        return f"Parameter({self.default!r}, name={self.name!r})"

class BitVec(gencore.BitVecBase, NoEvalExpr):
    def __init__(self, width=1, *, name=None, default=0, signed=False):
        if isinstance(width, gencore.BitVecBase):
            #we got a BitVecBase passed as width, use its width
            width = width.width 
        gencore.BitVecBase.__init__(self, width=width, name=name)
        self.default = default
        self.signed = signed
        self.pri = getPri('.', numOps=1)
        self.kind = 'BitVec'
        self.isReg = False

    def lvalue(self):
        return set([self])

    def __pow__(self, n):
        return Times(n, self)

    def __hash__(self):
        return self.name.__hash__()

    def Signed(self):
        self.signed = True
        return self

    def Default(self, x):
        self.default = x
        return self

    def used(self):
        return set([self])

    def paramUsed(self):
        if isinstance(self.width, Expr):
            return self.width.paramUsed()
        return set()

    def eq(self, rhs):      raise NotImplementedError
    def __le__(self, rhs):  raise NotImplementedError
    def update(self, rhs):  raise NotImplementedError

    def vlogMsb(self):
        if isinstance(self.width, Parameter):
            return f"{self.width.name}-1"
        if isinstance(self.width, Expr):
            return Expr('-', self.width, CInt(1)).vlog(0)
        return f"{self.getMsb()}"

    def vlogSigned(self):
        if self.signed:
            return ' signed'
        return ''

    def vlogReg(self):
        if self.kind == "Output" and self.isReg:
            return ' reg'
        return ''

    def vlog(self, indLvl, ctx=''):
        v = f'{self.name}'
        if ctx == 'io':
            if isinstance(self.width, int) and self.width != 1 or \
               isinstance(self.width, Expr):
                v += f"[{self.vlogMsb()}:0]"
        return v

    def __repr__(self):
        args = gencore.BitVecBase.__repr__(self)
        if self.default != 0:
            args += f', default={self.default}'
        if self.signed:
            args += f', signed={self.signed}'
        return f'{self.kind}({args})'

class Variable(BitVec):
    def __init__(self, width=1, name=None, default=0, signed=False):
        super().__init__(width=width, name=name, default=default, signed=signed)
        self.kind = 'Variable'

    def eq(self, rhs):
        return VarAssign(self, rhs)

    def __matmul__(self, n):
        return VarAssign(self, n)

    """
    def __eq__(self, n):
        if isinstance(self, Variable):
            return VarAssign(self, n)
        return Expr('==', self, rhs)

    def __hash__(self):
        return self.name.__hash__()
    """

class Signal(BitVec):
    def __init__(self, width=1, *, name=None, default=0, signed=False):
        super().__init__(width=width, name=name, default=default, signed=signed)
        self.kind = 'Signal'

    def __le__(self, rhs):
        return SigAssign(self, rhs)

    def update(self, rhs):
        return SigAssign(self, rhs)

class Declare(AstNode):
    def __init__(self, x):
        assert isinstance(x, (Signal, Variable))
        self.x = x

    @property
    def name(self):
        return self.x.name

    def declared(self):
        return set([self.x])

    #signal declarations are converted to reg/wires at Module
    def vlog(self, indLvl, ctx=''):
        return "" # f"// Declare signal {self!r}"

    def __repr__(self):
        return f"Declare({self.x!r})"

#has only temporary life while converting to vlog
class Reg(BitVec):
    def __init__(self, sig):
        super().__init__(width=sig.width, name=sig.name, 
                         default=sig.default, signed=sig.signed)
        self.typ = 'Reg'

    def vlog(self, indLvl):
        typ = 'reg' + self.vlogSigned()
        if self.width != 1:
            return ind(f"{typ} [{self.vlogMsb()}:0] {self.name};", indLvl)
        return ind(f"{typ} {self.name};", indLvl)

    def __repr__(self):
        raise NotImplementedError

#has only temporary life while converting to vlog
class Wire(BitVec):
    def __init__(self, sig):
        super().__init__(width=sig.width, name=sig.name, 
                         default=sig.default, signed=sig.signed)
        self.typ = 'Wire'

    def vlog(self, indLvl):
        typ = 'wire' + self.vlogSigned()
        if self.width != 1:
            return ind(f"{typ} [{self.vlogMsb()}:0] {self.name}; // auto", 
                       indLvl)
        return ind(f"{typ} {self.name}; // auto", indLvl)

    def __repr__(self):
        raise NotImplementedError

#------------------------------------------------------------------------------
# IO related
#------------------------------------------------------------------------------
class Io(Signal):
    def __init__(self, width, name, default, signed):
        Signal.__init__(self, width=width, name=name, default=default, signed=signed)
        self.kind='io'

    def vlog(self, indLvl, ctx=''):
        if ctx=='io':
            typ = self.kind.lower() + self.vlogReg() + self.vlogSigned()
            if self.width != 1:
                return ind(f"{typ} [{self.vlogMsb()}:0] {self.name}", indLvl)
            return ind(f"{typ} {self.name}", indLvl)
        return super().vlog(indLvl)

    def __str__(self):
        return self.__repr__()

class Output(Io, gencore.OutputBase):
    def __init__(self, width=1, *, name=None, default=0, signed=False):
        super().__init__(width=width, name=name, default=default, signed=signed)
        self.kind = 'Output'

class Input(Io, gencore.InputBase):
    def __init__(self, width=1, *, name=None, default=0, signed=False):
        super().__init__(width=width, name=name, default=default, signed=signed)
        self.kind = 'Input'

class Clock(Input):
    def __init__(self, *, name=None, posedge=True):
        super().__init__(width=1, name=name)
        self.posedge = posedge

    def edge(self):
        return "posedge" if self.posedge else "nedgede"

    def vlog(self, indLvl, ctx=''):
        if ctx=='io':
            return super().vlog(indLvl, ctx)
        if ctx=='event':
            return self.edge() + " " + self.name
        return self.name

    def __repr__(self):
        edge = f", posedge=False" if not self.posedge else ''
        return f"Clock(name={self.name!r}{edge})"

class Reset(Input):
    def __init__(self, *, name=None, asyn=True, lowTrue=True):
        super().__init__(width=1, name=name)
        self.asyn = asyn
        self.lowTrue = lowTrue

    def onExpr(self):
        return ~self if self.lowTrue else self

    def offExpr(self):
        return self if self.lowTrue else ~self

    def edge(self):
        return "negedge" if self.asyn and self.lowTrue else \
               "posedge" if self.asyn and not self.lowTrue else "" 

    def vlog(self, indLvl, ctx=''):
        if ctx=='io':
            return super().vlog(indLvl, ctx)
        if ctx=='event':
            if self.asyn:
                return self.edge() + " " + self.name
            return ""
        return self.name

    def __repr__(self):
        if not self.lowTrue:
            return f"Reset(name={self.name!r}, asyn={self.asyn}, " + \
                   f"lowTrue={self.lowTrue})"
        if not self.asyn:
            return f"Reset(name={self.name!r}, asyn={self.asyn})"
        return f"Reset(name={self.name!r})"

#------------------------------------------------------------------------------
# Module related
#------------------------------------------------------------------------------
class Module(AstNode, gencore.ModuleBase, varname.Named):
    def __init__(self, name=None, *, IOs=[], params=[], bd=[]):    
        varname.Named.__init__(self, name)
        gencore.ModuleBase.__init__(self, IOs)
        self.params = list(params)
        self.body = list(bd)

    def getName(self):
        return self.name

    def getAst(self):
        return self

    def __iadd__(self, x):
        self.body.append(x)
        return self

    def Ios(self, *ios):
        self.IOs += ios
        return self

    def Params(self, *params):
        self.params += params
        return self

    def __getitem__(self, stmts):
        return self.Body(*tupleize(stmts))

    def Body(self, *stmts):
        self.body += stmts
        return self

    def assigned(self, typ=(Signal, Variable)):
        return {x for stm in self.body for x in stm.assigned() 
                if isinstance(x, typ)}

    def used(self, typ=(Signal, Variable)):
        return {x for stm in self.body for x in stm.used() 
                if isinstance(x, typ)}

    def driven(self):
        return {x for stm in self.body for x in stm.driven()}

    def declared(self, typ=(Signal, Variable)):
        return {x for stm in self.body for x in stm.declared() 
                if isinstance(x, typ)}

    def paramUsed(self):
        return set.union({x for stm in self.body for x in stm.paramUsed()},
                         {x for io in self.IOs for x in io.paramUsed()})
          
    def getInstances(self):
        return [stm for stm in self.body if isinstance(stm, InstanceBase)]

    def _autoOutputs(self): # = {drivenSig} - {usedSig} - {declared}
        usedSig = {s for s in self.used(Signal) if not isinstance(s, Output)}
        declared = self.declared()
        drivenSig = self.assigned(Signal).union(self.driven())
        return (drivenSig.difference(usedSig)).difference(declared)

    def _autoInputs(self): # = {usedSig} - {drivenSig} - {declared}
        usedSig = self.used(Signal)
        declared = self.declared()
        drivenSig = self.assigned(Signal).union(self.driven())
        return (usedSig.difference(drivenSig)).difference(declared)

    def autoSignals(self): # = ({usedSig} ^ {drivenSig}) - {declared}
        usedSig = self.used(Signal)
        declared = self.declared()
        drivenSig = self.assigned(Signal).union(self.driven())
        autoSignalSet = (usedSig.intersection(drivenSig)).difference(declared)
        self.body = sortedAsList(Declare(s) for s in autoSignalSet) + self.body
        return self

    def autoIOs(self): #declared ones are kept in same order
        initIoSet = set(self.IOs)
        extraIns  = {InputCopy(x)  for x in self._autoInputs()}
        extraOuts = {OutputCopy(x) for x in self._autoOutputs()}
        self.IOs += sortedAsList(extraIns - initIoSet) + \
                    sortedAsList(extraOuts - initIoSet)
        return self

    def autoParams(self): #declared ones are kept in same order
        allParamSet = set(self.params).union(self.paramUsed())
        self.params += sortedAsList(allParamSet - set(self.params))
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
                   .autoSignals().autoParams().autoInstanceName()

    def elab(self):
        s = self.vlog(0) #for now resolves all names
        return self.autoReset()

    def annotateUses(self, x):
        return [Wire(sig) for sig in sortedAsList(x)]

    def annotateRegs(self, x):
        return [Reg(sig) for sig in sortedAsList(x)]

    def vlog(self, indLvl=0, recursive=False):

        instancesStr = ''
        if recursive:
            doneSet = set()
            for i in self.getInstances():
                if i.module() is None: #legacy instance
                    instancesStr += f"// INFO: {i} is external\n"
                elif i.module().getName() not in doneSet:
                    instancesStr += i.module().vlog(indLvl, recursive) + '\n'
                    doneSet.add(i.module().getName())

        
        #collect all assigned Signals 
        sigAsgn = self.assigned()
        for io in self.IOs:
            if io in sigAsgn:
                io.isReg = True

        #convert IOs[] into a verilog string
        ioStr = indListAsStr((io.vlog(indLvl+1, 'io') for io in self.IOs), 0)

        #out of all assigned Signals and create reg declarations for them
        #excluding IO's as they are already declared reg in the port list
        regDecl = self.annotateRegs(sigAsgn.difference(set(self.IOs)))
        regDeclStr = indListAsStr((decl.vlog(indLvl) for decl in regDecl), 
                                  0, sep="\n")

        #collect all declared Signals and create wire declarations for 
        #the ones not already IO's or regs
        sigDecl = self.declared(Signal)
        undeclUsed = self.annotateUses(
                        sigDecl.difference(set(self.IOs)).difference(sigAsgn))
        undeclUsedStr = indListAsStr((uu.vlog(indLvl) for uu in undeclUsed), 
                                     0, sep="\n")
        #convert all statements in the body to verilog
        bodyLst = [stm.vlog(indLvl) for stm in self.body]
        bodyStr = indListAsStr([stm for stm in bodyLst if stm != ''], 0, 
                                sep="\n\n")

        #convert parameters to verilog
        paramStr = ''
        if self.params != []:
            paramStr = indListAsStr((p.vlog(0, 'io') for p in self.params), 
                                    indLvl+1, sep=",\n")
            paramStr = ind('\n#(\n', indLvl) + paramStr + ')\n'

        return instancesStr + \
               f'//'+ (76*'-') +'\n'+ \
               f'// {self.name}\n'+ \
               f'//'+ (76*'-') +'\n'+ \
               f'module {self.name} {paramStr}(\n{ioStr}\n);\n'+ \
               f'{undeclUsedStr}\n{regDeclStr}\n\n'+ \
               f'{bodyStr}\n\nendmodule\n'

    def __repr__(self):
        return f'Module({self.name!r}, IOs={self.IOs!r}, ' + \
               f'params={self.params!r}, body={self.body!r})'

class Clocked(AstNode):
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
        for stm in stmts:
            self.body += stm
        return self

    def assigned(self):
        return self.body.assigned()

    def used(self):
        return set([self.clock, self.reset]).union(self.body.used())

    def Name(self, name):
        self.body.name = name
        return self

    def genResetLogic(self):
        d = self.body.assigned()
        lst = [SigAssign(var, var.default) for var in d]
        if lst == []:
            return self.body
        lst = sorted(lst, key=lambda x : x.lhs.name)
        return Block(If(self.reset.onExpr()).Then(*lst).Else(self.body))

    def addResetLogic(self):
        if self.autoReset and self.reset is not None:
            self.body = self.genResetLogic()
        return self

    def vlog(self, indLvl):
        events = [self.clock.vlog(indLvl, 'event')]
        if self.reset is not None:
            resetStr = self.reset.vlog(indLvl, 'event')
            if resetStr != "":
                events.append(resetStr)
        sensStr = " or ".join(events)
        bodyStr = self.body.vlog(indLvl)
        return ind(f'always @({sensStr}) ', indLvl) + bodyStr

    def __repr__(self):
        return f'Clocked({self.clock}, reset={self.reset!r}, ' + \
               f'autoReset={self.autoReset}).Body({self.body!r})'

class Combo(AstNode):
    def __init__(self, body=None):
        self.body = Block() if body is None else body

    def __iadd__(self, x):
        self.body += x
        return self

    def __getitem__(self, stmts):
        return self.Body(*tupleize(stmts))

    def Body(self, *stmts):
        for stm in stmts:
            self.body += stm
        return self

    def assigned(self):  return self.body.assigned()
    def used(self):      return self.body.used()
    def paramUsed(self): return self.body.paramUsed()

    def Name(self, name):
        self.body.name = name
        return self

    def vlog(self, indLvl):
        bodyStr = self.body.vlog(indLvl)
        return ind(f'always @(*) ', indLvl) + bodyStr

    def __repr__(self):
        return f'Combo(body={self.body!r})'

#------------------------------------------------------------------------------
# Instance related
#------------------------------------------------------------------------------
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
    name = lambda io : io.name if isinstance(io, Signal) else io
    d = {name(io): name(io) for io in IOs} # default name mapping
    for io, v in ioMapDict.items(): # override based on input
        if isinstance(io, Signal):
            assert io.name in d, 'signal in port map is not a port: ' + io.name
        if isinstance(io, str):
            assert io in d, 'signal in port map is not a port: ' + io
        d[name(io)] = v.vlog(0) if v is not None else ''
    return d

def _paramToTextDict(paramMapDict):
    name = lambda p : p.name if isinstance(p, Parameter) else p
    return {name(p) : name(v) for p, v in paramMapDict.items()}

class InstanceBase(AstNode):
    def __init__(self, insName):
        self.insName = insName

    def module(self):
        return None

    #must be overriden
    def used(self):              raise NotImplementedError
    def modName(self):           raise NotImplementedError
    def _textParamMapDict(self): raise NotImplementedError
    def _textIoMapDict(self):    raise NotImplementedError

    def _insName(self):
        if self.insName is not None:
            return self.insName
        return f"unamed_ins_{serialNumber()}"

    def paramPassVlog(self, indLvl):
        lst = [f".{k}({v})"for k, v in self._textParamMapDict().items()]
        if len(lst) == 0:
            return ""
        return '#(\n' + indListAsStr(lst, indLvl+1) + '\n' + ind(')', indLvl)

    def ioPassVlog(self, indLvl): 
        lst = [f".{k}({v})"for k, v in self._textIoMapDict().items()]
        if len(lst) == 0:
            return ""
        return '(\n' + indListAsStr(lst, indLvl+1) + '\n' + ind(');', indLvl)

    def vlog(self, indLvl):
        out  = ind(f"{self.modName()} ", indLvl)
        out += self.paramPassVlog(indLvl)
        out += f" {self._insName()} " + self.ioPassVlog(indLvl)
        return out

# for existing verilog modules
class InstanceLegacy(InstanceBase):
    def __init__(self, moduleName, textParamMapDict, textIoMapDict, insName=None):
        self.moduleName = moduleName
        self.textParamMapDict = textParamMapDict
        self.textIoMapDict = textIoMapDict
        super().__init__(insName)

    def used(self):
        return set()

    def paramUsed(self): #TODO
        return set()

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

    def used(self):
        inConn = {self.ioMapDict.get(i.name, i) for i in self.modExp.IOs
                  if isinstance(i, gencore.InputBase)}
        return set.union(*[x.used() for x in inConn])

    def driven(self):
        outConn = {self.ioMapDict.get(o.name, o) for o in self.modExp.IOs
                   if isinstance(o, gencore.OutputBase)}
        return set.union(*[x.lvalue() for x in outConn if x is not None])

    def paramUsed(self): #TODO
        return set()

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

class PortMapPolicy:
    pass

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
# Convenience functions
#------------------------------------------------------------------------------
def OutputCopy(x):
    return Output(width=x.width, name=x.name, default=x.default, signed=x.signed)

def InputCopy(x):
    return Input(width=x.width, name=x.name, default=x.default, signed=x.signed)

def Assign(sig, val):
    return Combo() [ sig <= val ]

# Short-cut to generate n copies of an object. e.g Input() ** 2
def Times(n, obj):
    return [obj] + [copy.copy(obj) for i in range(1, n)]

