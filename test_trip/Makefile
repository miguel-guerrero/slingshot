all: adder x y
TOOL=./trip.py

x: x.mp
	$(TOOL) x.mp -p context.json -k val=10 name=miguel -v > x.log

y: y.mp
	$(TOOL) y.mp -p context.json -k val=10 name=miguel -v > y.log

adder:
	$(TOOL) adder.vv -p context.json -k WIDTH=10 -v > adder.v

clean:
	$(RM) -r __pycache__
	$(RM) adder.v x.log y.log *.debug.py
