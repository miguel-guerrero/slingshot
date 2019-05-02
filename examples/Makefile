include ../common/include.mk

VCOMP=iverilog -g2001
VRUN=vvp

all: counter counter2

counter:
	./counter.py > counter.v
	$(VCOMP) counter.v
	diff gold/counter.v .

counter2:
	./counter2.py
	$(VCOMP) counter2.v
	diff gold/counter2.v counter2.v

clean:
	$(RM) -r __pycache__ a.out *.v build *.xml 
	$(RM) *.log 