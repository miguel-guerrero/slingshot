include ../common/include.mk

VCOMP=iverilog -g2001
VRUN=vvp
DIFF=diff -wbB

all: counter counter2 adder fsm pipe motor_fsm matmul_simple

counter:
	./$@.py > $@.v
	$(VCOMP) $@.v
	$(DIFF) gold/$@.v .

counter2:
	./$@.py
	$(VCOMP) $@.v
	$(DIFF) gold/$@.v $@.v

adder:
	./$@.py > $@.v
	$(VCOMP) $@.v tb/stb.v
	$(VRUN) a.out > $@.log
	$(DIFF) gold/$@.log .

fsm:
	./$@.py > $@.v
	$(VCOMP) $@.v
	$(DIFF) gold/$@.v .

pipe:
	./$@.py > $@.v
	$(VCOMP) -g2005-sv -DNITERS=2 -DSEED=1 $@.v tb/pipe_tb.v
	$(VRUN) a.out > $@.log
	@grep -q "RESULT: PASS" $@.log || (echo "RESULT: FAIL" && exit 1)
	$(DIFF) gold/$@.v .

motor_fsm:
	./$@.py > $@.v
	$(VCOMP) $@.v tb/motor_tb.v
	$(VRUN) a.out > $@.log
	$(DIFF) gold/$@.v $@.v
	$(DIFF) gold/$@.log .

matmul_simple:
	./$@.py > $@.v
	$(VCOMP) $@.v tb/matmul_tb.v tb/mem.v
	$(VRUN) a.out > $@.log
	$(DIFF) gold/$@.v $@.v
	$(DIFF) gold/$@.log .
	grep -q PASSED $@.log

clean:
	$(RM) -r __pycache__ a.out *.v build *.xml *.vcd
	$(RM) *.log 
