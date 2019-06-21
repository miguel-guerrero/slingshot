#!/usr/bin/env python3
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
from chipo import *
import g2p as g

#-------------------------------------------------------------------------------
# Field base and derived classes
#-------------------------------------------------------------------------------
class Field:
    def __init__(self, w, name, typ, reset):
        if isinstance(w, Signal):
            self.w = w.width().Eval() if isinstance(w.width(), Expr) else w.width()
            self.name = w.name if name is None else name
            self.reset = w.default if reset is None else reset
        else:
            self.w = w
            self.name = name
            self.reset = 0 if reset is None else reset
        self.typ = typ

class RW(Field):
    def __init__(self, w, name=None, reset=None): 
        super().__init__(w, name, 'rw', reset)

class RO(Field):
    def __init__(self, w, name=None, reset=None): 
        super().__init__(w, name, 'ro', reset)

class Const(Field):
    def __init__(self, w, name=None, *, reset=None): 
        super().__init__(w, name, 'c', reset)

class Rsrv(Field):
    def __init__(self, w, name=None): 
        super().__init__(w, name, 'c', 0)

#-------------------------------------------------------------------------------
# Register class
#-------------------------------------------------------------------------------
class Reg:
    def __init__(self, *fields, name=None, maxw=32):
        if name is None and len(fields)==1:
            self.name = fields[0].name
            fields[0].name = 'val'
        else:
            self.name = name
        self.fields = list(fields)

    def __iadd__(self, x):
        self.fields.append(x)
        return self

    def size(self):
        return sum(f.w for f in self.fields)

#-------------------------------------------------------------------------------
# Register block class
#-------------------------------------------------------------------------------
class RegBlock:

    def __init__(self, *regs, name, baseAddr=0, addrInc=4):
        self.regs = list(regs)
        self.name = name
        self.baseAddr = baseAddr
        self.addrInc = addrInc

    def __iadd__(self, x):
        self.regs.append(x)
        return self

    def bytes(self):
        return self.addrInc

    def breakUp(self):
        maxW = self.addrInc*8
        maskW = (1 << maxW) - 1

        def brk(inReg):

            newFieldAssoc = []
            newRegs = []
            cnt = 0
            cumSize = 0
            fcnt = 0
            reg = Reg(name=f'{inReg.name}_r{cnt}')

            def pushReg(reg):
                nonlocal newRegs, cnt, cumSize
                assert len(reg.fields) > 0
                newRegs.append(reg)
                cnt += 1
                cumSize = 0
                return Reg(name=f'{inReg.name}_r{cnt}')

            def pushField(reg, f):
                if f.w > maxW - reg.size():
                    reg = pushReg(reg)
                reg += f
                return reg

            for f in inReg.fields:
                if f.w >= maxW:
                    assert f.reset <= maskW, f'cannot split large field with reset {f.reset}'
                    if reg.size() > 0: # flush prev reg
                        reg = pushReg(reg)
                    newFields = []
                    remW = f.w
                    remReset = f.reset
                    while remW > 0:
                        newF = Field(w=min(maxW, remW), name=f'{f.name}_f{fcnt}',
                                     typ=f.typ, reset=remReset & maskW)
                        reg = pushField(reg, newF)
                        newFields.append((reg, newF))
                        fcnt += 1
                        remW -= newF.w
                        remReset >>= newF.w
                else:
                    reg = pushField(reg, f)

                if len(newFields) > 0:
                    newFieldAssoc.append((inReg, f, reversed(newFields)))

            if reg.size() > 0: #flush last reg
                pushReg(reg)

            return newFieldAssoc, newRegs

        #body of breakUp
        newRegs = []
        brokenLst = []
        for reg in self.regs:
            if reg.size() > maxW:
                fields, regs = brk(reg)
                brokenLst += fields
            else:
                regs = [reg]
            newRegs += regs
        self.regs = newRegs
        return brokenLst

#-----------------------------------------------------------------------------
# Separating dumpers from main classes to leave main classes clean
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Conversion to RALF
#-----------------------------------------------------------------------------
def toRalf(rb, ind='\t'):
    def dumpReg(reg, addr):
        def dumpField(f, bitOffs):
            s =  f"{ind*2}field {f.name} @'h{bitOffs:0x} {{\n"
            s += f"{ind*3}bits {f.w};\n"
            s += f"{ind*3}access {f.typ};\n"
            s += f"{ind*3}reset 'h{f.reset:0x};\n"
            s += f'{ind*2}}}\n'
            return s

        s = f"{ind}register {reg.name} @'h{addr:0x} {{\n"
        bitOffs = 0
        for f in reg.fields:
            s += dumpField(f, bitOffs)
            bitOffs += f.w
        s += f"{ind}}}\n"
        return s

    assert isinstance(rb, RegBlock)
    s =  f"block {rb.name} {{\n"
    s += f"{ind}bytes {rb.bytes()};\n"
    addr = rb.baseAddr
    for reg in rb.regs:
        s += dumpReg(reg, addr)
        addr += rb.addrInc
    s += "}\n"
    return s

#-----------------------------------------------------------------------------
# Conversion to gen_csrs XML
#-----------------------------------------------------------------------------
def toGenCsrsXML(rb, ind='\t'):
    def dumpReg(reg, addr):
        def dumpField(f, bitOffs):
            s = f'{ind*3}<FIELD NAME="{f.name}" BIT_RANGE="{f.w+bitOffs-1}:{bitOffs}" '
            if f.typ == 'rw':
                s +=  f'HOST_ATTR="RW" PE_ATTR="R" IO_ATTR="out" RESET="0x{f.reset:0x}"'
            elif f.typ == 'ro':
                s +=  f'HOST_ATTR="R" PE_ATTR="RW" IO_ATTR="in" RESET="0x{f.reset:0x}"'
            elif f.typ == 'c':
                s +=  f'HOST_ATTR="RC" PE_ATTR="R" CONST="0x{f.reset:0x}"'
            else:
                assert False, f'invalid field type {f.typ}'
            s += f' DOC=""/>\n'
            return s

        s = f'{ind*2}<REG NAME="{reg.name}" OFFS="0x{addr:0x}" DOC="{reg.name} Register">\n'
        bitOffs = 0
        for f in reg.fields:
            s += dumpField(f, bitOffs)
            bitOffs += f.w
        s += f'{ind*2}</REG>\n'
        return s

    assert isinstance(rb, RegBlock)
    s =  f'<!DOCTYPE spec SYSTEM "csr_schema.xsd">\n'
    s += f'<REGISTERS>\n'
    s += f'{ind}<DEFAULTS PRI="HOST" CLOCK="PCLK" APB_ADDR_W="32" BASE="{rb.baseAddr}"'
    s += f' PREFIX_CSRS="" MODULE="{rb.name}" APB_V3="1"/>\n'
    s += f'{ind}<REG_ARRAY>\n'
    addr = rb.baseAddr
    for reg in rb.regs:
        s += dumpReg(reg, addr)
        addr += rb.addrInc
    s += f"{ind}</REG_ARRAY>\n"
    s += f"</REGISTERS>"
    return s

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def genCsrs(rb, clk, rst_n):
    import subprocess as sp

    modName = rb.name
    #break-up large fields if needed
    brokenLst = rb.breakUp()

    #dump registers as XML for gen_csrs
    xmlFileName = modName+'.xml'
    with open(xmlFileName, 'w') as f:
        f.write(toGenCsrsXML(rb))

    #invoke gen_csrs
    res = sp.run(['./gen_csrs.pl', xmlFileName
                  , '-out', modName+'.v'
                  , '-g2p', modName+'.ios'
                  , '-vlogsep', '_'
                  ], input=b'', stdout=sp.PIPE, stderr=sp.PIPE)

    if res.returncode != 0:
        import sys
        print("-"*80,                     file=sys.stderr)
        print(res.stdout.decode('utf-8'), file=sys.stderr)
        print("-"*80,                     file=sys.stderr)
        print(res.stderr.decode('utf-8'), file=sys.stderr)
        print("-"*80,                     file=sys.stderr)
        raise RuntimeError("Error executing gen_csrs.pl")

    #read back IOs in our format
    with open(modName+'.ios') as f:
        s=f.read()
    IOs=eval(f"[{s}]")

    #generate a g2p module (IOs known but guts unknown)
    csrMod = g.Module(modName, IOs=IOs)

    #generate a portMap dictionary
    pm = {'PCLK':clk, 'PRESETN':rst_n}
    for io in csrMod.getIOs():
        if io.name not in pm.keys():
            topName = io.name[:-4] if io.name.endswith('_val') else io.name
            pm[io.name] = Signal(io.width(), name=topName)

    #create a wrapper of the actually generated csr module with propper 
    #signal renaming and broken field concatenation
    m = Module(f"{modName}_wrap")

    for orgReg, orgF, brkLst in brokenLst:
        fldSig = Signal(orgF.w, name=f'{orgReg.name}_{orgF.name}')
        partFields = [Signal(f.w, name=f'{r.name}_{f.name}') for r, f in brkLst]
        if isinstance(orgF, RW): #output
            m += Assign(fldSig, Concat(*partFields))
        else: #input
            m += Assign(Concat(*partFields), fldSig)

    m += InstanceG2p(csrMod, ParamMap(), pm)

    return m.autoGen()
