test:
	@clear
	nosetests -dvs

test-x:
	@clear
	nosetests -dvsx

doc:
	@clear
	./make-docs.sh -vg

.PHONY:	test test-x doc
