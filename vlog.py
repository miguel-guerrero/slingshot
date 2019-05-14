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

import chipo
from enum import Enum, IntEnum
from functools import singledispatch

try:
    from enforce import runtime_validation, config
    config({'mode':'covariant'}) # base class type covers type of subclasses
except:
    runtime_validation = lambda x : x

class Ctx(Enum):
    default=0
    io=1
    event=2

# not planned:
#  1995    - IEEE1364-1995
#  2005    - IEEE1364-2005
class Style(IntEnum):
    v2001=0   # IEEE1364-2001
    sv2005l=1 # IEEE1800-2005 + logic
    sv2009=2  # IEEE1800-2009
    sv2012=3  # IEEE1800-2012

STYLE = Style.v2001
#STYLE = Style.sv2005l
def setStyle(x:Style):
    global STYLE
    STYLE = x

INDENT='    '

@runtime_validation
def setIndent(x:str):
    global INDENT
    INDENT = x

@runtime_validation
def ind(s:str, n:int) -> str:
    return (INDENT*n) + s

def indList(lst:list, n:int) -> list:
    return [ind(item, n) for item in lst]

def indListAsStr(lst:list, n:int, sep=',\n') -> str:
    return sep.join(indList(lst, n))


# convert expr to vlog and parenthesize if expr operator is lower pri than 
# node.op/pri
def paren(node, expr):
    v = dump(expr)
    if isinstance(expr, chipo.Expr) and expr.pri < node.pri:
        return '('+v+')'
    return v


@runtime_validation
def dumpSigned(typ:chipo.Type):
    if typ.signed:
        return ' signed'
    return ''


def dumpParamPass(node, indLvl):
    lst = [f".{k}({v})"for k, v in node._textParamMapDict().items()]
    if len(lst) == 0:
        return ""
    return '#(\n' + indListAsStr(lst, indLvl+1) + '\n' + ind(')', indLvl)


def dumpIoPass(node, indLvl): 
    lst = [f".{k}({v})"for k, v in node._textIoMapDict().items()]
    if len(lst) == 0:
        return ""
    return '(\n' + indListAsStr(lst, indLvl+1) + '\n' + ind(');', indLvl)


def dumpMsb(node):
    if isinstance(node.width, chipo.Parameter):
        return f"{node.width.name}-1"
    if isinstance(node.width, chipo.Expr):
        return dump(chipo.Expr('-', node.width, chipo.CInt(1)))
    return f"{node.width-1}"


#has only temporary life while converting to vlog
class TempLogic(chipo.BitVec):
    def __init__(self, sig):
        super().__init__(width=sig.args[0].width, name=sig.name, 
            signed=sig.args[0].signed)
        self.default = sig.default


class Reg(TempLogic):
    typ = 'Reg'


class Wire(TempLogic):
    typ = 'Wire'


class Logic(TempLogic):
    typ = 'Logic'


def annotateRegs(x):
    if STYLE >= Style.sv2005l:
        return [Logic(sig) for sig in chipo.sortedAsList(x)]
    return [Reg(sig) for sig in chipo.sortedAsList(x)]
    

def annotateUses(x):
    if STYLE >= Style.sv2005l:
        return [Logic(sig) for sig in chipo.sortedAsList(x)]
    return [Wire(sig) for sig in chipo.sortedAsList(x)]


#-----------------------------------------------------------------------------
# why are we doing this instead of just simple inheritance? to keep
# several code dumpers separate and avoid cluttering the original classes
#-----------------------------------------------------------------------------

@singledispatch
def dump(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    if isinstance(node, chipo.AstStatement):
        assert False, f"undefined dump(AstStatement) for {node}"
    elif isinstance(node, chipo.AstProcStatement):
        assert False, f"undefined dump(AstProcStatement) for {node}"
    elif isinstance(node, chipo.AstNode):
        assert False, f"undefined dump(AstNode) for {node}"
    elif isinstance(node, chipo.Type):
        assert False, f"undefined dump(Type) for {node}"
    assert False, f"unhandled dump case. node={node}"

#-----------------------------------------------------------------------------
# AstNode derived
#-----------------------------------------------------------------------------
@dump.register(chipo.Comment)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    vlst = [f"// {cmnt}" for cmnt in node.lines]
    return indListAsStr(vlst, indLvl, sep='\n')


@dump.register(chipo.Module)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    instancesStr = ''
    if recursive:
        doneSet = set()
        for i in node.getInstances():
            if i.module() is None: #legacy instance
                instancesStr += f"// INFO: {i} is external\n"
            elif i.module().getName() not in doneSet:
                instancesStr += i.module().vlog(indLvl, recursive=recursive) + '\n'
                doneSet.add(i.module().getName())
    
    #collect all assigned Signals 
    sigAsgn = node.assigned()
    for io in node.IOs:
        if io in sigAsgn and isinstance(io, chipo.Out):
            io.isReg = True

    #convert IOs[] into a verilog string
    ioStr = indListAsStr((dump(io, indLvl+1, ctx=Ctx.io) for io in node.IOs), 0)

    #out of all assigned Signals and create reg declarations for them
    #excluding IO's as they are already declared reg in the port list
    regDecl = annotateRegs(sigAsgn.difference(set(node.IOs)))
    regDeclStr = indListAsStr((dump(decl, indLvl) for decl in regDecl), 
        0, sep="\n")

    #collect all declared Signals and create wire declarations for 
    #the ones not already IO's or regs
    sigDecl = node.declared(chipo.Signal)
    undeclUsed = annotateUses(
                    sigDecl.difference(set(node.IOs)).difference(sigAsgn))
    undeclUsedStr = indListAsStr((dump(uu, indLvl) for uu in undeclUsed), 
                                 0, sep="\n")

    #convert all statements in the body to verilog
    bodyLst = [dump(stm, indLvl) for stm in node.body]
    bodyStr = indListAsStr([stm for stm in bodyLst if stm != ''], 0, sep="\n\n")

    #convert parameters to verilog
    paramStr = ''
    if node.params:
        paramStr = indListAsStr((dump(p, 0, ctx=Ctx.io) for p in node.params), 
                                indLvl+1, sep=",\n")
        paramStr = ind('\n#(\n', indLvl) + paramStr + ')\n'

    #type declarations
    typeStr = ''
    if node.types:
        typeStr = '\n// types\n' + \
                  indListAsStr((dump(p, 0) for p in node.types), indLvl, sep=",\n") + \
                  ';\n'
    return instancesStr + \
           f'//'+ (76*'-') +'\n'+ \
           f'// {node.name}\n'+ \
           f'//'+ (76*'-') +'\n'+ \
           f'module {node.name} {paramStr}(\n{ioStr}\n);\n'+ \
           f'{typeStr}{undeclUsedStr}\n{regDeclStr}\n\n'+ \
           f'{bodyStr}\n\nendmodule\n'


#-----------------------------------------------------------------------------
# AstStatement derived
#-----------------------------------------------------------------------------
@dump.register(chipo.Clocked)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    events = [dump(node.clock, indLvl, ctx=Ctx.event)]
    if node.reset is not None:
        resetStr = dump(node.reset, indLvl, ctx=Ctx.event)
        if resetStr != "":
            events.append(resetStr)
    sensStr = " or ".join(events)
    bodyStr = dump(node.body, indLvl)
    alwaysStr = 'always_ff' if STYLE >= Style.sv2009 else 'always'
    return ind(f'{alwaysStr} @({sensStr}) ', indLvl) + bodyStr


@dump.register(chipo.Combo)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    bodyStr = dump(node.body, indLvl)
    alwaysStr = 'always_comb' if STYLE >= Style.sv2009 else 'always @(*)'
    return ind(f'{alwaysStr} ', indLvl) + bodyStr


@dump.register(chipo.Declare)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    #signal declarations are converted to reg/wires at Module
    return ""


@dump.register(chipo.InstanceBase)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    out  = ind(f"{node.modName()} ", indLvl)
    out += dumpParamPass(node, indLvl)
    out += f" {node._insName()} " + dumpIoPass(node, indLvl)
    return out


#-----------------------------------------------------------------------------
# AstProcStatement derived
#-----------------------------------------------------------------------------
@dump.register(chipo.Block)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    if len(node.stmts) == 1 and node.name is None:
        return "\n" + dump(node.stmts[0], indLvl+1)
    v = [dump(stm, indLvl+1) for stm in node.stmts]
    name = "" if node.name is None else " : " + node.name
    return f"begin{name}\n" + \
        indListAsStr(v, 0, sep='\n') + "\n" + ind("end", indLvl)


@dump.register(chipo.If)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    assert len(node.elifBlock)==len(node.elifCond), "Forgot cond on Elif ?"
    v = ind('if (' + dump(node.cond) + ')', indLvl) + ' ' + \
        dump(node.trueBlock,indLvl)
    for i, b in enumerate(node.elifBlock):
        v += '\n' + ind('else if (' + dump(node.elifCond[i]) + ')', 
            indLvl) + ' ' + dump(b, indLvl)
    if node.falseBlock is not None:
        v += "\n" + ind("else ", indLvl) + dump(node.falseBlock, indLvl)
    return v


@dump.register(chipo.While)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    return ind('while (' + dump(node.cond) + ')', indLvl) + ' ' + \
           dump(node.trueBlock, indLvl)


@dump.register(chipo.Switch)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    cases = indListAsStr([dump(i, indLvl+1) for i in node.cases], 0, sep='\n')
    defStr = ind("default: ", indLvl+1) + dump(node.default, indLvl+1) + '\n' \
             if node.default else ""
    return ind('case (' + dump(node.cond) + ')', indLvl) + '\n' + \
           cases + '\n' + defStr + ind('endcase', indLvl)


@dump.register(chipo.Switch.CaseClass)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    cases = ", ".join([dump(i) for i in node.conditionExpr])
    return ind(f'{cases} : ', indLvl) + dump(node.body, indLvl)


@dump.register(chipo.AssignBase)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    return ind(dump(node.lhs) + " " + node.oper + " " + \
           dump(node.expr, indLvl), indLvl) + ';'

#-----------------------------------------------------------------------------
# Expr
#-----------------------------------------------------------------------------
@dump.register(chipo.Expr)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    return paren(node, node.args[0]) + " " + node.op + " " + paren(node, node.args[1])


#-----------------------------------------------------------------------------
# Expr -> UnaryExpr
#-----------------------------------------------------------------------------
@dump.register(chipo.UnaryExpr)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    return node.op + paren(node, node.args[0]) 


@dump.register(chipo.CInt)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    prefix = '-' if node.signed and node.args[0] < 0 else ''
    sz = "'" if node.width is None else f"{node.width}'"
    sgn = 's' if node.signed else ''
    fmt = 'x' if node.base == 'h' else node.base
    num = f'{abs(node.args[0]):{fmt}}'
    if sz + sgn + node.base == "'d": # omit 'd prefix if alone
        return prefix + num
    return prefix + sz + sgn + node.base + num


@dump.register(chipo.CEnu)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    return node.args[0]


@dump.register(chipo.Parameter)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    v = f'{node.name}'
    if ctx == Ctx.io:
        v = f"parameter {v} = {dump(node.args[0])}"
    return v


@dump.register(chipo.Assignable)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    v = f'{node.name}'
    if ctx == Ctx.io:
        v = f"//Signal {node.name} {dump(node.args[0], ctx=ctx)}"
    return v


def dumpPort(node, indLvl=0, *, ctx:Ctx = Ctx.default):

    def dumpReg(node):
        if node.kind == "Out" and node.isReg:
            if STYLE >= Style.sv2005l:
                return ' logic'
            return ' reg'
        return ''

    if ctx == Ctx.io:
        typ = node.args[0]
        direc = 'input' if node.kind=='In' else 'output'
        typStr = direc + dumpReg(node) + dumpSigned(typ)
        if typ.width != 1:
            return ind(f"{typStr} [{dumpMsb(typ)}:0] {node.name}", indLvl)
        return ind(f"{typStr} {node.name}", indLvl)
    return f'{node.name}'


@dump.register(chipo.Port)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    return dumpPort(node, indLvl, ctx=ctx)


@dump.register(chipo.Clock)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    if ctx == Ctx.io:
        return dumpPort(node, indLvl, ctx=ctx)
    if ctx == Ctx.event:
        edge = 'posedge' if node.posedge else 'negedge'
        return edge + " " + node.name
    return node.name


@dump.register(chipo.Reset)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):

    def resetEvent(node):
        return "negedge" if node.asyn and node.lowTrue else \
               "posedge" if node.asyn and not node.lowTrue else "" 

    if ctx == Ctx.io:
        return dumpPort(node, indLvl, ctx=ctx)
    if ctx == Ctx.event:
        if node.asyn:
            return resetEvent(node) + " " + node.name
        return ""
    return node.name


#-----------------------------------------------------------------------------
# Expr -> MultiExpr
#-----------------------------------------------------------------------------
@dump.register(chipo.BitExtract)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    lsbv = '' if node.args[2] is None else ':' + dump(node.args[2])
    return paren(node, node.args[0]) + '['+ dump(node.args[1]) + lsbv +']'


@dump.register(chipo.Concat)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    return '{\n'+ indListAsStr([paren(node, x) for x in node.all()], indLvl+1) +'}'


@dump.register(chipo.IfCond)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    return paren(node, node.args[0]) + ' ? ' + dump(node.args[1]) + \
                                       ' : ' + dump(node.args[2]) 


@dump.register(chipo.ExprReduce)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    return node.op + paren(node, node.args[0]) 


#-----------------------------------------------------------------------------
# 
#-----------------------------------------------------------------------------
@dump.register(chipo.BitVec)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    v = f'{node.name}'
    if ctx == Ctx.io:
        if isinstance(node.width, int) and node.width != 1 or \
           isinstance(node.width, chipo.Expr):
            v += f"[{dumpMsb(node)}:0]"
    return v

#TODO Agreg, Arr, Enu

#-----------------------------------------------------------------------------
# Temporal during Module vlog generation
#-----------------------------------------------------------------------------
@dump.register(Logic)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    typ = 'logic' + dumpSigned(node)
    if node.width != 1:
        return ind(f"{typ} [{dumpMsb(node)}:0] {node.name};", indLvl)
    return ind(f"{typ} {node.name};", indLvl)


@dump.register(Reg)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    typ = 'reg' + dumpSigned(node)
    if node.width != 1:
        return ind(f"{typ} [{dumpMsb(node)}:0] {node.name};", indLvl)
    return ind(f"{typ} {node.name};", indLvl)


@dump.register(Wire)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    typ = 'wire' + dumpSigned(node)
    if node.width != 1:
        return ind(f"{typ} [{dumpMsb(node)}:0] {node.name}; // auto", 
                   indLvl)
    return ind(f"{typ} {node.name}; // auto", indLvl)

#-----------------------------------------------------------------------------
# Type dumping
#-----------------------------------------------------------------------------
@singledispatch
def dumpType(typ, indLvl=0):
    assert False, f"unhandled dumpType case. typ={typ}"


@dump.register(chipo.Enu)
def _(typ, indLvl=0):
    if STYLE >= Style.sv2012:
        enuLst = [f"{k}={v}" for k,v in typ.dict().items()]
        enuStr = ", ".join(enuLst)
        return ind(f"typedef enum {{{enuStr}}} {typ.name}", indLvl)
    else:
        enuLst = [f"localparam {k}={v}" for k,v in typ.dict().items()]
        return indListAsStr(enuLst, indLvl, ";\n")


@runtime_validation
def dumpFieldDecl(fld:chipo.Field):
    return f"{fld.typ.name} {', '.join(fld.names)}"


@dump.register(chipo.Rec)
def _(typ, indLvl=0):
    if STYLE >= Style.sv2012:
        recStr = ind("typedef struct {\n", indLvl)
        for fld in typ.body:
            recStr += ind(dumpFieldDecl(fld) + ";\n", indLvl+1)
        recStr += ind("}", indLvl)
        return recStr
    else:
        raise NotImplementedError

