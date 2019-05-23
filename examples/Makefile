include ../common/include.mk

VCOMP=iverilog -g2001
VRUN=vvp

all: counter counter2 fsm adder

counter:
	./$@.py > $@.v
	$(VCOMP) $@.v
	diff gold/$@.v .

counter2:
	./$@.py
	$(VCOMP) $@.v
	diff gold/$@.v $@.v

fsm:
	./$@.py > $@.v
	$(VCOMP) $@.v
	diff gold/$@.v .

adder:
	./$@.py > $@.v
	$(VCOMP) $@.v tb/stb.v
	$(VRUN) a.out > $@.log
	diff gold/$@.log .

clean:
	$(RM) -r __pycache__ a.out *.v build *.xml 
	$(RM) *.log 
