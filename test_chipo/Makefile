include ../common/include.mk

VCOMP=iverilog -g2001
VRUN=vvp

all: reg_test reg_test2 ex1 ex2 ex3 g2p_ex1 g2p_ex2 vlog

vlog: adder adder2 adder3 adder4 sadder4 adder5 \
 multi_adder multi_adder2 multi_adder3 \
 rec rec2 rec3 rec4 rec5 rec6 uni uni2 \
 pipe1

reg_test:
	./$@.py > $@.ralf
	diff -wb gold/$@.ralf .

reg_test2:
	./$@.py > $@.xml
	diff -wb gold/$@.xml .

ex1:
	./$@.py > $@.v
	$(VCOMP) $@.v
	diff -wb gold/$@.v .

ex2:
	./$@.py > $@.log
	diff -wb gold/$@.log .

ex3:
	./$@.py > $@.log
	diff -wb gold/$@.log .

ex4:
	./$@.py > $@.log
	diff -wb gold/$@.log .

adder:
	./$@.py > $@.v
	$(VCOMP) $@.v tb/tb.v
	$(VRUN) a.out > $@.log
	diff gold/$@.log .

adder2:
	./$@.py > $@.v
	$(VCOMP) $@.v tb/tb.v
	$(VRUN) a.out > $@.log
	diff gold/$@.log .

adder3:
	./$@.py > $@.v
	$(VCOMP) $@.v tb/tb.v
	$(VRUN) a.out > $@.log
	diff gold/$@.log .

adder4:
	./$@.py > $@.v
	$(VCOMP) $@.v tb/tb.v
	$(VRUN) a.out > $@.log
	diff gold/$@.log .

adder5:
	./$@.py > $@.v
	$(VCOMP) $@.v tb/tb.v
	$(VRUN) a.out > $@.log
	diff gold/$@.log .

sadder4:
	./$@.py > $@.v
	$(VCOMP) $@.v tb/stb.v
	$(VRUN) a.out > $@.log
	diff gold/$@.log .

rec:
	./$@.py > $@.v
	$(VCOMP) $@.v
	diff gold/$@.v .

rec2:
	./$@.py > $@.v
	$(VCOMP) $@.v
	diff gold/$@.v .

rec3:
	./$@.py > $@.v
	$(VCOMP) $@.v
	diff gold/$@.v .

rec4:
	./$@.py > $@.v
	$(VCOMP) $@.v
	diff gold/$@.v .

rec5:
	./$@.py > $@.v
	$(VCOMP) $@.v
	diff gold/$@.v .

rec6:
	./$@.py > $@.v
	$(VCOMP) $@.v
	diff gold/$@.v .

uni:
	./$@.py > $@.v
	$(VCOMP) $@.v
	diff gold/$@.v .

uni2:
	./$@.py > $@.v
	$(VCOMP) $@.v
	diff gold/$@.v .

pipe1:
	./$@.py > $@.v
	$(VCOMP) $@.v
	diff gold/$@.v .

multi_adder:
	./$@.py > $@.v
	$(VCOMP) ./$@.v
	diff gold/$@.v .

multi_adder2:
	./$@.py > $@.v
	$(VCOMP) ./$@.v
	diff gold/$@.v .

multi_adder3:
	./$@.py > $@.v
	$(VCOMP) ./$@.v
	diff gold/$@.v .

g2p_ex1:
	./$@.py > $@.log
	diff gold/adder_WIDTH32.v build
	diff gold/$@.log .

g2p_ex2:
	./$@.py > $@.log
	diff gold/adder_WIDTH32_2.v build/adder_WIDTH32.v
	diff gold/$@.log .

clean:
	$(RM) -r __pycache__ a.out *.v build *.ralf *.xml *.vcd
	$(RM) *.log 
