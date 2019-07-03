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
from functools import singledispatch
from collections import namedtuple

import chipo
from helper import error

try:
    from enforce import runtime_validation, config
    config({'mode':'covariant'}) # base class type covers type of subclasses
except:
    runtime_validation = lambda x : x

class Ctx(Enum):
    default=0
    io=1
    event=2
    compact=3
    useBlocking=3
    module=4

Style = namedtuple('Style', ['useLogic', 'useAlwaysFF', 'useAlwaysComb', 
    'useAgreg', 'useEnum', 'indent'])

STYLE = Style(useLogic=False, useAlwaysFF=False, useAlwaysComb=False,
    useAgreg=False, useEnum=False, indent='    ')

def setStyle(**kwargs):
    global STYLE
    d = STYLE._asdict()
    for k, v in kwargs.items():
        d[k] = v
    STYLE = Style(**d)

@runtime_validation
def ind(s:str, n:int) -> str:
    return (STYLE.indent*n) + s

def indList(lst:list, n:int) -> list:
    return [ind(item, n) for item in lst]

def indListAsStr(lst:list, n:int, sep=',\n') -> str:
    return sep.join(indList(lst, n))


# convert expr to vlog and parenthesize if expr operator is lower pri than 
# node.op/pri
def paren(node, expr, ctx=Ctx.default):
    v = dump(expr, ctx=ctx)
    forceParen = False #for debug
    if isinstance(expr, chipo.Expr) and (expr.pri < node.pri or forceParen):
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
    width = node.width
    if isinstance(width, chipo.Param):
        return f"{width.name}-1"
    if isinstance(width, chipo.Expr):
        return dump(chipo.simplify(width-1), ctx=Ctx.compact)
    return f"{width-1}"


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
    if STYLE.useLogic:
        return [Logic(sig) for sig in chipo.sortedAsList(x)]
    return [Reg(sig) for sig in chipo.sortedAsList(x)]
    

def annotateUses(x):
    if STYLE.useLogic:
        return [Logic(sig) for sig in chipo.sortedAsList(x)]
    return [Wire(sig) for sig in chipo.sortedAsList(x)]


#-----------------------------------------------------------------------------
# why are we doing this instead of just simple inheritance? to keep
# several code dumpers separate and avoid cluttering the original classes
#-----------------------------------------------------------------------------

@singledispatch
def dump(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    if node == ...:
        return ind('`WFE', indLvl)
    if isinstance(node, chipo.AstStatement):
        assert False, error("undefined dump(AstStatement)", node) 
    elif isinstance(node, chipo.AstProcStatement):
        assert False, error("undefined dump(AstProcStatement)", node)
    elif isinstance(node, chipo.AstNode):
        assert False, error("undefined dump(AstNode)", node)
    elif isinstance(node, chipo.Type):
        assert False, error("undefined dump(Type)", node)
    assert False, error("unhandled dump case", node)


#@dump.register(Ellipsis)
#def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
#    return "WFE"    

#-----------------------------------------------------------------------------
# AstNode derived
#-----------------------------------------------------------------------------
@dump.register(chipo.Comm)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    vlst = [f"// {cmnt}" for cmnt in node.lines]
    return indListAsStr(vlst, indLvl, sep='\n')


@dump.register(chipo.Module)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    externalStr = ''
    if recursive:
        doneSet = set()
        for i in node.getInstances():
            if i.module() is None: #legacy instance
                externalStr += f"// INFO: {i} is external\n"
            elif i.module().getName() not in doneSet:
                doneSet.add(i.module().getName())
                for modName, modStr in i.module().vlogIter(indLvl):
                    yield modName, modStr
    
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
    bodyLst = [dump(stm, indLvl, ctx=Ctx.module) for stm in node.body]
    bodyStr = indListAsStr([stm for stm in bodyLst if stm != ''], 0, sep="\n")

    #convert parameters to verilog
    paramStr = ''
    if node.params:
        paramStr = indListAsStr((dump(p, ctx=Ctx.io) for p in node.params), 
                                indLvl+1, sep=",\n")
        paramStr = ind('\n#(\n', indLvl) + paramStr + ')\n'

    #type declarations
    typeStr = ''
    typeStrLst = [x for x in (dump(p) for p in node.types) if x != ""]
    if len(typeStrLst) > 0:
        typeStr = '\n// types\n' + \
            indListAsStr(typeStrLst, indLvl, sep=",\n") + ';\n'

    modStr = externalStr + \
           f'//'+ (76*'-') +'\n'+ \
           f'// {node.name}\n'+ \
           f'//'+ (76*'-') +'\n'+ \
           f'module {node.name} {paramStr}(\n{ioStr}\n);\n'+ \
           f'{typeStr}{undeclUsedStr}\n{regDeclStr}\n\n'+ \
           f'{bodyStr}\n\nendmodule\n'
    yield node.name, modStr


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
    alwaysStr = 'always_ff' if STYLE.useAlwaysFF else 'always'
    prefix = ''
    if node.hasWfe:
        resetAct = dump(node.reset.onExpr())
        prefix = f"`define WFE begin @({sensStr}); if ({resetAct}) disable _loop; end;\n"
    return prefix+'\n'+ind(f'{alwaysStr} @({sensStr}) ', indLvl) + bodyStr + '\n'


def isSafeToUseBlockingAssig(node):
    assig = node.assigned()
    used = node.used()
    return assig.intersection(used) == set()


@dump.register(chipo.Combo)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    if STYLE.useLogic and len(node.body) == 1:
        stm = node.asList()[0]
        if isinstance(stm, chipo.SigAssign):
            assign = dump(stm, indLvl, ctx=Ctx.useBlocking)
            return ind(f"assign {assign}", indLvl)
    if isSafeToUseBlockingAssig(node):
        bodyStr = dump(node.body, indLvl, ctx=Ctx.useBlocking)
    else:
        bodyStr = dump(node.body, indLvl)
    alwaysStr = 'always_comb' if STYLE.useAlwaysComb else 'always @(*)'
    return '\n'+ind(f'{alwaysStr} ', indLvl) + bodyStr + '\n'


@dump.register(chipo.Declare)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    #signal declarations are converted to reg/wires at Module
    return ""


@dump.register(chipo.InstanceBase)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    out  = '\n' + ind(f"{node.modName()} ", indLvl)
    out += dumpParamPass(node, indLvl)
    out += f" {node._insName()} " + dumpIoPass(node, indLvl)
    return out


#-----------------------------------------------------------------------------
# AstProcStatement derived
#-----------------------------------------------------------------------------
@dump.register(chipo.Block)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    v = [dump(stm, indLvl+1, ctx=ctx) for stm in node.stmts]
    name = "" if node.name is None else " : " + node.name
    return f"begin{name}\n" + \
        indListAsStr(v, 0, sep='\n') + "\n" + ind("end", indLvl)


@dump.register(chipo.If)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    if len(node.elifBlock)!=len(node.elifCond):
        raise TypeError(error("In If/Elif/Else structure, at least one Elif has no condition", node))
    v = ind('if (' + dump(node.cond, ctx=ctx) + ')', indLvl) + ' ' + \
        dump(node.trueBlock, indLvl, ctx=ctx)
    for i, b in enumerate(node.elifBlock):
        v += '\n' + ind('else if (' + dump(node.elifCond[i], ctx=ctx) + ')', 
            indLvl) + ' ' + dump(b, indLvl, ctx=ctx)
    if node.falseBlock.asList():
        v += "\n" + ind("else ", indLvl) + dump(node.falseBlock, indLvl, ctx=ctx)
    return v


@dump.register(chipo.While)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    return ind('while (' + dump(node.cond, ctx=ctx) + ')', indLvl) + ' ' + \
           dump(node.trueBlock, indLvl, ctx=ctx)


@dump.register(chipo.Switch)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    cases = indListAsStr([dump(i, indLvl+1, ctx=ctx) for i in node.cases], 0, sep='\n')
    defStr = ind("default: ", indLvl+1) + dump(node.default, indLvl+1, ctx=ctx) + '\n' \
             if node.default else ""
    return ind('case (' + dump(node.cond, ctx=ctx) + ')', indLvl) + '\n' + \
           cases + '\n' + defStr + ind('endcase', indLvl)


@dump.register(chipo.Switch.CaseClass)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    cases = ", ".join([dump(i, ctx=ctx) for i in node.conditionExpr])
    return ind(f'{cases} : ', indLvl) + dump(node.body, indLvl, ctx=ctx)


@dump.register(chipo.AssignBase)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    if node.oper == '<=' and ctx==Ctx.module:
        assign = dump(node, indLvl, ctx=Ctx.useBlocking)
        if STYLE.useLogic:
            return ind(f"assign {assign}", indLvl)
        else:
            return ind(f"always @(*) {assign}", indLvl)
    else:
        oper = '=' if ctx == Ctx.useBlocking else node.oper
        return ind(dump(node.lhs, ctx=ctx) + " " + oper + " " + \
               dump(node.expr, indLvl), indLvl) + ';'

#-----------------------------------------------------------------------------
# Expr
#-----------------------------------------------------------------------------
@dump.register(chipo.Expr)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    sep = "" if ctx==Ctx.compact else " "
    return paren(node, node.args[0], ctx) + sep + node.op + sep + \
           paren(node, node.args[1], ctx)


#-----------------------------------------------------------------------------
# Expr -> UnaryExpr
#-----------------------------------------------------------------------------
@dump.register(chipo.UnaryExpr)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    return node.op + paren(node, node.args[0], ctx) 


@dump.register(chipo.CInt)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    width = node.width
    prefix = '-' if node.signed and node.args[0] < 0 else ''
    sz = "'" if width is None else f"{width}'"
    sgn = 's' if node.signed else ''
    fmt = 'x' if node.base == 'h' else node.base
    num = f'{abs(node.args[0]):{fmt}}'
    if sz + sgn + node.base == "'d": # omit 'd prefix if alone
        return prefix + num
    return prefix + sz + sgn + node.base + num


@dump.register(chipo.CEnu)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    return node.args[0]


def keyPath(key, parent):
    if type(parent)==chipo.DotExpr:
        return keyPath(parent.args[2], parent.args[1]) + "." + key
    return key


@dump.register(chipo.DotExpr)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):

    typ, parent, key = node.args
    parentTyp = parent.args[0]
    keyName = keyPath(key, parent)

    if STYLE.useAgreg:
        return f"{node.root.name}.{keyName}"
    else:
        lsb = node.offset(key)
        msb = parentTyp.fldWidth(key) + lsb - 1

        lsbStr = dump(chipo.simplify(lsb), ctx=Ctx.compact)
        msbStr = dump(chipo.simplify(msb), ctx=Ctx.compact)

        suffix = '' if msbStr == lsbStr else f':{lsbStr}'
        return f"{node.root.name}/*.{keyName}*/[{msbStr}{suffix}]"


@dump.register(chipo.Param)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    v = f'{node.name}'
    if ctx == Ctx.io:
        v = f"parameter {v} = {dump(node.args[0])}"
    return v


@dump.register(chipo.Assignable)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    v = f'{node.name}'
    if ctx == Ctx.io:
        v = f"//Signal name={node.name} typ={node.args[0]}"
        assert False, f"Only derived from Assignable are expected to be vlog.dump'ed, got {node}"
    return v


def dumpPort(node, indLvl=0, *, ctx:Ctx = Ctx.default):

    def dumpReg(node):
        if node.kind == "Out" and node.isReg:
            if STYLE.useLogic:
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
    typ, msb, lsb = node.args
    if isinstance(typ, chipo.DotExpr):
        _, parent, key = typ.args
        offs = typ.offset(key)

        msbStr = dump(chipo.simplify(msb+offs), ctx=Ctx.compact)
        keyName = keyPath(key, parent)

        suff = ":"+dump(chipo.simplify(lsb+offs), ctx=Ctx.compact) if lsb else ""
        suffC= ":"+dump(lsb) if lsb else ""
        return f"{typ.root.name}/*.{keyName}[{dump(msb)}{suffC}]*/[{msbStr}{suff}]"
    else:
        msbStr = dump(chipo.simplify(msb), ctx=Ctx.compact)
        suff = ":"+dump(chipo.simplify(lsb), ctx=Ctx.compact) if lsb else ""
        return paren(node, typ) + f"[{msbStr}{suff}]"


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
        width = node.width
        if isinstance(width, int) and width != 1 or \
           isinstance(width, chipo.Expr):
            v += f"[{dumpMsb(node)}:0]"
    return v


@dump.register(int)
def _(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):
    return f"{node}"


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
    if STYLE.useEnum:
        enuLst = [f"{k}={v}" for k,v in typ.dict().items()]
        enuStr = ", ".join(enuLst)
        return ind(f"typedef enum {{{enuStr}}} {typ.name}", indLvl)
    else:
        enuLst = [f"localparam {k}={v}" for k,v in typ.dict().items()]
        return indListAsStr(enuLst, indLvl, ";\n")


@runtime_validation
def dumpFieldDecl(fld:chipo.Field, indLvl):
    namesStr = ', '.join(fld.names)
    typeStr = ind(fld.typ.name, indLvl+1)
    if type(fld.typ) == chipo.BitVec:
        if fld.typ.name == 'self':
            width = fld.typ.width
            v = 'logic'
            if isinstance(width, int) and width != 1 or \
               isinstance(width, chipo.Expr):
                v = f"logic [{dumpMsb(fld.typ)}:0]"
            typeStr = ind(v, indLvl+1)

    return typeStr + " " + namesStr


@dump.register(chipo.Rec)
def _(typ, indLvl=0):
    if STYLE.useAgreg:
        recStr = ind("typedef packed struct {\n", indLvl)
        for fld in typ.body:
            recStr += dumpFieldDecl(fld, indLvl) + ";\n"
        recStr += ind("} " f"{typ.name}", indLvl)
        return recStr
    else:
        return ""


@dump.register(chipo.Union)
def _(typ, indLvl=0):
    if STYLE.useAgreg:
        recStr = ind("typedef packed union {\n", indLvl)
        for fld in typ.body:
            recStr += dumpFieldDecl(fld, indLvl) + ";\n"
        recStr += ind("} " f"{typ.name}", indLvl)
        return recStr
    else:
        return ""


