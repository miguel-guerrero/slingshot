include ../common/include.mk

VCOMP=iverilog -g2001
VRUN=vvp

all: counter counter2 adder fsm pipe motor_fsm matmul_simple

counter:
	./$@.py > $@.v
	$(VCOMP) $@.v
	diff gold/$@.v .

counter2:
	./$@.py
	$(VCOMP) $@.v
	diff gold/$@.v $@.v

adder:
	./$@.py > $@.v
	$(VCOMP) $@.v tb/stb.v
	$(VRUN) a.out > $@.log
	diff gold/$@.log .

fsm:
	./$@.py > $@.v
	$(VCOMP) $@.v
	diff gold/$@.v .

pipe:
	./$@.py > $@.v
	$(VCOMP) -g2005-sv -DNITERS=2 -DSEED=1 $@.v tb/pipe_tb.v
	$(VRUN) a.out > $@.log
	@grep -q "RESULT: PASS" $@.log || (echo "RESULT: FAIL" && exit 1)
	diff gold/$@.v .

motor_fsm:
	./$@.py > $@.v
	$(VCOMP) $@.v tb/motor_tb.v
	$(VRUN) a.out > $@.log
	diff gold/$@.v $@.v
	diff gold/$@.log .

matmul_simple:
	./$@.py > $@.v
	$(VCOMP) $@.v tb/matmul_tb.v tb/mem.v
	$(VRUN) a.out > $@.log
	diff gold/$@.v $@.v
	diff gold/$@.log .
	grep -q PASSED $@.log

clean:
	$(RM) -r __pycache__ a.out *.v build *.xml *.vcd
	$(RM) *.log 
