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
import inspect

def retrieveNames(var, maxLevels=100):
    lastMatch=[]
    frame = inspect.currentframe()
    f = frame.f_back
    for i in range(maxLevels):
        try:
            callerLocals = f.f_locals.items()
            match = [name for name, val in callerLocals if val is var]
            if len(match) > 0:
                lastMatch.append(match)
            f = f.f_back
        except:
            del frame
            return lastMatch

def makeCounter():
    count = 0
    def inner():
        nonlocal count
        count += 1
        return count
    return inner

counter = makeCounter()

def outerName(var):
    try:
        nm = retrieveNames(var)[-1][-1]
        if nm == 'self':
            nm=''
        return nm
    except:
        return 'auto_'+str(counter())

class Named():
    def __init__(self, name=None):
        if name == 'self':
            raise ValueError('The name "self" is reserved and cannot be used')
        self.__name = name

    @property
    def name(self):
        self.__name = self.__name or outerName(self)
        return self.__name

    @name.setter
    def name(self, x):
        self.__name = x
