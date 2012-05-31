test:
	@clear
	@python `which nosetests` -dv

doc:
	./make-docs.sh -vg

.PHONY:	test doc
