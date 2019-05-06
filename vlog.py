import chipo
from enum import Enum, IntEnum

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
def setIndent(x:str):
    global INDENT
    INDENT = x

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

def dumpSigned(node):
    if node.signed:
        return ' signed'
    return ''

def dumpReg(node):
    if node.kind == "Output" and node.isReg:
        if STYLE >= Style.sv2005l:
            return ' logic'
        return ' reg'
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
    return f"{node.getMsb()}"

def dumpIo(node, indLvl, *, ctx:Ctx = Ctx.default):
    if ctx == Ctx.io:
        typ = node.kind.lower() + dumpReg(node) + dumpSigned(node)
        if node.width != 1:
            return ind(f"{typ} [{dumpMsb(node)}:0] {node.name}", indLvl)
        return ind(f"{typ} {node.name}", indLvl)
    return f'{node.name}'


#has only temporary life while converting to vlog
class Reg(chipo.BitVec):
    def __init__(self, sig):
        super().__init__(width=sig.width, name=sig.name, 
                         default=sig.default, signed=sig.signed)
        self.typ = 'Reg'

    def __repr__(self):
        raise NotImplementedError

#has only temporary life while converting to vlog
class Wire(chipo.BitVec):
    def __init__(self, sig):
        super().__init__(width=sig.width, name=sig.name, 
                         default=sig.default, signed=sig.signed)
        self.typ = 'Wire'

    def __repr__(self):
        raise NotImplementedError

class Logic(chipo.BitVec):
    def __init__(self, sig):
        super().__init__(width=sig.width, name=sig.name, 
                         default=sig.default, signed=sig.signed)
        self.typ = 'Logic'

    def __repr__(self):
        raise NotImplementedError

def annotateRegs(x):
    if STYLE >= Style.sv2005l:
        return [Logic(sig) for sig in chipo.sortedAsList(x)]
    return [Reg(sig) for sig in chipo.sortedAsList(x)]
    
def annotateUses(x):
    if STYLE >= Style.sv2005l:
        return [Logic(sig) for sig in chipo.sortedAsList(x)]
    return [Wire(sig) for sig in chipo.sortedAsList(x)]

def dumpModule(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):

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
        if io in sigAsgn:
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
    if node.params != []:
        paramStr = indListAsStr((dump(p, 0, ctx=Ctx.io) for p in node.params), 
                                indLvl+1, sep=",\n")
        paramStr = ind('\n#(\n', indLvl) + paramStr + ')\n'

    return instancesStr + \
           f'//'+ (76*'-') +'\n'+ \
           f'// {node.name}\n'+ \
           f'//'+ (76*'-') +'\n'+ \
           f'module {node.name} {paramStr}(\n{ioStr}\n);\n'+ \
           f'{undeclUsedStr}\n{regDeclStr}\n\n'+ \
           f'{bodyStr}\n\nendmodule\n'

#-----------------------------------------------------------------------------
# why are we doing this instead of just simple inheritance? to keep
# several code dumpers separate and avoid cluttering the original classes
#-----------------------------------------------------------------------------
def dump(node, indLvl=0, *, ctx:Ctx = Ctx.default, recursive=False):

    if isinstance(node, chipo.Comment):
        vlst = [f"// {cmnt}" for cmnt in node.lines]
        return indListAsStr(vlst, indLvl, sep='\n')

    elif isinstance(node, chipo.AstStatement):

        if isinstance(node, chipo.Block):
            if len(node.stmts) == 1 and node.name is None:
                return "\n" + dump(node.stmts[0], indLvl+1)
            v = [dump(stm, indLvl+1) for stm in node.stmts]
            name = "" if node.name is None else " : " + node.name
            return f"begin{name}\n" + \
                indListAsStr(v, 0, sep='\n') + "\n" + ind("end", indLvl)

        elif isinstance(node, chipo.If):
            assert len(node.elifBlock)==len(node.elifCond), "Forgot cond on Elif ?"
            v = ind('if (' + dump(node.cond) + ')', indLvl) + ' ' + \
                dump(node.trueBlock,indLvl)
            for i, b in enumerate(node.elifBlock):
                v += '\n' + ind('else if (' + dump(node.elifCond[i]) + ')', 
                    indLvl) + ' ' + dump(b, indLvl)
            if node.falseBlock is not None:
                v += "\n" + ind("else ", indLvl) + dump(node.falseBlock, indLvl)
            return v

        elif isinstance(node, chipo.While):
            return ind('while (' + dump(node.cond) + ')', indLvl) + ' ' + \
                   dump(node.trueBlock, indLvl)

        elif isinstance(node, chipo.Switch):
            cases = indListAsStr([dump(i, indLvl+1) for i in node.cases], 0, sep='\n')
            return ind('case (' + dump(node.cond) + ')', indLvl) + '\n' + \
                   cases + '\n' + ind('endcase', indLvl)

        elif isinstance(node, chipo.Switch.CaseClass):
            cases = ", ".join([dump(i) for i in node.conditionExpr])
            return ind(f'{cases} : ', indLvl) + dump(node.body, indLvl)

        elif isinstance(node, chipo.AssignBase):
            return ind(dump(node.lhs) + " " + node.vlogOper + " " + \
                   dump(node.expr, indLvl), indLvl) + ';'

        assert False, f"undefined dump(AstStatement) for {node}"

    elif isinstance(node, chipo.CInt):
        prefix = '-' if node.signed and node.val < 0 else ''
        sz = "'" if node.width is None else f"{node.width}'"
        sgn = 's' if node.signed else ''
        fmt = 'x' if node.base == 'h' else node.base
        num = f'{abs(node.val):{fmt}}'
        if sz + sgn + node.base == "'d": # omit 'd prefix if alone
            return prefix + num
        return prefix + sz + sgn + node.base + num

    elif isinstance(node, chipo.Expr):

        if isinstance(node, chipo.UnaryExpr):
            return node.op + paren(node, node.rhs) 

        elif isinstance(node, chipo.NoEvalExpr):

            if isinstance(node, chipo.Concat):
                return '{\n'+ indListAsStr([paren(node, x) for x in node.all_], indLvl+1) +'}'

            elif isinstance(node, chipo.IfCond):
                return paren(node, node.cond) + ' ? ' + dump(node.ift) + \
                                                ' : ' + dump(node.iff) 
            elif isinstance(node, chipo.BitExtract):
                lsbv = '' if node.rhs2 is None else ':' + dump(node.rhs2)
                return paren(node, node.lhs) + '['+ dump(node.rhs) + lsbv +']'

            elif isinstance(node, chipo.ExprReduce):
                return node.op + paren(node, node.rhs) 

            elif isinstance(node, chipo.BitVec):

                if isinstance(node, chipo.Io):
                    if isinstance(node, chipo.Clock):
                        if ctx == Ctx.io:
                            return dumpIo(node, indLvl, ctx=ctx)
                        if ctx == Ctx.event:
                            return node.edge() + " " + node.name
                        return node.name

                    elif isinstance(node, chipo.Reset):
                        if ctx == Ctx.io:
                            return dumpIo(node, indLvl, ctx=ctx)
                        if ctx == Ctx.event:
                            if node.asyn:
                                return node.edge() + " " + node.name
                            return ""
                        return node.name

                    return dumpIo(node, indLvl, ctx=ctx)

                elif isinstance(node, Logic):
                    typ = 'logic' + dumpSigned(node)
                    if node.width != 1:
                        return ind(f"{typ} [{dumpMsb(node)}:0] {node.name};", indLvl)
                    return ind(f"{typ} {node.name};", indLvl)

                elif isinstance(node, Reg):
                    typ = 'reg' + dumpSigned(node)
                    if node.width != 1:
                        return ind(f"{typ} [{dumpMsb(node)}:0] {node.name};", indLvl)
                    return ind(f"{typ} {node.name};", indLvl)

                elif isinstance(node, Wire):
                    typ = 'wire' + dumpSigned(node)
                    if node.width != 1:
                        return ind(f"{typ} [{dumpMsb(node)}:0] {node.name}; // auto", 
                                   indLvl)
                    return ind(f"{typ} {node.name}; // auto", indLvl)

                #BitVec
                v = f'{node.name}'
                if ctx == Ctx.io:
                    if isinstance(node.width, int) and node.width != 1 or \
                       isinstance(node.width, chipo.Expr):
                        v += f"[{dumpMsb(node)}:0]"
                return v

            return node.op + paren(node, node.rhs) 

        elif isinstance(node, chipo.Parameter):
            v = f'{node.name}'
            if ctx == Ctx.io:
                v = f"parameter {v} = {dump(node.default)}"
            return v

        return paren(node, node.lhs) + " " + node.op + " " + paren(node, node.rhs)

    elif isinstance(node, chipo.Declare):
        #signal declarations are converted to reg/wires at Module
        return ""

    elif isinstance(node, chipo.Module):
        return dumpModule(node, indLvl, recursive=recursive)

    elif isinstance(node, chipo.Clocked):
        events = [dump(node.clock, indLvl, ctx=Ctx.event)]
        if node.reset is not None:
            resetStr = dump(node.reset, indLvl, ctx=Ctx.event)
            if resetStr != "":
                events.append(resetStr)
        sensStr = " or ".join(events)
        bodyStr = dump(node.body, indLvl)
        alwaysStr = 'always_ff' if STYLE >= Style.sv2009 else 'always'
        return ind(f'{alwaysStr} @({sensStr}) ', indLvl) + bodyStr

    elif isinstance(node, chipo.Combo):
        bodyStr = dump(node.body, indLvl)
        alwaysStr = 'always_comb' if STYLE >= Style.sv2009 else 'always @(*)'
        return ind(f'{alwaysStr} ', indLvl) + bodyStr

    elif isinstance(node, chipo.InstanceBase):
        out  = ind(f"{node.modName()} ", indLvl)
        out += dumpParamPass(node, indLvl)
        out += f" {node._insName()} " + dumpIoPass(node, indLvl)
        return out

    assert False, f"unhandled dump case. node={node}"
