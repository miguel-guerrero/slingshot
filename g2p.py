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
from abc import ABC, abstractmethod
import os
from gencore import *
defaultRenderType = 'trip'

#-------------------------------------------------------------------------------
# Template Renderer's
#-------------------------------------------------------------------------------
class TemplateRenderer(ABC):

    @staticmethod
    @abstractmethod
    def renderStr(contents, passedParamDict, result):
        pass

    @classmethod
    def renderFile(cls, filename, passedParamDict):
        with open(filename) as f:
            contents = f.read()
        return cls.renderStr(contents, passedParamDict)

class MakoRenderer(TemplateRenderer):
    def renderStr(contents, passedParamDict):
        from mako.template import Template
        prefix   = f'<% import g2p as g %>\n'
        prefix  += f'<% passedParamDict = {passedParamDict} %>\n'
        prefix  += f'<% instances = g.InstanceFactory() %>\n'
        prefix  += f'<% IOs = [] %>\n'
        prefix  += f'<% userResult = g.Result() %>\n'

        postfix  = f'<% if result is not None: result.module = g.Module(name, IOs, paramDict, instances.thisLevel(), userResult) %>'

        result = Result()
        render = Template(prefix+contents+postfix).render(**passedParamDict, result=result)
        return render, result.module
        #return Template(prefix+contents+postfix).render(passedParamDict=passedParamDict, result=result)

class TripRenderer(TemplateRenderer):
    def renderStr(contents, passedParamDict):
        import trip
        prefix   = f'% import g2p as g\n'
        prefix  += f'% passedParamDict = tripio["passedParamDict"]\n'
        prefix  += f'% instances = g.InstanceFactory()\n'
        prefix  += f'% IOs = []\n'
        prefix  += f'% userResult = g.Result()\n'
        prefix  += f'% #user code begins\n'

        postfix  = f'\n% #user code ends\n'
        postfix += f'% tripio["result"] = g.Module(name, IOs, paramDict, instances.thisLevel(), userResult)'
        tripio = {}
        tripio['passedParamDict'] = passedParamDict
        tripio['result'] = None
        render, rc = trip.render(prefix+contents+postfix, tripio=tripio, lineOffset=7)
        return render, rc['result']

#See Borg pattern: http://code.activestate.com/recipes/66531 similar to a singleton
class Borg:
    shared_state = {}
    def __init__(self):
        self.__dict__ = self.shared_state

#a singleton like class
class TheRenderer(Borg):
    def __init__(self, typ='mako'):
        super().__init__()
        self.setType(typ)

    def setType(self, typ):
        if typ == 'mako':
            self.renderer = MakoRenderer()
        elif typ == 'trip':
            self.renderer = TripRenderer()
        else:
            raise ValueError

    def instance(self):
        return self.renderer

#-------------------------------------------------------------------------------
# Utility functions
#-------------------------------------------------------------------------------

#during the conversion skips private attributes (starting with __)
def objToDict(class_, filt=lambda kv_tuple : kv_tuple[0][0:2]!='__'):
    return dict(filter(filt, class_.__dict__.items()))

class dictToObj:
    def __init__(self, dict_):
        for k, v in dict_.items():
            setattr(self, k, v)

def vlogIO(IOs, indent=' '*4):
    return f',\n{indent}'.join(map(lambda x : str(x), IOs))

#-------------------------------------------------------------------------------
# File generators
#-------------------------------------------------------------------------------

#given passed params and default values, build a name based on parameters that
#override defaults
def getDefaultName(modBaseName, paramDict, defaultParamDict):
    overriden = {k:v for k,v in paramDict.items() if k in defaultParamDict and paramDict[k] != defaultParamDict[k]}
    nondefault = {k:v for k,v in paramDict.items() if k not in defaultParamDict}
    union = overriden
    union.update(nondefault)
    return modBaseName + ''.join(sorted(f'_{k}{v}' for k,v in union.items()))

def getFinalParams(passedDownParamDict, defaultParamDict):
    allKeys = set(passedDownParamDict).union(defaultParamDict)
    return {key:passedDownParamDict.get(key, defaultParamDict.get(key, None)) for key in allKeys}


def setRenderType(rt):
    global defaultRenderType
    defaultRenderType = rt

def getRenderType(rt):
    if rt is None:
        return defaultRenderType
    return rt

class RenderGenerator(GeneratorBase):
    def __init__(self, targetDir='build', targetExt='.v', *, 
                       srcDir='.', srcExt='.vp', renderType=None):
         super().__init__(targetDir, targetExt)
         self.srcDir = srcDir
         self.srcExt = srcExt
         self.renderType = getRenderType(renderType)

    def runGeneration(self, modBaseName, passedParamDict):
        templatePath = os.path.join(self.srcDir, modBaseName+self.srcExt)
        renderer = TheRenderer(self.renderType)
        return renderer.instance().renderFile(templatePath, passedParamDict)

def generate(name, passedParamDict, **kwargs):
    return RenderGenerator(**kwargs).run(name, passedParamDict)
                
#-------------------------------------------------------------------------------
# Classes for user to define input/output module declarations
#-------------------------------------------------------------------------------
# the weird parameter handle bellow is to allow all these ways to define IOs
#   Input('name', w)      -> lagacy g2p
#   Input('name')         -> legacy g2p with default width=1
#   Input(w, name='name') -> for compatibility with chipo
#   Input(w, 'name')      -> also allowed

def getWidthName(width, name):
    if name is None:
        width, name = 1, width
    if isinstance(width, str) and isinstance(name, int):
        width, name = name, width 
    return width, name

class Input(InputBase, BitVecBase):
    def __init__(self, width=1, name=None):
        width, name = getWidthName(width, name)
        BitVecBase.__init__(self, width=width, name=name)

    def __str__(self):
        return "input "+super().__str__()

class Output(OutputBase, BitVecBase):
    def __init__(self, width=1, name=None):
        width, name = getWidthName(width, name)
        BitVecBase.__init__(self, width=width, name=name)

    def __str__(self):
        return "output "+super().__str__()

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
class Module(ModuleBase):
    def __init__(self, name='<noname>', IOs=[], paramDict={}, 
                 instanceList=[], userResult=None):
        super().__init__(IOs)
        self.name = name
        self.paramDict = paramDict
        self.instanceList = instanceList
        self.userResult = userResult
        self.targetPath = ''

    def getName(self):
        return self.name

    def getInstances(self):
        return self.instanceList

    def __repr__(self):
        paramSortedDict = sortedDictStr(self.paramDict)
        rest = f', paramDict={paramSortedDict}, instanceList={self.instanceList}'
        if self.userResult is not None and repr(self.userResult) != 'Result()':
            rest += f', userResult={self.userResult!r}'
        return f'Module(name={self.name!r}, IOs={self.IOs}{rest})'

#-------------------------------------------------------------------------------
# Class that keeps track of an instance name and uniquified module name
#-------------------------------------------------------------------------------
class Instance:
    def __init__(self, module, insName):
        self.module = module
        self.insName = insName

    def __repr__(self):
        return f'Instance(module={self.module}, insName={self.insName!r})'

#-------------------------------------------------------------------------------
# short-cut functions
#-------------------------------------------------------------------------------
def processParams(modBaseName, passedParamDict, defaultParamDict):
   name = getDefaultName(modBaseName, passedParamDict, defaultParamDict)
   paramDict = getFinalParams(passedParamDict, defaultParamDict)
   params = dictToObj(paramDict)
   return name, paramDict, params

def generateInstance(modBaseName, insName, paramDict):
    module = generate(modBaseName, paramDict)
    return Instance(module, insName)

class InstanceFactory:
    def __init__(self):
        from collections import defaultdict
        self.instanceList = []
        self.instanceCnts = defaultdict(int)

    def add(self, ins):
        self.instanceList.append(ins)

    def thisLevel(self):
        return self.instanceList

    def new(self, modBaseName, paramDict, insName=None):
        if insName is None:
            insName = modBaseName + '_' + str(self.instanceCnts[modBaseName])
            self.instanceCnts[modBaseName] += 1

        ins = generateInstance(modBaseName, insName, paramDict)
        self.add(ins)
        return ins

#-------------------------------------------------------------------------------
# Basic driver
#-------------------------------------------------------------------------------
if __name__=="__main__":
    import sys
    from  argparse import ArgumentParser

    def numberOrStr(s):
        try:
            return int(s)
        except ValueError:
            try:
                return float(s)
            except ValueError:
                return s

    def mainCmdParser(parser, **extra):
        parser.add_argument("templateFile",       help="template file",  type=str, **extra)
        #parser.add_argument("--paramsFile", "-p", help="parameter file", type=str, **extra)
        parser.add_argument("--keyValues",  "-k", help="Where KEYVALUES are pairs key=value", nargs='+', default=[])
        parser.add_argument("--mako",             help="Use Mako renderer instead of Trip", action='store_true', default=False)
        args = parser.parse_args()
        setRenderType('mako' if args.mako else 'trip')
        args.keyValues = dict(kv.split('=') for kv in args.keyValues)
        args.keyValues = {k:numberOrStr(v) for k,v in args.keyValues.items()}
        return args

    args = mainCmdParser(ArgumentParser())

    directory, fileName = os.path.split(args.templateFile)
    topFileName, ext = os.path.splitext(fileName)
    passedParamDict = args.keyValues
    module = generate(topFileName, passedParamDict)
    print('module', module.name, 'generated under build directory')

