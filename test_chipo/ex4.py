#!/usr/bin/env python3
from chipo import *
setIndent('    ')
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
print(w.vlog(0))
print(w.vlog(1))


s=Switch(a).Case(1,2).Do(i,i).Case(3).Do(i).Default(i)
print(s)
print(s.vlog(0))
print(s.vlog(1))

f=If(a).Then(i).Else(i,i)
print(f)
print(f.vlog(0))
print(f.vlog(1))
