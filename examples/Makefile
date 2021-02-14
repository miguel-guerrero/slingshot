include ../common/include.mk

VCOMP=iverilog -g2005-sv
VRUN=vvp
DIFF=diff -wbB -I '^VCD'

all: counter counter2 adder fsm pipe motor_fsm matmul_simple vtpg vtpg_behav

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
	$(DIFF) gold/$@.log .
	$(DIFF) gold/$@.v $@.v

motor_fsm_behav:
	./$@.py > $@.v
	$(VCOMP) -o $@.out $@.v tb/motor_tb.v
	$(VRUN) $@.out > $@.log
	$(DIFF) gold/motor_fsm.log motor_fsm_behav.log
	$(DIFF) gold/$@.v $@.v

matmul_simple:
	./$@.py > $@.v
	$(VCOMP) -o $@.out $@.v tb/matmul_tb.v tb/mem.v
	$(VRUN) $@.out > $@.log
	$(DIFF) gold/$@.log .
	$(DIFF) gold/$@.v $@.v
	grep -q PASSED $@.log

matmul_simple2:
	./$@.py > $@.v
	$(VCOMP) -o $@.out $@.v tb/matmul_tb.v tb/mem.v
	$(VRUN) $@.out > $@.log
	$(DIFF) gold/$@.log .
	$(DIFF) gold/$@.v $@.v
	grep -q PASSED $@.log

vtpg:
	./$@.py > $@.v
	$(VCOMP) -o $@.out $@.v tb/vtpg_tb.v
	$(VRUN) $@.out > $@.log
	$(DIFF) gold/$@.log .
	$(DIFF) gold/$@.v $@.v
	@#grep -q PASSED $@.log

vtpg_behav:
	./$@.py -behav > $@.v
	$(VCOMP) -g2012 -o $@.out $@.v tb/vtpg_tb.v
	$(VRUN) $@.out > $@.log
	$(DIFF) gold/$@.log .
	$(DIFF) gold/$@.v $@.v
	@#grep -q PASSED $@.log

clean:
	$(RM) -r __pycache__ *.out *.v build *.xml *.vcd
	$(RM) *.log *.vg
