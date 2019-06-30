include ../common/include.mk

VCOMP=iverilog -g2001
VRUN=vvp
DIFF=diff -wbB

all: reg_test reg_test2 ex1 ex2 ex3 g2p_ex1 g2p_ex2 vlog

vlog: adder adder2 adder3 adder4 sadder4 adder5 \
 multi_adder multi_adder2 multi_adder3 \
 rec rec2 rec3 rec4 rec5 rec6 uni uni2 \
 pipe1 ins ins2 ins3 ins4

reg_test:
	./$@.py > $@.ralf
	$(DIFF) gold/$@.ralf .

reg_test2:
	./$@.py > $@.xml
	$(DIFF) gold/$@.xml .

ex1:
	./$@.py > $@.v
	$(VCOMP) $@.v
	$(DIFF) gold/$@.v .

ex2:
	./$@.py > $@.log
	$(DIFF) gold/$@.log .

ex3:
	./$@.py > $@.log
	$(DIFF) gold/$@.log .

ex4:
	./$@.py > $@.log
	$(DIFF) gold/$@.log .

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
	$(DIFF) gold/$@.v .

rec2:
	./$@.py > $@.v
	$(VCOMP) $@.v
	$(DIFF) gold/$@.v .

rec3:
	./$@.py > $@.v
	$(VCOMP) $@.v
	$(DIFF) gold/$@.v .

rec4:
	./$@.py > $@.v
	$(VCOMP) $@.v
	$(DIFF) gold/$@.v .

rec5:
	./$@.py > $@.v
	$(VCOMP) $@.v
	$(DIFF) gold/$@.v .

rec6:
	./$@.py > $@.v
	$(VCOMP) $@.v
	$(DIFF) gold/$@.v .

uni:
	./$@.py > $@.v
	$(VCOMP) $@.v
	$(DIFF) gold/$@.v .

uni2:
	./$@.py > $@.v
	$(VCOMP) $@.v
	$(DIFF) gold/$@.v .

ins:
	./$@.py > $@.v
	$(VCOMP) $@.v
	$(DIFF) gold/$@.v .

ins2:
	./$@.py 
	$(VCOMP) -f file_list.f
	#$(DIFF) gold/$@.v .

ins3:
	./$@.py > $@.v
	$(VCOMP) $@.v
	$(DIFF) gold/$@.v .

ins4:
	./$@.py > $@.v
	$(VCOMP) $@.v
	$(DIFF) gold/$@.v .

pipe1:
	./$@.py > $@.v
	$(VCOMP) -g2005-sv $@.v
	$(DIFF) gold/$@.v .

multi_adder:
	./$@.py > $@.v
	$(VCOMP) ./$@.v
	$(DIFF) gold/$@.v .

multi_adder2:
	./$@.py > $@.v
	$(VCOMP) ./$@.v
	$(DIFF) gold/$@.v .

multi_adder3:
	./$@.py > $@.v
	$(VCOMP) ./$@.v
	$(DIFF) gold/$@.v .

g2p_ex1:
	./$@.py > $@.log
	$(DIFF) gold/adder_WIDTH32.v build
	diff gold/$@.log .

g2p_ex2:
	./$@.py > $@.log
	$(DIFF) gold/adder_WIDTH32_2.v build/adder_WIDTH32.v
	diff gold/$@.log .

clean:
	$(RM) -r __pycache__ a.out *.v build *.ralf *.xml *.vcd
	$(RM) *.log file_list.f
