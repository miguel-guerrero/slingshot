
all:
	make -C test_trip all
	make -C test_chipo all
	make -C examples all
	@echo "ALL PASS"

clean:
	make -C test_trip clean
	make -C test_chipo clean
	make -C examples clean
	$(RM) -r __pycache__

