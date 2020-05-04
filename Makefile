MAKE=make

check:
	@(echo "** Running UnitTests **\n")
	(python2 -m unittest discover test)
	@(echo "** Running integration tests **\n")
	@(cd test; ./run_integration_tests.sh)

makecheckfiles:
	@(cd test; ./make_checkfiles.sh)
