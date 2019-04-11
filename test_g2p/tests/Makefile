
all:
	../g2p.py adder_tree.vp --trip
	touch ./newer
	./test_g2p.py
	./test2_g2p.py
	./test3_g2p.py
	./test4_g2p.py

clean:
	$(RM) -r build __from_string__.debug.py __pycache__
