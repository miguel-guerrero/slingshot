#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# See https://github.com/miguel-guerrero/slingshot/blob/master/LICENSE
#-------------------------------------------------------------------------------
import sys
sys.path.append("..") # add path to chipo and related
from chipo import *
from vlog import dump

x=(
 If(1).
  Then().
  Else()
)

a=Signal(8)
x=Signal()
i=(x <= 1)

w=While(a).Do(i)
print(w)
print(dump(w, 0))
print(dump(w, 1))


s=Switch(a).Case(1,2).Do(i,i).Case(3).Do(i).Default(i)
print(s)
print(dump(s, 0))
print(dump(s, 1))

f=If(a).Then(i).Else(i,i)
print(f)
print(dump(f, 0))
print(dump(f, 1))
