all: adder adder2
TOOL=./trip.py

adder:
	$(TOOL) adder.vp --keepPython -p context.json -k WIDTH=10 -v > adder_10_cin.v
	$(TOOL) adder.vp -p context.json -k WIDTH=10 HAS_CIN=0 -v > adder_10.v

adder2:
	$(TOOL) adder2.vp -p context.json -k WIDTH=10 -v > adder2_10_cin.v

clean:
	$(RM) -r __pycache__
	$(RM) adder_10.v adder_10_cin.v adder2_10_cin.v *.debug.py
