MAKE=make

check:
	@(echo "** Running UnitTests **\n")
	(python2 -m unittest discover test)
