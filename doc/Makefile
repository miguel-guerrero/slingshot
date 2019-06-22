
all: use_relationships.png legend.png


%.png: %.dot
	dot -Tpng $< -o $@

%.svg: %.dot
	dot -Tsvg $< -o $@

clean:
	$(RM) *.png *.svg
