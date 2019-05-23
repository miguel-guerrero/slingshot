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

from chipo import BinExpr, CInt, isInt, intVal, simplify


def isIntVal(obj, x:int) -> bool:
    return isInt(obj) and intVal(obj)==x


def simplifyPattern1(op, l, r): # (+ E (* N E)) --> (* N+1 E)
    assert op == '+'
    if isinstance(r, BinExpr) and r.op=='*':
        if isinstance(r.args[0], CInt):
            val = r.args[0].args[0]
            if repr(r.args[1]) == repr(l):
                return BinExpr('*', CInt(val+1), l)

def simplifyPattern2(op, l,r): # (+/- (+ E N1) N2) --> (+ E N1+/-N2)
    assert op in {'+', '-'}
    if isinstance(l, BinExpr) and l.op=='+':
        if isInt(l.args[1]) and isInt(r):
            N1 = intVal(l.args[1])
            N2 = intVal(r)
            res = eval(f"{N1} {op} {N2}")
            return BinExpr(l.op, l.args[0], CInt(res))

def simplifyPattern3(op, l,r): # (+/- (+ N1 E) N2)) --> (+ E N1+/-N2)
    assert op in {'+', '-'}
    if isinstance(l, BinExpr) and l.op=='+':
        if isInt(l.args[0]) and isInt(r):
            N1 = intVal(l.args[0])
            N2 = intVal(r)
            res = eval(f"{N1} {op} {N2}")
            return BinExpr(l.op, l.args[1], CInt(res))

def simplifyPattern4(op, l,r): # (+ N1 (+/- E N2)) --> (+ E N1+/-N2)
    assert op == '+'
    if isinstance(r, BinExpr) and r.op in {'+','-'}:
        if isInt(r.args[1]) and isInt(l):
            N1 = intVal(l)
            N2 = intVal(r.args[1])
            res = eval(f"{N1} {r.op} {N2}")
            return BinExpr(op, r.args[0], CInt(res))

def simplifyBinExpr(be):
    l = simplify(be.args[0])
    r = simplify(be.args[1])
    if isInt(l) and isInt(r):
        return eval(f"{intVal(l)} {be.op} {intVal(r)}")
    if be.op == '+':
        if repr(l) == repr(r): # (+ E E) -> (* 2 E)
            return simplify(BinExpr('*', CInt(2), l))

        for x, y in [(l,r), (r,l)]:
            if isIntVal(x, 0): # (+ E 0) --> E
                return simplify(y)
            e = simplifyPattern1(be.op, x, y)
            if e:
                return simplify(e)

    if be.op in {'+', '-'}:
        e = simplifyPattern2(be.op, l, r)
        if e:
            return simplify(e)

        e = simplifyPattern3(be.op, l, r)
        if e:
            return simplify(e)

    return BinExpr(be.op, l, r) #default don't do anything


