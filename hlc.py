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
# High level Constructs
#------------------------------------------------------------------------------
from enum import Enum
from collections import Counter

from chipo import *
from simplify import isIntVal


#------------------------------------------------------------------------------
# Logic under a block contains a clock edge?
#------------------------------------------------------------------------------
def hasWfe(node):
    return node.any(lambda x : x is ...)

#------------------------------------------------------------------------------
# Pipeline
#------------------------------------------------------------------------------
class Stage(AstNode):
    def __init__(self, stmts):
        self.stmts = stmts

    def assigned(self):  return self.apply('assigned',  self.stmts)
    def used(self):      return self.apply('used',      self.stmts)
    def paramUsed(self): return self.apply('paramUsed', self.stmts)
    def typesUsed(self): return self.apply('typesUsed', self.stmts)
    def driven(self):    return self.apply('driven',    self.stmts)
    def declared(self):  return self.apply('declared',  self.stmts)

    def __repr__(self):
        return f"Stage({self.stmts})"


class StagedSignal(Signal):
    def __init__(self, s:Signal, stageNum:int, lastStageNum:int, pipeName:str):
        super().__init__(s.args[0], s.name, s.default)
        self.stageNum = stageNum
        self.lastStageNum = lastStageNum
        self.pipeName = pipeName
        self.origSignal = s
        self._origName = s.name

    @property
    def name(self):
        if self.stageNum != self.lastStageNum:
            return f"{self.pipeName}_s{self.stageNum}_{self._origName}"
            #return f"{self.pipeName}{self.stageNum}_{self._origName}"
        return f"{self.pipeName}_{self._origName}"

    @property
    def origName(self):
        return self._origName
    

class Pipeline(Named):
    def __init__(self, clock, reset, *, keep, name=None, vld=None, rdy=None):
        Named.__init__(self, name)
        self.clock, self.reset = clock, reset
        self.keep = list(keep)
        self.body = Block()
        self.vld_up = vld
        self.rdy_dn = rdy
        self.vld = Signal(1, name='vld') if vld else None
        self.rdy = Signal(1, name='rdy') if rdy else None
        if rdy and not vld: 
            raise ValueError(h.error("If rdy provided, vld must be provided too", self))
        self.logic_ = None
        self.outs_ =  None

    def check(self, stm):
        if isinstance(stm, While) and hasWfe(stm):
            raise TypeError(h.error('While loops with ... enclosed not allowed within a Pileline.', stm))

    def __iadd__(self, stm):
        self.check(stm)
        self.body += stm
        return self

    def __getitem__(self, stmts):
        for stm in h.tupleize(stmts):
            self.check(stm)
            self.body += stm
        return self

    @staticmethod
    def replaceUses(stm, s, ss):
        def f(x):
            if isinstance(x, (BinExpr, MultiExpr)) or type(x)==UnaryExpr:
                for i, e in enumerate(x.args):
                    if repr(e) == repr(s): # and isinstance(x.args[0], Signal):
                        x.args[i] = ss

        stm.applyFunc(f)

    @staticmethod
    def replaceAssigned(stm, s, ss):
        def f(x):
            if isinstance(x, SigAssign):
                if repr(x.lhs) == repr(s): # and isinstance(x.args[0], Signal):
                    x.lhs = ss

        stm.applyFunc(f)

    # TODO
    #def _autoKeep(self): # = {drivenSig} - {usedSig} - {declared}
    #    usedSig = {s for s in self.used(Signal) if not isinstance(s, Out)}
    #    declared = self.declared()
    #    drivenSig = self.assigned(Signal).union(self.driven())
    #    return (drivenSig.difference(usedSig)).difference(declared)

    def processStages(self, stages):
        allUsed = set()
        allAssigned = set()
        for stg in stages:
            allUsed = allUsed.union(stg.used())
            allAssigned = allAssigned.union(stg.assigned())

        prevIns = set(self.keep)
        pipeList = []
        lastStageNum = len(stages)
        currStageNum = lastStageNum
        lastStageSigs = []
        for stg in reversed(stages):
            assigned_i = stg.assigned()
            outs_i = prevIns
            ins_i = set.union(outs_i, stg.used()) - assigned_i
            passed_i = outs_i - assigned_i

            m = Clocked(self.clock, autoReset=False, name=f"{self.name}_stage{currStageNum}")

            if self.vld:
                vld_i   = StagedSignal(self.vld, currStageNum,   lastStageNum, self.name)
                vld_im1 = StagedSignal(self.vld, currStageNum-1, -1, self.name)

            if self.rdy:
                rdy_i   = StagedSignal(self.rdy, currStageNum,   -1, self.name)
                rdy_ip1 = StagedSignal(self.rdy, currStageNum+1, -1, self.name)

            load_data = None
            if self.vld and self.rdy:
                m2 = Clocked(self.clock, self.reset, name=f"{self.name}_stage{currStageNum}_vld")
                #E.g. for s3:  if (sad_s2_vld & sad_s3_rdy) .. load on s3
                load_data = vld_im1 & rdy_i
                #E.g. for s3:  sad_s3_vld <= sad_s3_rdy ? sad_s2_vld : sad_s3_vld
                m2 += SigAssign(vld_i, IfCond(rdy_i, vld_im1, vld_i))
                #E.g. for s3:  assign sad_s3_rdy = sad_s4_rdy | ~sad_s3_vld;
                c = SigAssign(rdy_i, rdy_ip1 | ~vld_i)
                pipeList.insert(0, c)
                pipeList.insert(0, m2)

                enaStm = If(load_data)
                m += enaStm
                body = enaStm.trueBlock
            elif self.vld:
                m2 = Clocked(self.clock, self.reset, name=f"{self.name}_stage{currStageNum}_vld")
                load_data = vld_im1
                m2 += SigAssign(vld_i, vld_im1)
                pipeList.insert(0, m2)

                enaStm = If(load_data)
                m += enaStm
                body = enaStm.trueBlock
            else:
                body = m

            for stm in stg.stmts:
                if currStageNum != 1:
                    for s in stm.used():
                        ss = StagedSignal(s, currStageNum-1, lastStageNum, self.name)
                        Pipeline.replaceUses(stm, s, ss)
                for s in stm.assigned():
                    ss = StagedSignal(s, currStageNum, lastStageNum, self.name)
                    if currStageNum == lastStageNum:
                        lastStageSigs.append(ss)
                    Pipeline.replaceAssigned(stm, s, ss)
                body += stm

            for s in passed_i:
                ss = StagedSignal(s, currStageNum, lastStageNum, self.name)
                if currStageNum != 1:
                    body += SigAssign(ss, StagedSignal(s, currStageNum-1, lastStageNum, self.name))
                else:
                    body += SigAssign(ss, s)
                if currStageNum == lastStageNum:
                    lastStageSigs.append(ss)

            pipeList.insert(0, m)
            pipeList.insert(0, Comment(f"--- Stage {currStageNum} ---"))
            prevIns = ins_i
            currStageNum -= 1

        if self.vld:
            #E.g. assign sad_s0_vld = up_vld;
            vld_0 = StagedSignal(self.vld, 0, lastStageNum, self.name)
            pipeList.insert(0, SigAssign(vld_0, self.vld_up))
            pipeList.insert(0, Comment('hook to upsstream vld'))

        if self.rdy:
            #E.g. assign sad_rdy = sad_s1_rdy;
            rdy_first = StagedSignal(self.rdy, lastStageNum, lastStageNum, self.name)
            pipeList.insert(0, SigAssign(rdy_first, rdy_i))
            pipeList.insert(0, Comment('hook to upstream rdy'))
            #E.g. assign sad_s4_rdy = dn_rdy;
            pipeList.append(Comment('hook to downstream rdy'))
            rdy_last = StagedSignal(self.rdy, lastStageNum+1, lastStageNum, self.name)
            pipeList.append(SigAssign(rdy_last, self.rdy_dn))

        return pipeList, lastStageSigs

    def expand(self):
        if self.logic_ is None:
            if self.name is None:
                raise ValueError(h.error('A Pipeline must be named', self))
            stages = []
            curr = []
            body = self.body.asList() + [...]
            for stm in body:
                if stm == ...:
                    stages.append(Stage(curr))
                    curr = []
                else:
                    curr.append(stm)
            self.logic_, sigs = self.processStages(stages)
            self.outs_ = h.Struct()
            for s in sigs:
                self.outs_[s.origName] = s
        return tuple(self.logic_)

    @property
    def logic(self):
        if self.logic_ is None:
            self.expand()
        return tuple(self.logic_)

    @property
    def outs(self):
        if self.logic_ is None:
            self.expand()
        return self.outs_

    def __repr__(self):
        s = f"Pipeline({self.name}, {self.clock}, {self.reset}, keep={self.keep}) [\n    "
        s+= "\n   ,".join(repr(stm) for stm in self.body.asList())
        s += ']'
        return s

#------------------------------------------------------------------------------
# Fsm
#------------------------------------------------------------------------------
class NodeType(Enum):
    ife=0
    stm=1
    wfe=2
    removed=3

#------------------------------------------------------------------------------
# Handles parse tree nodes
#------------------------------------------------------------------------------
class Node:
    cnt = 0
    all = []

    def __init__(self, typ, *, code=None, bt=None, bf=None, nx=None):
        self.typ = typ
        self.code = code
        self.bt = bt
        self.bf = bf
        self.nx = nx
        self.visited = False
        self.uid = Node.cnt
        Node.cnt += 1
        Node.all.append(self)

    @classmethod
    def reset(cls):
        Node.cnt=0
        Node.all=[]

    @classmethod
    def clearVisited(cls):
        for n in Node.all:
            n.visited = False

    def __str__(self):
        return f"id{self.uid}"

    @staticmethod
    def nxIter(n):
        while n:
            yield n
            n = n.nx
        raise StopIteration

    def toStr(self):
        out = f"{self} typ:{self.typ}"
        if self.bt is not None:
            out += f" bt:{self.bt}"
        if self.bf is not None:
            out += f" bf:{self.bf}"
        if self.nx is not None:
            out += f" nx:{self.nx}"
        if self.code is not None:
            out += f" code:'{self.code!r}'"
        return out 

    def succ(self):
        return self.bf or self.nx

    @staticmethod
    def linksTo(dst):
        to={}
        for n in Node.all:
            t=[]
            if n.bt == dst:
                t.append("bt")
            if n.bf == dst:
                t.append("bf")
            if n.nx == dst:
                t.append("nx")
            if t != []:
                to[n] = list(t)
        return to

    @staticmethod
    def remove(node):
        node.typ = NodeType.removed


#--------------------------------------------------------------------
# DAG related routines
#--------------------------------------------------------------------
def showFromNode(root:Node, tab="\t") -> str:
    def subPr(ind:str, n:Node) -> str:
        if n.visited:
            return ""
        n.visited = True
        out = ind + n.toStr()
        nxStr = subPr(ind, n.nx) if n.nx else ''
        if n.bt:
            out += '\n' + subPr(ind+tab, n.bt)
        if n.bf:
            out += '\n' + subPr(ind+tab, n.bf)
        if n.nx:
            out += '\n' + nxStr
        return out

    Node.clearVisited()
    return subPr("", root)


#------------------------------------------------------------------------------
# Main Fsm class
#------------------------------------------------------------------------------
def Wait(expr): #conveniece macro within Fsm body's
    return While(~expr) [...]


class Fsm(Named):
    def __init__(self, clock=None, reset=None, *, name=None, behav=False, sigFsm=True, keep=[]):
        Named.__init__(self, name)
        self.clock, self.reset = clock, reset
        self.keep = list(keep)
        self.body = Block()
        self.logic_ = None
        self.Q = "_q"
        self.wfeCounter = 0
        self.behav = behav
        self.sigFsm = sigFsm
        if sigFsm: # dummy state name for mergeStates
            self.state = Signal(1, name='__theState__')
        else:
            self.state = Var(1, name='__theState__') 

    def __iadd__(self, x):
        self.body += x
        return self

    def __getitem__(self, stmts):
        for stm in h.tupleize(stmts):
            if not isinstance(stm, AstProcStatement) and stm is not ...:
                raise ValueError(f"Expecting AstProcStatement or ... but got {stm}")
            self.body += stm
        return self

    def findFirstWfe(self, node:Node):
        def findFirstWfeSub(node):
            if node is None or node.visited:
                return
            node.visited = True
            if node.typ == NodeType.wfe:
                return node
            for n in (node.bt, node.bf, node.nx):
                nWfe = findFirstWfeSub(n)
                if nWfe is not None:
                    return nWfe
 
        Node.clearVisited()
        node = findFirstWfeSub(node)
        if node:
            return node
        raise ValueError("Cannot determine initial state (no ...?)")

    def hasWfeList(self, n:Node) -> bool : 
        return any(self.hasWfe(i) for i in Node.nxIter(n))

    def hasWfe(self, n:Node) -> bool:
        if n is None or n.typ == NodeType.stm:
            return False
        elif n.typ == NodeType.wfe:
            return True
        elif n.typ == NodeType.ife:
            return self.hasWfeList(n.bt) or self.hasWfeList(n.bf)
        else:
            raise TypeError(f"Type {n.typ} not allowed in Fsm block")

    def toDAG(self):
        def toDagSub(body, nx):
            for stm in reversed(body):
                if isinstance(stm, If):
                    nLast = toDagSub(stm.falseBlock, nx=nx)
                    for i in reversed(range(len(stm.elifCond))):
                        block = stm.elifBlock[i]
                        cond = stm.elifCond[i]
                        nLast = Node(NodeType.ife, code=cond, bt=toDagSub(block, nx=nx), bf=nLast)
                    n = Node(NodeType.ife, code=stm.cond, bt=toDagSub(stm.trueBlock, nx=nx), bf=nLast)
                elif isinstance(stm, While):
                    n = Node(NodeType.ife, code=stm.cond, bf=nx)
                    n.bt = toDagSub(stm.trueBlock, nx=n)
                elif stm is ...:
                    n = Node(NodeType.wfe, code=self.wfeCounter, nx=nx)
                    self.wfeCounter += 1
                else:
                    n = Node(NodeType.stm, code=stm, nx=nx)
                nx = n
            return nx

        Node.reset()
        self.wfeCounter = 0
        return toDagSub(self.body, nx=None)

    def stateName(self, node:Node) -> str:
        return f"{self.oprefix}S{node.code}"

    def varAssigned(self):
        return set([v for v in self.body.assigned() if isinstance(v, Var)])

    def dumpTree(self, root:Node):
        self.root = root
 
        #create dict that links wfe nodes with its id
        wfeLst = [n for n in Node.all if n.typ == NodeType.wfe]
        wfeCnt = len(wfeLst)
        wfes = {}
        for node in wfeLst:
            wfeCnt -= 1
            node.code = wfeCnt
            wfes[node.code] = node
 
        #give unique names to the estates based on wfe nodes
        stateNames = [self.stateName(wfes[code]) for code in sorted(wfes)]

        #create state type
        States = Enu(*stateNames, name=self.name+f"{self.name}_state_t")

        #find initial state
        initStateName = self.stateName(self.findFirstWfe(root))

        if self.sigFsm:
            self.state = Signal(States, name=f'{self.name}_state', default=initStateName)
        else:
            self.state = Var(States, name=f'{self.name}_state', default=initStateName)

        #start building the logic
        clocked = Clocked(self.clock, self.reset, name=f"{self.name}_clocked")

        #create transition switch statement
        switch = Switch(self.state)
        for code in sorted(wfes):
            node = wfes[code]
            stName = self.stateName(node)
            switch = switch.Case(stName) [
                self.dumpSubtreeFsm(node.succ(), "rel", node, visitedIn=set())
            ]

        if self.sigFsm:
            clocked += switch
            return clocked
        else:
            #create state signal
            stateQ = Signal(States, name=f'{self.name}_state'+self.Q, default=initStateName)
            combo = Combo(name=f"{self.name}_combo")
            #set next state variables to right default (flop output)
            sigs = {Signal(v, name=v.name+self.Q):v for v in sortedAsList(self.varAssigned())}
            sigs[stateQ] = state
            for s, v in sigs.items():
                clocked += SigAssign(s, v)
                combo   += VarAssign(v, s)
            combo += switch
            return Block(combo, clocked)

    def sigAssigned(self):
        return set([v for v in self.body.assigned() if isinstance(v, Signal)])

    def dumpSubtreeFsm(self, node:Node, mode:str, stateNode:Node, visitedIn):
        visited = set(visitedIn) # make a value copy
        out = Block()
        while node:
            if node.uid in visited:
                import sys
                visitedStr = ', '.join([str(x) for x in visited])
                print(showFromNode(self.root), file=sys.stderr)
                raise ValueError(f"SM There is a loop path without ... within "+\
                                f"the set of nodes {visitedStr}. Currently @{node.uid}")

            bt, bf, nx = node.bt, node.bf, node.nx
            if node.typ == NodeType.ife:
                visited.add(node.uid)
                cond = node.code
                if isIntVal(cond, 1):
                    blk = self.dumpSubtreeFsm(bt, mode, stateNode, visited)
                    appendStms(out, blk.asList())
                elif isIntVal(cond, 0):
                    n = bf or nx
                    if n:
                        blk = self.dumpSubtreeFsm(n, mode, stateNode, visited)
                        appendStms(out, blk.asList())
                else:
                    ife = If(cond) [
                              self.dumpSubtreeFsm(bt, mode, stateNode, visited)
                           ]
                    n = bf or nx
                    if n:
                        ife = ife.Else[
                            self.dumpSubtreeFsm(n, mode, stateNode, visited)
                        ]
                    out += ife
                node = None
            elif node.typ == NodeType.stm: 
                visited.add(node.uid)
                out += node.code
                node = node.succ()
            elif node.typ == NodeType.wfe:
                if mode == "rel" and node == stateNode:
                    out += Comment("stay")
                else:
                    out += SigAssign(self.state, self.stateName(node)) if self.sigFsm else \
                           VarAssign(self.state, self.stateName(node))
                node = None
            else:
                out += Comment(f"// Ignoring node={node} typ={node.typ} code='{node.code}'")
                node = node.succ()
        return out

    def mergeStates(self, root):
        someMerge = True
        while someMerge:
            someMerge = False
            wfes = {node.code:node for node in Node.all if node.typ == NodeType.wfe}
            for mode in ("abs", "rel"):
                codeCnt = Counter()
                codeByNode = {}
                for code in sorted(wfes):
                    node = wfes[code]
                    out = repr(self.dumpSubtreeFsm(node.succ(), mode, node, set()))
                    codeCnt[out] += 1
                    codeByNode[node] = out
                for code, cnt in codeCnt.items():
                    if cnt > 1:
                        nodesToMerge=[n for n in codeByNode if codeByNode[n] == code]
                        self.mergeKeepingFirst(nodesToMerge[1], nodesToMerge[0])
                        someMerge = True
                        break

    #anything pointing to B should now point to A
    def mergeKeepingFirst(self, nodeA, nodeB):
        for nodeFrom, linkTypes in Node.linksTo(nodeB).items():
            if 'bt' in linkTypes:
                nodeFrom.bt = nodeA
            if 'bf' in linkTypes:
                nodeFrom.bf = nodeA
            if 'nx' in linkTypes:
                nodeFrom.nx = nodeA
        Node.remove(nodeB) #... removed

    def expand(self):
        if self.logic_ is None:
            if self.name is None:
                raise ValueError(h.error('An Fsm must be named', self))
            self.oprefix = "SM_"+self.name.upper()+"_"
            if self.behav:
                rstLst = (x <= x.default for x in self.body.assigned())
                rstLst = sorted(rstLst, key=lambda x : x.lhs.name)
                loopName = f"_loop"
                clocked = Clocked(self.clock, self.reset, name=f"{self.name}_clocked")
                clocked += \
                    Block(
                        If(self.reset.offExpr()) [
                            Block(
                                While(1) [
                                    tuple(self.body.stmts),
                                    ...
                                ],
                            name=loopName)
                        ],
                        *rstLst,
                        ...,
                    )
                clocked.hasWfe = True
                clocked.autoReset = False
                self.logic_ = clocked
            else:
                self.body = Block( While(1).Do(..., *self.body.stmts) ) 
                root = self.toDAG()
                self.mergeStates(root)
                self.logic_ = self.dumpTree(root)
        return self.logic_

    @property
    def logic(self):
        if self.logic_ is None:
            self.expand()
        return self.logic_

    def __repr__(self):
        s  = f"Fsm({self.name}, {self.clock}, {self.reset}, keep={self.keep}) [\n    "
        s += "\n   ,".join(repr(stm) for stm in self.body)
        s += ']'
        return s

