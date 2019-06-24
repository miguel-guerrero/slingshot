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
import os
from varname import Named

def sortedDictStr(d):
    return '{' + ', '.join(f"{k!r}: {v!r}" for k,v in sorted(d.items())) + '}'

def mkdirRecursive(path):
    path += os.sep
    pos = -1 
    while True:
        pos = path.find(os.path.sep, pos+1)
        if pos < 0:
            break
        if not os.path.isdir(path[:pos]):
            os.mkdir(path[:pos])

# may not be used
def isFileNewer(filePath1, filePath2):
    return os.path.getctime(filePath1) > os.path.getctime(filePath2)

def toDict(**kwargs):
    return kwargs

#-------------------------------------------------------------------------------
# Struct style of class for user defined results from a module generation
# the user can dynamically add class attributes to it
#-------------------------------------------------------------------------------
class Result: 
    def __init__(self, *args, **kwargs):
        if args != ():
            self.args = args
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        pairs = ', '.join(f'{k}={self.__getattribute__(k)!r}' 
                          for k in self.__dir__() if k[:2]!='__')
        return f'Result({pairs})'

#-------------------------------------------------------------------------------
# Base class for RenderGenerator (used by g2p) and 
# ApiGenrator (used by chipo) to provide a consistent way to mix and match
# modules generated either way
#-------------------------------------------------------------------------------
class GeneratorBase:

    def __init__(self, targetDir='build', targetExt='.v'):
        self.targetDir = targetDir
        self.targetExt = targetExt

    def run(self, modBaseName, passedParamDict):
        if not os.path.isdir(self.targetDir):
            mkdirRecursive(self.targetDir)

        resultString, rc = self.runGeneration(modBaseName, passedParamDict)
        rc.targetPath = os.path.join(self.targetDir, rc.name+self.targetExt)

        skipWrite = False
        if os.path.exists(rc.targetPath):
            #check preexisting file matches
            with open(rc.targetPath, 'r') as f:
               skipWrite = f.read() == resultString
        if not skipWrite:
            with open(rc.targetPath, 'w') as f:
                f.write(resultString)
        return rc

    def runGeneration(modBaseName, passedParamDict):
        return NotImplementedError #must be provided by derived classes

#-------------------------------------------------------------------------------
# To keep track of a Module parameters, IO's, instantiations and uniquified name
# across hierarchy
#-------------------------------------------------------------------------------
class ModuleBase:
    def __init__(self, IOs):
        self.IOs = list(IOs)
        self.paramDict = dict()
        self.userResult = Result()
        self.targetPath = ''

    def getName(self):
        return NotImplementedError

    def getIOs(self):
        return self.IOs

    def getAst(self):
        return None

    def getInstances(self):
        raise NotImplementedError

    def vlog(self, indLvl=0, recursive=False):
        return ""

    def vlogIter(self, indLvl=0, recursive=False):
        yield self.getName(), None

#-------------------------------------------------------------------------------
# Makes sure str/repr is consistent with g2p and chipo derived types
#-------------------------------------------------------------------------------
class BitVecBase(Named):

    def __init__(self, *, width=1, name=None):
        self.width = width
        Named.__init__(self, name)

    def getName(self):
        return self.name

    def getWidth(self):
        return self.width

    def getMsb(self):
        return self.width-1

    def __str__(self):
        if self.width != 1:
            return f"[{self.getMsb()}:0] {self.name}"
        return self.name

    def __repr__(self):
        if self.width != 1:
            return f"{self.width!r}, name={self.name!r}"
        return f"name={self.name!r}"

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
class IoBase:
    pass

class InputBase(IoBase):
    def __repr__(self):
        w = f", {self.width}" if self.width != 1 else ""
        return f"Input({self.name!r}{w})"

class OutputBase(IoBase):
    def __repr__(self):
        w = f", {self.width}" if self.width != 1 else ""
        return f"Output({self.name!r}{w})"
