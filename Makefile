
all:
	make -C test_trip all
	make -C test all
	make -C examples all

clean:
	make -C test_trip clean
	make -C test clean
	make -C examples clean
	$(RM) -r __pycache__

