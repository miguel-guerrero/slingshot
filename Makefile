
all:
	make -C test_trip all
	make -C test all

clean:
	make -C test_trip clean
	make -C test clean
	$(RM) -r __pycache__

