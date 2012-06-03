test:
	@clear
	@nosetests -dvs

doc:
	./make-docs.sh -vg

.PHONY:	test doc
