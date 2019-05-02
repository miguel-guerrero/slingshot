include ../common/include.mk

VCOMP=iverilog -g2001
VRUN=vvp

all: reg_test reg_test2 ex1 ex2 ex3 g2p_ex1 g2p_ex2 vlog

vlog: adder adder2 adder3 adder4 sadder4 adder5 \
 multi_adder multi_adder2 multi_adder3

reg_test:
	./reg_test.py > reg_test.ralf
	diff -wb gold/reg_test.ralf .

reg_test2:
	./reg_test2.py > reg_test2.xml
	diff -wb gold/reg_test2.xml .

ex1:
	./ex1.py > ex1.v
	$(VCOMP) ex1.v
	diff -wb gold/ex1.v .

ex2:
	./ex2.py > ex2.log
	diff -wb gold/ex2.log .

ex3:
	./ex3.py > ex3.log
	diff -wb gold/ex3.log .

ex4:
	./ex4.py > ex4.log
	diff -wb gold/ex4.log .

adder:
	./adder.py > adder.v
	$(VCOMP) adder.v tb.v
	$(VRUN) a.out > adder.log
	diff gold/adder.log .

adder2:
	./adder2.py > adder2.v
	$(VCOMP) adder2.v tb.v
	$(VRUN) a.out > adder2.log
	diff gold/adder2.log .

adder3:
	./adder3.py > adder3.v
	$(VCOMP) adder3.v tb.v
	$(VRUN) a.out > adder3.log
	diff gold/adder3.log .

adder4:
	./adder4.py > adder4.v
	$(VCOMP) adder4.v tb.v
	$(VRUN) a.out > adder4.log
	diff gold/adder4.log .

adder5:
	./adder5.py > adder5.v
	$(VCOMP) adder5.v tb.v
	$(VRUN) a.out > adder5.log
	diff gold/adder5.log .

sadder4:
	./sadder4.py > sadder4.v
	$(VCOMP) sadder4.v stb.v
	$(VRUN) a.out > sadder4.log
	diff gold/sadder4.log .

multi_adder:
	./multi_adder.py > multi_adder.v
	$(VCOMP) ./multi_adder.v
	diff gold/multi_adder.v .

multi_adder2:
	./multi_adder2.py > multi_adder2.v
	$(VCOMP) ./multi_adder2.v
	diff gold/multi_adder2.v .

multi_adder3:
	./multi_adder3.py > multi_adder3.v
	$(VCOMP) ./multi_adder3.v
	diff gold/multi_adder3.v .

g2p_ex1:
	./g2p_ex1.py > g2p_ex1.log
	diff gold/adder_WIDTH32.v build
	diff gold/g2p_ex1.log .

g2p_ex2:
	./g2p_ex2.py > g2p_ex2.log
	diff gold/adder_WIDTH32_2.v build/adder_WIDTH32.v
	diff gold/g2p_ex2.log .

clean:
	$(RM) -r __pycache__ a.out ex*.v *adder*.v build *.ralf *.xml debug_apb_csr*
	$(RM) *.log 
