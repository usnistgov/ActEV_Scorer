MAKE=make

install:
	@(echo "** Installing dependencies **\n")
	(sudo apt install -y python3 python3-dev python3-pip jq)
	(python3 -m pip install -r requirements.txt)
	@(echo "** Dependencies successfully installed**\n")

check:
	@(echo "** Running UnitTests **\n")
	(python3 -m unittest discover test)
	@(echo "** Running integration tests **\n")
	@(cd test; ./run_integration_tests.sh)

makecheckfiles:
	@(cd test; ./make_checkfiles.sh)
