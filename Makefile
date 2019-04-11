
all:
	make -C test all

clean:
	make -C test clean
	$(RM) -r __pycache__

