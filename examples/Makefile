include ../common/include.mk

VCOMP=iverilog -g2001
VRUN=vvp
DIFF=diff -wbB

all: counter counter2 adder fsm pipe motor_fsm matmul_simple

counter:
	./$@.py > $@.v
	$(VCOMP) -o $@.out $@.v
	$(DIFF) gold/$@.v .

counter2:
	./$@.py
	$(VCOMP) -o $@.out $@.v
	$(DIFF) gold/$@.v $@.v

adder:
	./$@.py > $@.v
	$(VCOMP) -o $@.out $@.v tb/stb.v
	$(VRUN) $@.out > $@.log
	$(DIFF) gold/$@.log .

fsm:
	./$@.py > $@.v
	$(VCOMP) -o $@.out $@.v
	$(DIFF) gold/$@.v .

pipe:
	./$@.py > $@.v
	$(VCOMP) -o $@.out -g2005-sv -DNITERS=10 -DSEED=1 -DDUMP $@.v tb/pipe_tb.v
	$(VRUN) $@.out > $@.log
	@grep -q "RESULT: PASS" $@.log || (echo "RESULT: FAIL" && exit 1)
	$(DIFF) gold/$@.v .

motor_fsm:
	./$@.py > $@.v
	$(VCOMP) -o $@.out $@.v tb/motor_tb.v
	$(VRUN) $@.out > $@.log
	$(DIFF) gold/$@.v $@.v
	$(DIFF) gold/$@.log .

motor_fsm_behav:
	./$@.py > $@.v
	$(VCOMP) -o $@.out $@.v tb/motor_tb.v
	$(VRUN) $@.out > $@.log
	$(DIFF) gold/$@.v $@.v
	$(DIFF) gold/motor_fsm.log motor_fsm_behav.log

matmul_simple:
	./$@.py > $@.v
	$(VCOMP) -o $@.out $@.v tb/matmul_tb.v tb/mem.v
	$(VRUN) $@.out > $@.log
	$(DIFF) gold/$@.v $@.v
	$(DIFF) gold/$@.log .
	grep -q PASSED $@.log

matmul_simple2:
	./$@.py > $@.v
	$(VCOMP) -o $@.out $@.v tb/matmul_tb.v tb/mem.v
	$(VRUN) $@.out > $@.log
	$(DIFF) gold/$@.v $@.v
	$(DIFF) gold/$@.log .
	grep -q PASSED $@.log

clean:
	$(RM) -r __pycache__ *.out *.v build *.xml *.vcd
	$(RM) *.log 
