all: adder
TOOL=./trip.py

adder:
	$(TOOL) adder.vp -p context.json -k WIDTH=10 -v > adder_10_cin.v
	$(TOOL) adder.vp -p context.json -k WIDTH=10 HAS_CIN=0 -v > adder_10.v

clean:
	$(RM) -r __pycache__
	$(RM) adder_10.v adder_10_cin.v *.debug.py
